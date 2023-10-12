import requests
import json
from datetime import datetime
import time

# Replace with your Yelp API key
api_key = '44Sk0dJgURYottbMKIsd-zdPg9y3uXnWYmxdX0Uji8Dr6WfoEPl8ENVJb6RE2tykPgBp2T9XT6y6MnF3tBI7uTfW9r6qyPni87GzJn-qMnzUISWw2X7n5Pnl08glZXYx'

# Set your desired cuisine type and location
cuisine_types = ['indpak','Chinese','Mexican','Italian']
location = 'Manhattan'

# Set the API endpoint
url = 'https://api.yelp.com/v3/businesses/search'

# Set the HTTP headers with your API key
headers = {
    'Authorization': f'Bearer {"44Sk0dJgURYottbMKIsd-zdPg9y3uXnWYmxdX0Uji8Dr6WfoEPl8ENVJb6RE2tykPgBp2T9XT6y6MnF3tBI7uTfW9r6qyPni87GzJn-qMnzUISWw2X7n5Pnl08glZXYx"}',
}
responses=[]
json_data=[]
unique_restaurant_ids = set()
restaurant_data = []
# Make the API request

for i in range(0,4):
    print("\n",cuisine_types[i])
    offset=0
    while len(unique_restaurant_ids) < 50*(i+1):
        print("\nLength of set:",len(unique_restaurant_ids))
        params = {
            'categories': cuisine_types[i],
            'location': location,
            'limit': 50,
            'offset': offset
        }   
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)

            # Create a list to store the extracted restaurant data
            
            
            for business in data.get('businesses', []):
                # Extract relevant information from the Yelp response
                # print(business)
                restaurant_id = business.get('id')
                print("\n in ",cuisine_types[i])
                if(len(unique_restaurant_ids) == 50*(i+1)):
                    break
                if restaurant_id not in unique_restaurant_ids:
                    # Extract relevant information from the Yelp response
                    timestamp = datetime.now().isoformat()
                    restaurant_info = {
                        'insertedAtTimestamp': timestamp,
                        'Business_ID': restaurant_id,
                        'Name': business.get('name'),
                        'Address': ', '.join(business.get('location', {}).get('display_address', [])),
                        'Latitude': business.get('coordinates')['latitude'],
                        'Longitude': business.get('coordinates')['longitude'],
                        'No_of_reviews': business.get('review_count'),
                        'Rating': business.get('rating'),
                        'Phone': business.get('phone'),
                        'Zip_code': business.get('location')['zip_code'],
                        'Cuisine': cuisine_types[i]
                    }
                    # Add this restaurant's info to the list
                    restaurant_data.append(restaurant_info)
                    unique_restaurant_ids.add(restaurant_id)
            # Convert the list to JSON format
        else:
            print('Error:', response.status_code)
            print('Response:', response.text)
        # Print the JSON data (you can save it to a file or send it to DynamoDB)
        offset+=50
file_path = 'Other_Scripts\Restaurant_data.json'
with open(file_path, 'w') as json_file:
    json.dump(restaurant_data, json_file, indent=4)

print(f'JSON data saved to: {file_path}')


