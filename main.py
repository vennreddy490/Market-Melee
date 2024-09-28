from flask import Flask, request, redirect, url_for, render_template, session, flash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Get secret key for sessions, Bcrypt for pswd hashing
app.secret_key = os.environ.get('SECRET_KEY')
bcrypt = Bcrypt(app)

# Form MongoDB connection
uri = os.environ.get('MONGO_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['sample_mflix']
test_collection = db['test_users']


# Test MongoDB connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# Base Route
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Registers new user, adds them to MongoDB users 
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

# Logs in users
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

# Provides a route to allow users to update their stock collection & allocations
# TODO: Add login required wrapper around this thing
@app.route('/update_portfolio', methods=['GET', 'POST'])
def update_portfolio():
    if request.method == 'POST':
        username = session['username']
        # Collect form data
        collection_of_stocks = request.form.getlist('stocks')
        allocations = request.form.getlist('allocations')
        portfolio_value = int(request.form['portfolio_value'])

        # Update the user data in MongoDB
        test_collection.update_one(
            {'user': username},
            {'$set': {
                'collection_of_stocks': collection_of_stocks,
                'allocations': [float(a) for a in allocations],
                'portfolio_value': portfolio_value
            }}
        )
        return redirect(url_for('dashboard'))
    return render_template('update_portfolio.html')


# Dashboard Route (To be implemented later)
@app.route("/dashboard")
def dashboard():
    username = session['username']
    # Fetch user data
    user = test_collection.find_one({'user': username})
    return render_template('dashboard.html', user=user)

# Tests Mongo_db connection, used for debugging
@app.route("/mongo_test")
def mongo_test():
    user_data = {
        'user': 'test_user_xxx',
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