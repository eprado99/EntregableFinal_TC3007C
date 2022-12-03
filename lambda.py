"""
 Emilio Prado A01570318
 Made use of starter template 'MakeAppointment' helper functions available on AWS.
"""

import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message,
            'responseCard': response_card
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message,
            'responseCard': response_card
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


def build_response_card(title, subtitle, options):
    """
    Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
    """
    buttons = None
    if options is not None:
        buttons = []
        for i in range(min(5, len(options))):
            buttons.append(options[i])

    return {
        'contentType': 'application/vnd.amazonaws.card.generic',
        'version': 1,
        'genericAttachments': [{
            'title': title,
            'subTitle': subtitle,
            'buttons': buttons
        }]
    }


""" --- Helper Functions --- """


def build_options(slot, appointment_type, date, booking_map):
    """
    Build a list of potential options for a given slot, to be used in responseCard generation.
    """

    if slot == 'Bebida':
        return [
            {'text': 'Refresco', 'value': 'Refresco'},
            {'text': 'Agua Natural', 'value': 'Agua Natural'},
            {'text': 'Agua de Jamaica', 'value': 'Agua de Jamaica'},
            {'text': 'Agua de Horchata', 'value': 'Agua de Horchata'}
        ]

    if slot == 'Torta':
        return [
            {'text': 'Pastor', 'value': 'Pastor'},
            {'text': 'Maciza', 'value': 'Maciza'},
            {'text': 'Suadero', 'value': 'Suadero'},
            {'text': 'Longaniza', 'value': 'Longaniza'},
            {'text': 'Pechuga', 'value': 'Pechuga'},
            {'text': 'Bistec', 'value': 'Bistec'},
            {'text': 'Chuleta', 'value': 'Chuleta'}
        ]

""" --- Functions that control the bot's behavior --- """
    
def calculate_cuenta(bebida, torta, postre, alambre):
    bebidaDict = {"Refresco": 23, "Agua Natural": 20, "Agua de Jamaica": 24, "Agua de Horchata": 24}
    tortaDict = {"Pastor": 50, "Maciza": 50, "Suadero": 50, "Longaniza": 50, "Pechuga": 50, "Bistec": 65, "Chuleta": 65}
    alambreDict = {"Vegetariano": 115, "Pechuga": 120, "Bistec": 120, "Chuleta": 120, "Costilla": 130, "Arrachera": 145}
    postreDict = {"Arroz Con Leche": 30, "Pastel Chocolate": 35, "Fresas Con Crema": 35, "Gelatina": 20, "Flan": 30}
    cuenta = 0
    cuenta += bebidaDict[bebida]
    cuenta += tortaDict[torta]
    cuenta += alambreDict[alambre]
    cuenta += postreDict[postre]
    return cuenta

def make_order(intent_request):
    bebidas = intent_request['currentIntent']['slots']['Bebidas']
    tortas = intent_request['currentIntent']['slots']['Tortas']
    alambres = intent_request['currentIntent']['slots']['Alambres']
    postres = intent_request['currentIntent']['slots']['Postres']
    
    # bebidasCant = intent_request['currentIntent']['slots']['BebidasCant']
    # tortasCant = intent_request['currentIntent']['slots']['TortasCant']
    # alambresCant = intent_request['currentIntent']['slots']['AlambresCant']
    # postresCant = intent_request['currentIntent']['slots']['PostresCant']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    
        
    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Okay, Su cuenta seria de {}'.format(calculate_cuenta(bebidas, tortas, postres, alambres))
        }
    )


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'MakeOrder':
        return make_order(intent_request)
        
    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
