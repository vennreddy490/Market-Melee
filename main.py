from flask import Flask, request, redirect, url_for, render_template, session, flash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')



uri = os.environ.get('MONGO_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['sample_mflix']
# test_collection = db['test_users']
test_collection = db['test_users']

bcrypt = Bcrypt(app)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# user_data = {
#     'user': 'test_user_6',
#     'password': "abc123",
#     'collection_of_stocks': [],
#     'allocations': [],
#     'portfolio_value': 10000        
# }

# test_collection.insert_one(user_data)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_pswd = bcrypt.generate_password_hash(password).decode('utf-8')

        user_data = {
            'user': username,
            'password': hashed_pswd,
            'collection_of_stocks': [],
            'allocations': [],
            'portfolio_value': 10000
        }

        test_collection.insert_one(user_data)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = test_collection.find_one({'user': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else: 
            flash('Invalid username or password')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/dashboard")
def dashboard():
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