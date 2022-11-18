from pymongo import MongoClient

uri = "mongodb://root:root@db:27017/?authSource=my_virtual_personal_trainer&authMechanism=SCRAM-SHA-256"

def connect_bd():
    client = MongoClient(uri)
    return client

def disconnect_bd(connection):
    connection.close()