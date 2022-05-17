from bson.json_util import dumps
from pymongo import MongoClient
import certifi

ca = certifi.where()

username = input("Enter the MongoDB username: ")  # Enter the MongoDB username.
password = input("Enter the MongoDB password: ")  # Enter the MongoDB password.
db_name = input("Enter the database name: ")  # Enter the database name.
collection_name = input("Enter the collection name: ")  # Enter the collection name.

client = MongoClient(f"mongodb+srv://{username}:{password}@l.ddi9w.mongodb.net/{db_name}?retryWrites"
                     f"=true&w=majority", tlsCAFile = ca)  # Enter the connection string.
db = client[f"{db_name}"]  # Connect to the database.
collection = db[f"{collection_name}"]  # Connect to the collection.
cursor = collection.find({})  # Get all the documents.

with open(f"{collection_name}.json", "w") as file:  # Open the file.
    file.write('[')  # Write the opening bracket.
    for document in cursor:  # Loop through the documents.
        file.write(dumps(document))  # Write the document.
        file.write(',')  # Write the comma.
    file.write(']')  # Write the closing bracket.
    print(f"Collection '{collection_name}' successfully exported.")  # Print the success message.
