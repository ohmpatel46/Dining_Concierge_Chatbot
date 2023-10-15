import math
import dateutil.parser
import datetime
import time
import os
import logging
import json
import boto3
from botocore.exceptions import ClientError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']
    
def push_to_sqs(QueueURL, msg_body):
    """
    :param QueueName: String name of existing SQS queue
    :param msg_body: String message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """
    
    sqs = boto3.client('sqs')

    queue_url = QueueURL
    try:
        # Send message to SQS queue
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=0,
            MessageAttributes={
                'cuisine': {
                    'DataType': 'String',
                    'StringValue': msg_body['cuisine']
                },
                'location': {
                    'DataType': 'String',
                    'StringValue': msg_body['location']
                },
                'phNo': {
                    'DataType': 'Number',
                    'StringValue': msg_body['phNo']
                },
                'time': {
                    'DataType': 'String',
                    'StringValue': msg_body['time']
                },
                'num_people': {
                    'DataType': 'Number',
                    'StringValue': msg_body['num_people']
                },
                'email': {
                    'DataType': 'String',
                    'StringValue': msg_body['email']
                }
            },
            
            MessageBody=(
                'Information about the diner'
            )
        )
    
    except ClientError as e:
        logging.error(e) 
        return None
    
    return response
        

    
    
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }
    
def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def validate_parameters(_time_,cuisine_type, location, num_people, phone_number,email):
    
    location_types = ['manhattan', 'new york', 'ny', 'nyc']
    if not location:
        return build_validation_result(False, 'location', 'In which city would you like to dine?')
    
    elif location.lower() not in location_types:
        return build_validation_result(False, 'location', 'Unfortunately, we currently do not have a restaurant operating in that area. However, we would be delighted to assist you in finding a nearby location in Manhattan, New York.')
    
    
    cuisine_types = ['chinese', 'indian', 'middleeastern', 'italian', 'mexican']
    if not cuisine_type:
        return build_validation_result(False, 'cuisine', 'okay, in {}, What kind of cuisine would you like to enjoy?'.format(location))
        
    elif cuisine_type.lower() not in cuisine_types:
        return build_validation_result(False, 'cuisine', 'We do not have any restaurant that serves {}, would you like a different cuisine'.format(cuisine_type))
    
    
    if not _time_:
        return build_validation_result(False, 'time', 'What time would you prefer?')
    if not email:
        return build_validation_result(False, 'email', 'Could you please provide the email address where you would like to receive the recommendations?')

    
    
    if not num_people:
        return build_validation_result(False, 'num_people', 'How many guests, including yourself, should I make a reservation for?')
    
    if not phone_number:
        return build_validation_result(False, 'phNo', 'kindly share your contact number')
    
    elif len(phone_number)!=10:
        return build_validation_result(False, 'phNo', 'Please enter the correct phone_number'.format(phone_number))
    
    return build_validation_result(True, None, None)



def get_restaurants(intent_request):
    """
    Performs dialog management and fulfillment for asking details to get restaurant recommendations.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
    
    source = intent_request['invocationSource']
    
    if source == 'DialogCodeHook':
        slots = get_slots(intent_request)
        
        time_ = slots["time"]
        cuisine = slots["cuisine"]
        location = slots["location"]
        num_people = slots["num_people"]
        phone_number = slots["phNo"]
        email = slots["email"]
        
        slot_dict = {
            'time': time_,
            'cuisine': cuisine,
            'location': location,
            'num_people': num_people,
            'phNo': phone_number,
            'email':email
        }
        
        validation_result = validate_parameters(time_,cuisine, location, num_people, phone_number,email)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                              intent_request['currentIntent']['name'],
                              slots,
                              validation_result['violatedSlot'],
                              validation_result['message'])
                              
        if intent_request['currentIntent']['confirmationStatus'] == 'Denied':
            return {
                "dialogAction": {
                    "type": "Close",
                    "fulfillmentState": "Failed",
                    "message": {
                        "contentType": "PlainText",
                        "content": "Okay! Let me know if you need further assistance."
                    }
                }
            }
        elif intent_request['currentIntent']['confirmationStatus'] == 'None':
            # Ask for confirmation
            return {
                'dialogAction': {
                    'type': 'ConfirmIntent',
                    'intentName': intent_request['currentIntent']['name'],
                    'slots': slots,
                    'message': {
                        'contentType': 'PlainText',
                        'content': 'Could you please confirm your request to receive recommendations via email {} for a group of {} looking to dine at {} in a {} restaurant in the city of {} ?'.format(email,num_people,time_, cuisine, location)
                    }
                }
            }


    res = push_to_sqs('https://sqs.us-east-1.amazonaws.com/552744796033/Q1', slot_dict)
    
    
    if res:
        response = {
                    "dialogAction":
                        {
                         "fulfillmentState":"Fulfilled",
                         "type":"Close",
                         "message":
                            {
                                "contentType":"PlainText",
                                "content": " We have received your request for {} cuisine.You will recieve recommendations to your number {}. Have a great day with your group of {} to dine at {} in the city of {}!".format(
                                    cuisine,email, num_people, time_, location),
                            }
                        }
        }
    else:
        response = {
                    "dialogAction":
                        {
                         "fulfillmentState":"Fulfilled",
                         "type":"Close",
                         "message":
                            {
                              "contentType":"PlainText",
                              "content": "Sorry, come back after some time!",
                            }
                        }
                    }
                    
    # response = {
    #                 "dialogAction":
    #                     {
    #                      "fulfillmentState":"Fulfilled",
    #                      "type":"Close",
    #                      "message":
    #                         {
    #                           "contentType":"PlainText",
    #                           "content": " We have received your request for {} cuisine.You will recieve recommendations to your email {}. Have a great day with your group of {} to dine at {} in the city of {}!".format(
    #                               cuisine,phone_number, num_people, time_, location),
    #                         }
    #                     }
    #     }
    return response

def dispatch(event):
    logger.debug('dispatch userId={}, intentName={}'.format(event['userId'], event['currentIntent']['name']))
    intent_name = event['currentIntent']['name']
    if intent_name == 'diningsuggestion':
        return get_restaurants(event)
    raise Exception('Intent with name ' + intent_name + ' not supported')

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





