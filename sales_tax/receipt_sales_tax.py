import re
import json
import pprint
import boto3
import os
import logging
from decimal import *
from line_has_number import line_has_number

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Baseline is getting the query parameters and passing them into the functions
def lambda_handler(event, context):
    # Makes sure that there are valid query parameters inside of the request
    if event['queryStringParameters']['filePath'] == None or len(event['queryStringParameters']['filePath']) == 0:
        retMsg += ', missing filePath parameter'
        if event['queryStringParameters']['userId'] == None or len(event['queryStringParameters']['userId']) == 0:
            retMsg += ', missing userId parameter'
            if event['queryStringParameters']['category'] == None or len(event['queryStringParameters']['category']) == 0:
                retMsg += ', missing category parameter'
        return {
            'statusCode': 400,
            'message': retMsg
        }

    bucket = os.environ['BUCKET']
    filePath = event['queryStringParameters']['filePath']
    user = event['queryStringParameters']['userId']
    category = event['queryStringParameters']['category']
    res = None

    res = dispatch(category, bucket, filePath, user)

    
    if res == None:
        return {
        'statusCode': 400,
        'message': 'Something went wrong with category matching'
        }

    return {
        'statusCode': 200,
        'body': json.dumps(res),
        'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Credentials": True
        }
    }

### Taxes paid ###

def sales_tax(bucket, filePath, user, category):
    res = readImage(bucket, filePath)
    storeName = []
    for r in res['TextDetections']:
        if r['Type'] == 'LINE':
            if line_has_number(r['DetectedText']):
               break
            storeName.append(r['DetectedText'])
    storeName = ' '.join(storeName)
    total = None
    tax = None
    totalFound = False
    taxFound = False
    # print(storeName)
    # print(res)
    for index, r in enumerate(res['TextDetections']):
        if totalFound and taxFound:
            break
        if r['Type'] == 'LINE':
            detectedText = r['DetectedText'].lower()
            if 'total' in detectedText and not ('subtotal' in detectedText) and not totalFound:
                total = detectedText
                if line_has_number(total):
                    total = re.sub('[^0-9.]', '', total)
                    total = total.split('.')
                    total = [total[0], total[1]]
                    total = '.'.join(total)
                    total = float(total)
                else:
                    total = numberNotFound(res['TextDetections'], index)
                totalFound = True
            if 'tax' in detectedText:
                tax = detectedText
                if line_has_number(tax):
                    tax = tax.split()
                    tax = tax[-1]
                    tax = float(re.sub('[^0-9.]', '', tax))
                else:
                    tax = numberNotFound(res['TextDetections'], index)
                taxFound = True
    if storeName == [] or storeName == None or len(storeName) == 0:
        storeName = ''
    if total == None:
        total = 0
    if tax == None:
        tax = 0
    resDict = {
        'storeName': storeName,
        'total': total,
        'taxAmount': tax,
        'category': category
    }
    res = {
        'userId': user,
        'filePath': filePath,
        'receiptInfo': resDict
    }
    return res

def income_tax(bucket, filePath, user, category):
    res = readImageFilter(bucket, filePath, 'w2')
    employerName = 'Google'
    federalAmount = 0.00
    for index, r in enumerate(res['TextDetections']):
        # logger.debug("[INCOME_TAX] detected text: {}".format(r['DetectedText']))
        if r['Type'] == 'LINE':
            detectedText = r['DetectedText'].lower()
            logger.debug("[INCOME_TAX] detected line: {}".format(detectedText))
            if 'wages' in detectedText:
                logger.debug("[INCOME_TAX] wages: {}".format(res['TextDetections'][index+1]['DetectedText']))
                logger.debug("[INCOME_TAX] federal tax: {}".format(res['TextDetections'][index+2]['DetectedText']))
                federalAmount = re.sub('[^0-9.]', '', res['TextDetections'][index+2]['DetectedText'])
                federalAmount = float(federalAmount)
                break
    resDict = {
        'employerName': employerName,
        'form': 'w2',
        'federalAmount': federalAmount,
        'category': category
    }
    res = {
        'userId': user,
        'filePath': filePath,
        'receiptInfo': resDict
    }
    return res

