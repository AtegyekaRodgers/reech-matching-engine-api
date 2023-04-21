from fake_data_set import ReechFakeData
import pymongo
import math

client = pymongo.MongoClient("mongodb+srv://Reech:amazingDev!1@reechdb.ojmoq.mongodb.net/?retryWrites=true&w=majority") # Connect client to mongodb atlas server
db = client.ReechDatabase # access test database from client 
collection = db.fake_users # access users collection from test database

instance = ReechFakeData()
data = instance()
# result = collection.insert_many(data) # Try not to run this by accident

# result = collection.create_index([('userId', pymongo.ASCENDING)],unique=True)


collection.update_many({"radius": {"$exists": False}}, {"$set": {"radius": 500}})
import datetime
time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

collection.update_many({"time": {"$exists": False}}, {"$set": {"time": time}})

collection.update_many({"N_views": {"$exists": False}}, {"$set": {"N_views": 0}})
