from pymongo import MongoClient
import datetime
import sys
import certifi

# Author: "ykuw"
# Email: "hurrays_coder_0r@icloud.com"
# Description:
# "This script is used to create documents within a MongoDB collection."
# "You have to provide the URL of MongoDB server, the name of the database, the name of the collection."
# "After you enter the text you want to insert, press 'Enter' and type '.' to break the loop and send the data."
# "If you want to cancel the operation, type 'Ctrl+C' or type '`'."

ca = certifi.where()

url = input("Enter the URL of the MongoDB database: ")  # Enter the URL of the MongoDB database.
username = input("Enter the MongoDB username: ")  # Enter the MongoDB username.
password = input("Enter the MongoDB password: ")  # Enter the MongoDB password.
db_name = input("Enter the database name: ")  # Enter the database name.
collection_name = input("Enter the collection name: ")  # Enter the collection name.

cluster = MongoClient(f"{url}", 27017, tlsCAFile = ca)  # Connect to the MongoDB database.
db = cluster[f"{db_name}"]  # Select the database.
collection = db[f"{collection_name}"]  # Select the collection.

buffer = []  # Create a buffer to store the documents.

while True:
    print("> ", end="")  # Prompt the user for input.
    line = input()  # Get the input.
    if line == ".":  # If the user enters ".", break the loop.
        break  # Break the loop.
    if line == "`":  # If the user enters "`", print the buffer.
        sys.exit()  # Exit the program.
    buffer.append(line)  # Append the input to the buffer.
multiline_string = "\n".join(buffer)  # Join the buffer into a string.

collection.insert_one(
    {
        "date": datetime.datetime.now(),
        "notes": f"{multiline_string}"
    }
)  # Insert the string into the collection.
