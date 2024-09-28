from flask import Flask, request, redirect, url_for, render_template, session, flash, send_from_directory
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from portfolio_analysis.assess_portfolio import *

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

GRAPH_DIR = 'user_portfolio_graphs'


# Base Route
@app.route("/")
def hello_world():
    # If not logged in, route to welcome, else render dashboard 
    return redirect(url_for('welcome'))

@app.route("/welcome")
def welcome():
    return render_template('welcome.html')

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
        portfolio_value = int(request.form['portfolio_value'])
        
        # Collect form data
        collection_of_stocks = []
        allocations = []

        # Iterate over number of fields, since we don't know total amt 
        for i in range(1, 11):
            stock = request.form.get(f'stock_{i}')
            allocation = request.form.get(f'allocation_{i}')
            if stock and allocation:
                collection_of_stocks.append(stock)
                allocations.append(float(allocation))

        # Make sure that allocations sum up to 100%
        total_allocation = sum(allocations)
        if total_allocation != 100.0:
            return 'Allocations must sum up to 100%.'

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

@app.route("/backend_test")
def backend_test():
    dates = pd.date_range('2024-08-01', '2024-09-27')
    symbols = ['GOOG', 'AAPL', 'XOM']
    df_prices = get_data(symbols, dates)
    print("Data:")
    print(df_prices.head())

    allocs = [0.4, 0.3, 0.3]
    sv = 10000

    port_val = get_portfolio_returns(df_prices, allocs, sv)
    print(f"\nget_portfolio_returns() returns: \n{port_val.head(10)}")

    return "<p>This should have created a dataframe and printed it in the console.</p>"

@app.route("/user_data_test")
def user_data_test():
    username = session.get('username')
    user_data = test_collection.find_one({'user': username})

    print(f"The user is: {username}")

    allocs = user_data.get('allocations', [])
    sv = user_data.get('portfolio_value', 0)

    # print(f"symbols: {symbols}")
    # print(f"allocs: {allocs}")
    # print(f"sv: {sv}")

    dates = pd.date_range('2024-08-01', '2024-09-27')
    symbols = user_data.get('collection_of_stocks', [])
    df_prices = get_data(symbols, dates)
    print("Data:")
    print(df_prices.head())

    allocs = user_data.get('allocations', [])
    allocs = [alloc / 100 for alloc in allocs]
    sv = user_data.get('portfolio_value', 0)

    print(f"\nHere is the value getting passed in for allocs: {allocs}")
    print(f"\nHere is the value getting passed in for sv: {sv}")


    port_val = get_portfolio_returns(df_prices, allocs, sv)
    print(f"\nget_portfolio_returns() returns: \n{port_val.head(10)}")

    directory = 'user_portfolios'
    
    filename = f"{session['username']}_portfolio.csv"
    file_path = os.path.join(directory, filename)

    print(f"The type of port_val: {type(port_val)}")

    # port_val.to_csv(file_path, index=True)
    # port_val.to_csv(file_path, index=True)

    port_val_df = port_val.reset_index()
    port_val_df.columns = ['Date', 'Portfolio']
    port_val_df.to_csv(file_path, index=False)

    return "<p>This should have created a dataframe and printed it in the console.</p>"

@app.route("/visualization_test")
def visualization_test():
    username = session.get('username')
    print(f"The user is: {username}")
    print("Now, running plot user portfolio:")
    plot_user_portfolio(username)


    return "<p>This should have created a graph of the user's portfolio.</p>"

# @app.route('/display_portfolio/<username>')
# def display_portfolio(username):
@app.route('/display_portfolio')
def display_portfolio():
    username = session.get('username')
    # Construct the image filename based on the username
    image_filename = f"{username}_portfolio_graph.png"

    # Check if the image exists before serving
    image_path = os.path.join(GRAPH_DIR, image_filename)
    if os.path.exists(image_path):
        return render_template('display_image.html', username=username)
    else:
        return f"Image for {username} not found.", 404
    
@app.route('/portfolio_image')
def serve_image():
    username = session.get('username')
    # Construct the image filename
    image_filename = f"{username}_portfolio_graph.png"

    # Serve the image from the user portfolio directory
    return send_from_directory(GRAPH_DIR, image_filename)