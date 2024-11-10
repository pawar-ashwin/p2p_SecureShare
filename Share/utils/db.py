from pymongo import MongoClient

def get_mongo_client():
    mongo_uri = "mongodb+srv://sowmyamutya20:hyB1Mq5ODLBssNDl@logincredentials.oalqb.mongodb.net/?retryWrites=true&w=majority&appName=loginCredentials"
    client = MongoClient(mongo_uri, ssl=True)
    return client

def get_collection(database_name, collection_name):
    client = get_mongo_client()
    db = client[database_name]
    return db[collection_name]
