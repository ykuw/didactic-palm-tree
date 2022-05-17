from bson.json_util import dumps
from pymongo import MongoClient
import certifi

# Author: "ykuw"
# Email: "hurrays_coder_0r@icloud.com"
# Description:
# "This script is used to export data from MongoDB to JSON file."
# "Create in the main directory where this script is located a directory named 'collections'."
# "You have to provide the URL of MongoDB server, the name of the database, the name of the collection."
# "The script will create a JSON file in the 'collections' directory with the name of the collection."

ca = certifi.where()

url = input("Enter the URL of the MongoDB database: ")  # Enter the URL of the MongoDB database.
username = input("Enter the MongoDB username: ")  # Enter the MongoDB username.
password = input("Enter the MongoDB password: ")  # Enter the MongoDB password.
db_name = input("Enter the database name: ")  # Enter the database name.
collection_name = input("Enter the collection name: ")  # Enter the collection name.

client = MongoClient(f"mongodb+srv://{username}:{password}@{url}/{db_name}?retryWrites"
                     f"=true&w=majority", tlsCAFile = ca)  # Enter the connection string.
db = client[f"{db_name}"]  # Connect to the database.
collection = db[f"{collection_name}"]  # Connect to the collection.
cursor = collection.find({})  # Get all the documents.

with open(f"collections/{collection_name}.json", "w") as file:  # Open the file.
    file.write('[')  # Write the opening bracket.
    for document in cursor:  # Loop through the documents.
        file.write(dumps(document))  # Write the document.
        file.write(',')  # Write the comma.
    file.write(']')  # Write the closing bracket.
    print(f"Collection '{collection_name}' successfully exported.")  # Print the success message.
