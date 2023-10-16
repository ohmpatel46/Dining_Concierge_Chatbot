import uuid
import datetime
import logging
import boto3
import json
from botocore.exceptions import ClientError

import requests
import decimal
# from aws_requests_auth.aws_auth import AWSRequestsAuth
# from elasticsearch import Elasticsearch, RequestsHttpConnection
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

#Send email for SES
def send_email(sender_email, message):
    msg = MIMEMultipart()
    msg["Subject"] = "Restaurant recommedation for you!"
    msg["From"] = "jeevika99@gmail.com"
    msg["To"] = "jeevika99@gmail.com"

    # Set message body
    body = MIMEText(message)
    msg.attach(body)


    # Convert message to string and send
    ses_client = boto3.client("ses", region_name="us-east-1")
    print("t1")
    response = ses_client.send_raw_email(
        Source="jeevika99@gmail.com",
        Destinations=["jeevika99@gmail.com"],
        RawMessage={"Data": msg.as_string()}
    )
    #print(response)
    return response



logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(0,len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj
    
def get_sqs_data(queue_URL):
    sqs = boto3.client('sqs')
    queue_url = queue_URL
    
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[
                'time', 'cuisine', 'location', 'num_people', 'phNo'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        print(response)
        messages = response['Messages'] if 'Messages' in response.keys() else []

        for message in messages:
            receiptHandle = message['receiptHandle']
            sqs.delete_message(QueueUrl=queue_URL, ReceiptHandle=receiptHandle)
        return messages
    
    except ClientError as e:
        logging.error(e)
        return []
        
def es_search(host, query, cuisine):
    
    if cuisine.lower() == "indian" or cuisine.lower() =="pakistani":
        cuisine = "indpak"
    url = "https://search-restaurants-b5yo6l2255e3me6yyf4lyfr3m4.us-east-1.es.amazonaws.com/_search?q=Cuisine:"+cuisine
    esresponse = requests.get(url,auth=("Jeevika99","OpenSearch@123"),headers= {'content-type': 'application/json'})
    data = json.loads(esresponse.content.decode('utf-8'))
    return data
    # awsauth = AWSRequestsAuth(aws_access_key='AKIAYBMRIH6ARCHMBYF5',
    #                   aws_secret_access_key=' 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',
    #                   aws_host=host,
    #                   aws_region='us-east-1',
    #                   aws_service='es')
    
    # # use the requests connection_class and pass in our custom auth class
    # esClient = Elasticsearch(
    #     hosts=[{'host': host, 'port': 443}],
    #     use_ssl=True,
    #     http_auth=awsauth,
    #     verify_certs=True,
    #     connection_class=RequestsHttpConnection)
    
    # es_result=esClient.search(index="restaurants", body=query)    # response=es.get()
    # return es_result
    

    
def get_dynamo_data(dynno, table, key):
    response = table.get_item(Key={'Business_ID':key}, TableName='yelp-restaurants')
    
    response = replace_decimals(response)
    print(response)
    name = response['Item']['Name']
    address_list = response['Item']['Address']
    return '{}, {}'.format(name, address_list)

def lambda_handler(event, context):
    
    # Create SQS client
    sqs = boto3.client('sqs')

    es_host = 'search-restaurants-b5yo6l2255e3me6yyf4lyfr3m4.us-east-1.es.amazonaws.com/'
    table_name = 'yelp-restaurants'
    
    #messages = get_sqs_data('https://sqs.us-east-1.amazonaws.com/552744796033/Q1')
    messages = event['Records']
    
    logging.info(messages)
        
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    print(messages)
    

    for message in messages:
        logging.info(message)
        msg_attributes=message['messageAttributes']
        query = {"query": {"match": {"cuisine": msg_attributes["cuisine"]["stringValue"]}}}
        es_search_result = es_search(es_host, query, msg_attributes["cuisine"]["stringValue"])
        number_of_records_found = int(es_search_result["hits"]["total"]["value"])
        hits = es_search_result['hits']['hits']
        print("es")
        print(hits)
        suggested_restaurants = []
        for hit in hits:
            id = hit['_source']['Business_ID']
            suggested_restaurant = get_dynamo_data(dynamodb, table, id)
            print("restaurant")
            print(suggested_restaurant)
            suggested_restaurants.append(suggested_restaurant)

        text = "Hello! Here are the "+msg_attributes['cuisine']['stringValue']+ " suggestions for "+msg_attributes['num_people']['stringValue']+" people at "+ msg_attributes['time']['stringValue']+"\n"
        for i,rest in enumerate(suggested_restaurants):
	        text += "\n(" + str(i+1) + ")" + rest 
        

        phone_number = msg_attributes['phNo']
        # sns_client = boto3.client('sns' , 'us-east-1')
        
        # response = sns_client.publish(
        #     TopicArn="arn:aws:sqs:us-east-1:552744796033:Q1",
        #     Message=text
        # )
        if len(suggested_restaurants) > 0:
            send_email("jeevika99@gmail.com",text)
            sqs_cli = boto3.client('sqs')
            sqs_cli.delete_message(QueueUrl="https://sqs.us-east-1.amazonaws.com/552744796033/Q1",ReceiptHandle=message['receiptHandle'])