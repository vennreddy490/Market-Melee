from flask import Flask
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

uri = os.environ.get('MONGO_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['sample_mflix']
# test_collection = db['test_users']
test_collection = db['movies']

user_data = {
    'user': 'test_user_1',
    'password': "abc123",
    'collection_of_stocks': [],
    'allocations': [],
    'portfolio_value': 10000        
}

query = { "name": "Mercedes Tyler" }
document = test_collection.find_one(query)

if document:
    print("Document found:")
    print(document)
else:
    print("No document matches the query.")


test_collection.insert_one(user_data)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/mongo_test")
def mongo_test():
    user_data = {
        'user': 'test_user_1',
        'password': "abc123",
        'collection_of_stocks': [],
        'allocations': [],
        'portfolio_value': 10000        
    }

    test_collection.insert_one(user_data)

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    return "<p>This should have added a user.</p>"