from flask import Flask, request, redirect, url_for, render_template, session, flash, send_from_directory
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from portfolio_analysis.assess_portfolio import *
import pandas as pd

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
stock_metrics_collection = db['stock_metrics']

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


# Dashboard Route
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    username = session['username']
    # Fetch user data
    user = test_collection.find_one({'user': username})

    # Generate list of S&P 500 Stocks
    sp500_dataFrame = pd.read_csv('sp500_symbols.csv')
    sp500_symbols = sp500_dataFrame['Symbol'].tolist()
    valid_stock = False
    # Information for Stock Stats
    stock_image = None
    stock_stats = None

    # Handle form submission to generate stock stats
    stock_stats = None 
    if request.method == 'POST':
        stock_selected = request.form['symbol'].upper()
        print(stock_selected)
        if stock_selected in sp500_symbols:
            valid_stock = True

            # Retrieve Stock Data from MongoDB
            stock_data = stock_metrics_collection.find_one({'stock_name': stock_selected})

            if stock_data:
                stock_data.pop('id', None)
                stock_stats = stock_data

                # Get Graph Plot
                plot_solo_stock(stock_selected)
                image_path = f"{stock_selected}_returns.png"
                stock_image = f'stock_graphs/{image_path}'
            else:
                flash(f"Data for {stock_selected} not found in database.")
        else:
            flash(f"{stock_selected} is not in the S&P 500")
                

    return render_template('dashboard.html', user=user, sp500_symbols=sp500_symbols, stock_stats=stock_stats, valid_stock=valid_stock, stock_image=stock_image)

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

@app.route("/league")
def league():
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

    # Plot the user portfolio and save the image
    plot_user_portfolio(username)

    # Serve the image and display it to the frontend
    image_filename = f"user_portfolio_graphs/{username}_portfolio_graph.png"

    # Check if the image exists before serving
    image_static_path = 'static/' + image_filename
    if os.path.exists(image_static_path):
        return render_template('league.html', username=username, portfolio_image_path=image_filename)
    else:
        return f"Image for {username} not found.", 404
    
@app.route('/portfolio_image')
def serve_image():
    print("IF YOU SEE THIS DEBUG STATEMENT, /portfolio_image is being hit, when it should not be.")
    username = session.get('username')
    # Construct the image filename
    image_filename = f"{username}_portfolio_graph.png"

    # Serve the image from the user portfolio directory
    return send_from_directory(GRAPH_DIR, image_filename)

@app.route('/apple')
def apple():
    print("attempting to read and plot apple stock")
    plot_solo_stock('AAPL')
    return "<p>This should have graphed apple stock.</p>"
