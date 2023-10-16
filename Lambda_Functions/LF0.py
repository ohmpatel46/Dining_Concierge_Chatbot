import json
import boto3
import datetime
import logging
import uuid

def lambda_handler(event, context):
    
    client = boto3.client('lex-runtime')
    user_id = 'test'
    bot_name_lex = 'hotel_recomm'
    bot_alias =  'dining_bot'
    msg_text = event['messages'][0]['unstructured']['text']
    try:
        session = event['messages'][0]['unstructured']['id']
    except:
        session = CreateSessionId()
    response = client.post_text(
        botName=bot_name_lex ,botAlias= bot_alias,userId=user_id,sessionAttributes={'string': 'string','sessionId': session},requestAttributes={
            'string': 'string'},inputText= msg_text) 
    bot_response= {
        
        "messages": [
            {
                "type": "unstructured",
                "unstructured": {
                "id": '1',
                "text": response['message'],
                "timestamp": "",
                'sessionId': session
                    
                }
                
            }
            ]
        
    }
    return bot_response

def CreateSessionId():
    token = str(uuid.uuid4())
    label_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    session = f"{label_time}-{token}"
    return session   
    
    
    

