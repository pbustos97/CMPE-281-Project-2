import re
import json
import pprint
import boto3
from line_has_number import line_has_number

def lambda_handler(event, context):
    
    bucket = event['queryStringParameters']['bucket']
    file = event['queryStringParameters']['file']
    user = event['queryStringParameters']['userId']
    filePath = str(user) + '/' + str(file)
    
    rekognition = boto3.client('rekognition', 'us-west-2')
    res = rekognition.detect_text(
        Image={
        'S3Object': {
            'Bucket': str(bucket),
            'Name': filePath
        }
    })
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
    print(storeName)
    #print(res)
    for index, r in enumerate(res['TextDetections']):
        if totalFound and taxFound:
            break
        if r['Type'] == 'LINE':
            detectedText = r['DetectedText'].lower()
            if 'total' in detectedText and not ('subtotal' in detectedText) and not totalFound:
                total = detectedText
                if line_has_number(total):
                    total = float(re.sub('[^0-9.]', '', total))
                else:
                    prevValue = res['TextDetections'][index-1]['DetectedText']
                    nextValue = 0.00
                    if index+1 < len(res['TextDetections']):
                        nextValue = res['TextDetections'][index+1]['DetectedText']
                    prevValue = float(re.sub('[^0-9.]', '', prevValue))
                    nextValue = float(re.sub('[^0-9.]', '', nextValue))
                    if prevValue >= nextValue:
                        total = prevValue
                    elif prevValue < nextValue:
                        total = nextValue
                totalFound = True
            if 'tax' in detectedText:
                tax = detectedText
                if line_has_number(tax):
                    tax = tax.split()
                    tax = tax[-1]
                    tax = float(re.sub('[^0-9.]', '', tax))
                    taxFound = True
                print(tax)
                print(type(tax))
                print(tax)
                
    
    if storeName == [] or storeName == None or len(storeName) == 0:
        storeName = ''
    if total == None:
        total = ''
    if tax == None:
        tax = ''
    res = {
        'storeName': storeName,
        'total': total,
        'taxAmount': tax
    }
    return {
        'statusCode': 200,
        'body': json.dumps(res)
    }
