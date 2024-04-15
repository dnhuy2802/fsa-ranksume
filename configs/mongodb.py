from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

# Get the MongoDB URI from the environment
uri_mongodb = os.getenv('MONGODB_URI')

# Create a new client and connect to the server
mongodb_client = MongoClient(uri_mongodb, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    mongodb_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("MongoDB Error: ", e)
