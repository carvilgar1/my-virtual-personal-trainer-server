from bson.json_util import dumps
from pymongo import MongoClient
from flask import Flask

app = Flask(__name__)
uri = "mongodb://root:root@db:27017/?authSource=sample_db&authMechanism=SCRAM-SHA-256"
client = MongoClient(uri)

db = client.get_database('sample_db')
collection = db.get_collection('sample_collection')

class test():
    def __init__(self, _id, org, filter, addrs):
        self.id = _id
        self.org = org
        self.filter = filter
        self.addrs = addrs

def get_hit_count():
    return dumps({"tests": list(collection.find( {} ))})

@app.route('/')
def hello():
    return get_hit_count()