from bson.json_util import dumps
from pymongo import MongoClient
import certifi

ca = certifi.where()

db_name = input("Enter the database name: ")
collection_name = input("Enter the collection name: ")

client = MongoClient(f"mongodb+srv://user:pass@l.ddi9w.mongodb.net/{db_name}?retryWrites"
                     f"=true&w=majority", tlsCAFile=ca)
db = client[f"{db_name}"]
collection = db[f"{collection_name}"]
cursor = collection.find({})
with open(f"{collection_name}.json", "w") as file:
    file.write('[')
    for document in cursor:
        file.write(dumps(document))
        file.write(',')
    file.write(']')
    print(f"Collection '{collection_name}' successfully exported.")