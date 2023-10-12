import boto3
import json
import time
from decimal import Decimal
# Initialize the DynamoDB resource and specify your region
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Replace 'YourTable' with your DynamoDB table name
table_name = 'yelp-restaurants'
table = dynamodb.Table(table_name)

file_path = 'Other_Scripts\Restaurant_data.json'  # Replace with your file path

with open(file_path, 'r') as json_file:
    data = json.load(json_file, parse_float=Decimal)  # Parse float as Decimal

for item in data:
        table.put_item(Item=item)
        time.sleep(0.25)

print(f'Data uploaded to DynamoDB table: {table_name}')