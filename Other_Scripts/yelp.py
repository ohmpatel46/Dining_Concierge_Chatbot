import requests
import json
from datetime import datetime

# Replace with your Yelp API key
api_key = '44Sk0dJgURYottbMKIsd-zdPg9y3uXnWYmxdX0Uji8Dr6WfoEPl8ENVJb6RE2tykPgBp2T9XT6y6MnF3tBI7uTfW9r6qyPni87GzJn-qMnzUISWw2X7n5Pnl08glZXYx'

# Set your desired cuisine type and location
cuisine_type = 'Indian'
location = 'Manhattan'

# Set the API endpoint
url = 'https://api.yelp.com/v3/businesses/search'

# Define the query parameters
params = {
    'categories': cuisine_type,
    'location': location,
    'limit': 1000
}

# Set the HTTP headers with your API key
headers = {
    'Authorization': f'Bearer {"44Sk0dJgURYottbMKIsd-zdPg9y3uXnWYmxdX0Uji8Dr6WfoEPl8ENVJb6RE2tykPgBp2T9XT6y6MnF3tBI7uTfW9r6qyPni87GzJn-qMnzUISWw2X7n5Pnl08glZXYx"}',
}

# Make the API request
response = requests.get(url, params=params, headers=headers)


if response.status_code == 200:
    data = json.loads(response.text)

    # Create a list to store the extracted restaurant data
    restaurant_data = []
    
    for business in data.get('businesses', []):
        # Extract relevant information from the Yelp response
        # print(business)
        timestamp = datetime.now().isoformat()
        restaurant_info = {
            'insertedAtTimestamp':timestamp,
            'Business_ID': business.get('id'),
            'Name': business.get('name'),
            'Address': ', '.join(business.get('location', {}).get('display_address', [])),
            'Latitude': business.get('coordinates')['latitude'],
            'Longitude': business.get('coordinates')['longitude'],
            'No_of_reviews': business.get('review_count'),
            'Rating': business.get('rating'),
            'Phone': business.get('phone'),
            'Zip_code': business.get('location')['zip_code']
            
        }

        # Add this restaurant's info to the list
        restaurant_data.append(restaurant_info)
    # Convert the list to JSON format
    json_data = json.dumps(restaurant_data, indent=4)

    # Print the JSON data (you can save it to a file or send it to DynamoDB)
    print(json_data)
    file_path = './Indian_data.json'

# Write the JSON data to the file
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print(f'JSON data saved to: {file_path}')

else:
    print('Error:', response.status_code)
    print('Response:', response.text)