def property_tax():
    return None

def real_estate_tax():
    return None

### Medical expenses ###

def medical_tax():
    return None

### Charitable contributions ###

def charity():
    return None

### Interests ###

def mortgage_interest():
    return

def investment_interest():
    return None


### Helper functions ###

# Rekognition helper function
def readImage(bucket, filePath):
    rekognition = boto3.client('rekognition', os.environ['REGION'])
    return rekognition.detect_text(
        Image={
        'S3Object': {
            'Bucket': str(bucket),
            'Name': filePath
        }
    })

# Rekognition helper function with filter
def readImageFilter(bucket, filePath, filter):
    rekognition = boto3.client('rekognition', os.environ['REGION'])
    filters = {
        'RegionsOfInterest': [
            {
                'BoundingBox': {
                    'Width': 0 ,
                    'Height': 0,
                    'Left': 0,
                    'Top': 0
                }
            }]
        }
    if filter == 'w2':
        filters = {
        'RegionsOfInterest': [
            {
                'BoundingBox': {
                    'Width': 1,
                    'Height': 1,
                    'Left': .5,
                    'Top': 0
                }
            }]
        }
    return rekognition.detect_text(
        Image={
        'S3Object': {
            'Bucket': str(bucket),
            'Name': filePath
            },
        },
        Filters=filters)

# DEPRICATED, no reason for this lambda to update db in prod
def dynamoUpdate(res):
    dynamodb = boto3.resource('dynamodb')
    receiptTable = dynamodb.Table(os.environ['TABLE_RECEIPT'])
    userTable = dynamodb.Table(os.environ['TABLE_USER'])
    receiptTable.update_item(
        Key={
            'filePath': res['filePath']
        },
        UpdateExpression="SET userId=:userId, taxAmount=:tax, totalAmount=:totalAmount, category=:category",
        ExpressionAttributeValues={
                ':tax': Decimal(str(res['receiptInfo']['taxAmount'])),
                ':totalAmount': Decimal(str(res['receiptInfo']['total'])),
                ':userId': res['userId'],
                ':category': res['receiptInfo']['category']
        }
        )
    return

def dispatch(category, bucket, filePath, user):
    if category == 'sales_tax':
        res = sales_tax(bucket, filePath, user, category)
    elif category == 'medical_tax':
        res = medical_tax()
    elif category == 'income_tax':
        res = income_tax(bucket, filePath, user, category)
    elif category == 'property_tax':
        res = property_tax()
    elif category == 'real_estate_tax':
        res = real_estate_tax()
    elif category == 'charity':
        res = charity()
    elif category == 'investment_interest':
        res = investment_interest()
    elif category == 'mortgage_interest':
        res = mortgage_interest()
    else:
        res = None
    return res

# Helper function if number is not found on a line
# tax still doesn't work with bebeyokoono01.jpg :(
def numberNotFound(textDetections, index):
    prevValue = 0.00
    if index-1 >= 0:
        prevValue = textDetections[index-1]['DetectedText']
    nextValue = 0.00
    if index+1 < len(textDetections):
        nextValue = textDetections[index+1]['DetectedText']
    prevValue = re.sub('[^0-9.]', '', prevValue)
    prevValue = prevValue.split('.')
    if len(prevValue) >= 2:
        prevValue = [prevValue[0], prevValue[1]]
        prevValue = '.'.join(prevValue)
        prevValue = float(prevValue)
    nextValue = re.sub('[^0-9.]', '', nextValue)
    nextValue = nextValue.split('.')
    if len(nextValue) >= 2:
        nextValue = [nextValue[0], nextValue[1]]
        nextValue = '.'.join(nextValue)
        nextValue = float(nextValue)
    if type(prevValue) == float and type(nextValue) != float:
        return prevValue
    elif type(prevValue) != float and type(nextValue) == float:
        return nextValue
    elif type(prevValue) == float and type(nextValue) == float:
        if prevValue >= nextValue:
            return prevValue
        elif prevValue < nextValue:
            return nextValue
    else:
        return 0.00