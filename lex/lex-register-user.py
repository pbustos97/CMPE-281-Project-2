import json
import boto3
import time
import logging
import os
import uuid
import re
from decimal import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

### Handler ###
def lambda_handler(event, context):
    logger.debug('[EVENT] event: {}'.format(type(event)))
    logger.debug('[CONTEXT] identity: {}'.format(context.identity))
    logger.debug('[CONTEXT] identityId: {}'.format(context.identity.cognito_identity_id))
    logger.debug('[CONTEXT] identityPoolId: {}'.format(context.identity.cognito_identity_pool_id))
    logger.debug('event={}'.format(event))
    os.environ['TZ'] = 'America/Los_Angeles'
    time.tzset()
    
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    return dispatch(event)


def RegisterUser(intent_request):
    logger.debug('RegisterUser')
    name = {}
    first_name = get_slots(intent_request)['first_name']
    last_name = get_slots(intent_request)['last_name']
    name['first_name'] = first_name
    name['last_name'] = last_name
    agi = get_slots(intent_request)['agi']
    filing_status = get_slots(intent_request)['filing_status']
    filers = {}
    filers_blind = get_slots(intent_request)['filers_blind']
    filers_sixtyfive = get_slots(intent_request)['filers_sixtyfive']
    filers['filers_blind'] = filers_blind
    filers['filers_sixtyfive'] = filers_sixtyfive
    properties = get_slots(intent_request)['properties']
    source = intent_request['invocationSource']
    
    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)
        
        validation_result = validate_data(name, agi, filing_status, filers, properties)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent['sessionAttributes'],
                              intent_request['currentIntent']['name'],
                              slots,
                              validation_result['violatedSlot'],
                              validation_result['message'])
        
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        
        return delegate(output_session_attributes, get_slots(intent_request))
    
    logger.debug('[SESSION] {}'.format(type(intent_request['sessionAttributes'])))
    intent_request['sessionAttributes']['lexRegisterId'] = str(uuid.uuid4())
    #UpdateTable(intent_request['userId'], name, agi, filing_status, filers, properties)
    message = {
        'contentType': 'PlainText',
        'content': 'Thank you for registering with us {} {}'.format(name['first_name'].capitalize(), name['last_name'].capitalize())
    }
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                  message)

# Makes sure that all the fields during the lex registration process are valid
def validate_data(name:dict, agi, filing_status, filers:dict, properties):
    logger.debug('validate_data')
    if name['first_name'] is not None:
        logger.debug('first_name: {}'.format(name['first_name']))
        for i in str(name['first_name']):
            if i.isdigit():
                return build_validation_result(False, 'first_name', 'First names do not contain numbers')
    if name['last_name'] is not None:
        logger.debug('last_name: {}'.format(name['last_name']))
        for i in str(name['last_name']):
            if i.isdigit():
                return build_validation_result(False, 'last_name', 'Last names do not contain numbers')
    if agi is not None:
        logger.debug('agi: {}'.format(agi))
        agi = re.sub('[^0-9.]', '', str(agi))
        count = 0
        for i in agi:
            if i == ".":
                count += 1
            if count >= 2:
                return build_validation_result(False, 'agi', 'AGI has too many "."')
        if float(agi) < 0:
            return build_validation_result(False, 'agi', 'AGI cannot be negative')
        
    filing_types = ['single', 
                      'married filing jointly',
                      'married filing separately',
                      'head of household',
                      'qualifying widow(er) with dependent child']
    if filing_status is not None:
        logger.debug('filing_status: {}'.format(filing_status))
        if str(filing_status).lower() not in filing_types:
            return build_validation_result(False, 'filing_status', 'Unable to verify filing status')
    if filers['filers_blind'] is not None:
        logger.debug('filers_blind: {}'.format(filers['filers_blind']))
        if int(filers['filers_blind']) < 0:
            return build_validation_result(False, 'filers_blind', 'There cannot be negative blind filers')
    if filers['filers_sixtyfive'] is not None:
        logger.debug('filers_sixtyfive: {}'.format(filers['filers_sixtyfive']))
        if int(filers['filers_sixtyfive']) < 0:
            return build_validation_result(False, 'filers_sixtyfive', 'There cannot be negative filers over the age of 65')
    if properties is not None:
        logger.debug('properties: {}'.format(properties))
        if int(properties) < 0:
            return build_validation_result(False, 'properties', 'Nobody can own negative properties')
    logger.debug('validate_data: success')
    return build_validation_result(True, None, None)

### Helper functions ###
    
def dispatch(intent_request):
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'RegisterUser':
        return RegisterUser(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

# DEPRECIATED, frontend calls signup
def UpdateTable(userId, name:dict, agi, filing_status, filers:dict, properties):
    logger.debug('UpdateTable method | userId: {} | name: {} | agi: {} | filing_status: {} | filers: {} | properties: {}'.format(userId, name, agi, filing_status, filers, properties))
    dynamodb = boto3.resource('dynamodb')
    userTable = dynamodb.Table(os.environ['TABLE_USERS'])
    userTable.put_item(
        Item={
            'userId': userId,
            'first_name': name['first_name'].capitalize(),
            'last_name': name['last_name'].capitalize(),
            'agi': Decimal(agi),
            'filing_status': filing_status,
            'filers_blind': filers['filers_blind'],
            'filers_sixtyfive': filers['filers_sixtyfive'],
            'properties': properties
        })

# Returns the currentIntent slots from an event
def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

### Response Helper Functions ###
        
def build_validation_result(is_valid, violated_slot, message_content):
    logger.debug('build_validation_result | is_valid: {} | violated_slot: {} | message_content: {}'.format(is_valid, violated_slot, message_content))
    if message_content is None:
        return {
            'isValid': is_valid,
            'violatedSlot': violated_slot,
        }
    
    return {
        'isValid': is_valid,
        'violatedSlot': violatedSlot,
        'message': {'contentType': 'Plaintext', 'content': message_content}
    }

# Returns the slot that is next in the Lex intent
def elicit_slot(session_attributes, intent_name, slots, slots_to_elicit, message):
    logger.debug('elicit_slot method | session_attributes: {} | intent_name: {} | slots: {} | slots_to_elicit: {} | message: {}'.format(session_attributes, intent_name, slots, slots_to_elicit, message))
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slots_to_elicit,
            'message': message
        }
    }
    
def delegate(session_attributes, slots):
    logger.debug('delegate method | session_attributes: {} | slots: {}'.format(session_attributes, slots))
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }

# Final message when the intent flow is finished
def close(session_attributes, fulfillment_state, message):
    logger.debug('close method | session_attributes: {} | fulfillmentState: {} | message: {}'.format(session_attributes, fulfillment_state, message))
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    logger.debug('response={}'.format(response))
    return response
    