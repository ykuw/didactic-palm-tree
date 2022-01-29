from pymongo import MongoClient
import datetime
import sys
import urllib

cluster = MongoClient("localhost", 27017)
db = cluster["g"]
collection = db["notes"]

buffer = []

while True:
    print("> ", end="")
    line = input()
    if line == ".":
        break
    if line == "`":
        sys.exit()
    buffer.append(line)
multiline_string = "\n".join(buffer)

collection.insert_one({"date": datetime.datetime.now(), "notes": f"{multiline_string}"})
