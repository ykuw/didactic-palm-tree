import json
import csv
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client["twitter_db_stream_1"]
collection = db["twitter_collection"]
data_python = collection.find(
    {"user.location": {"$exists": True}, "user.location": {"$ne": "null"}},
    {
        "created_at": 1,
        "text": 1,
        "user.name": 1,
        "user.location": 1,
        "geo.coordinates": 1,
        "sentiment_value": 1,
        "confidence_value": 1,
    },
)

field_names = [
    "created_at",
    "text",
    "user.name",
    "user.location",
    "sentiment_value",
    "confidential_value",
]

with open("Sentiment_Analisys.csv", "w", newline="") as f_output:
    csv_output = csv.writer(f_output)
    csv_output.writerow(field_names)

    for data in data_python:
        csv_output.writerow(
            [
                data["created_at"],
                data["text"].encode("utf8", "ignore"),
                data["user"]["name"].encode("utf8"),
                data["user"]["location"],
                data["sentiment_value"],
                data["confidence_value"],
            ]
        )
