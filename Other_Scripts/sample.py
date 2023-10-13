import json

# Sample JSON data

with open('./Other_Scripts/Restaurant_data.json', 'r') as file:
    original_data = json.load(file)

# Create a new list to store dictionaries with "Business_ID" and "Cuisine" fields
new_data = []

# Iterate through the original data
for i, item in enumerate(original_data, start=1):
    new_item = {
        "Business_ID": item["Business_ID"],
        "Cuisine": item["Cuisine"]
    }
    new_data.append(new_item)

# Create a list of index dictionaries
index_data = [{"index": {"_index": "restaurant", "_id": str(i)}} for i in range(1, len(new_data) + 1)]
# final_data_list=[]


# for i in range(0,len(index_data)-1):
#     final_data_list.append(index_data[i])
#     final_data_list.append(new_data[i])

filename="Other_Scripts/rest_data.json"

for i in range(0,len(index_data)):
    with open(filename, "a") as file:
        json.dump(index_data[i], file, indent=4)
        file.write("\n")
        json.dump(new_data[i], file, indent=4)
        file.write("\n")



# Combine the index and data lists into a single list
# final_data = [dict(zip(["index", "data"], pair)) for pair in zip(index_data, new_data)]

# # Write the final data to a JSON file
# with open("output.json", "w") as outfile:
#     json.dump(final_data, outfile, indent=4)

# print("Output JSON file created.")
