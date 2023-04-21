import pymongo
import pandas as pd

client = pymongo.MongoClient("mongodb+srv://Reech:amazingDev!1@reechdb.ojmoq.mongodb.net/?retryWrites=true&w=majority") # Connect client to mongodb atlas server
db = client.ReechDatabase # access test database from client 
collection = db.fake_users # access users collection from test database

df = pd.DataFrame(list(collection.find()))


# Write fake data to local mongo 
cl = pymongo.MongoClient("mongodb://localhost:27017/")
db = cl.reechdatabase
collection = db.fake_users
df = df.iloc[:,1:]
db.collection.insert_many(df.to_dict('records'))
