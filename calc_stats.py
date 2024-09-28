import pandas as pd
import numpy as np
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Get MongoDB connection URI from environment variables
uri = os.environ.get('MONGO_URI')

# Create a new client and connect to the server
client = MongoClient(uri)

# Select the database and collection
db = client['sample_mflix']  # Replace with your database name
metrics_collection = db['stock_metrics']  # New collection for stock metrics

def calculate_metrics(file_path):
    try:
        # Load the stock data from a CSV file
        stock_df = pd.read_csv(file_path)

        # Ensure the data is sorted by date
        stock_df['Date'] = pd.to_datetime(stock_df['Date'])
        stock_df = stock_df.sort_values('Date')

        # Calculate daily returns
        stock_df['Daily_Return'] = stock_df['Adj Close'].pct_change()

        # Calculate cumulative return
        price_recent = stock_df['Adj Close'].iloc[-1]
        price_old = stock_df['Adj Close'].iloc[0]
        cumulative_return = ((price_recent - price_old) / price_old)

        # Calculate volatility (standard deviation of daily returns)
        volatility = stock_df['Daily_Return'].std()

        # Calculate Sharpe ratio (assuming risk-free rate of 0 for simplicity)
        sharpe_ratio = stock_df['Daily_Return'].mean() / volatility if volatility != 0 else 0

        # Calculate Sortino ratio (focus on downside deviation)
        negative_returns = stock_df[stock_df['Daily_Return'] < 0]['Daily_Return']
        downside_volatility = negative_returns.std()
        sortino_ratio = stock_df['Daily_Return'].mean() / downside_volatility if downside_volatility != 0 else 0

        # Calculate average daily return
        avg_daily_return = stock_df['Daily_Return'].mean()

        # Return the calculated metrics
        return {
            'Cumulative Return': cumulative_return,
            'Average Daily Return': avg_daily_return,
            'Volatility (Standard Deviation)': volatility,
            'Sharpe Ratio': sharpe_ratio,
            'Sortino Ratio': sortino_ratio,
        }

    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The file {file_path} is empty.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    # Load the symbols file
    symbols_file_path = 'sp500_symbols.csv'  # Ensure this file exists
    sp500_symbols = pd.read_csv(symbols_file_path)

    # Directory where the stock data files are located
    data_directory = 'data/'

    # Iterate through each symbol in the sp500_symbols file
    for index, row in sp500_symbols.iterrows():
        symbol = row['Symbol']
        file_path = os.path.join(data_directory, f"{symbol}.csv")

        # Calculate metrics for each symbol's CSV file
        print(f"Calculating metrics for {symbol}...")

        metrics = calculate_metrics(file_path)

        if metrics:
            print(f"Metrics for {symbol}:")
            for key, value in metrics.items():
                print(f"  {key}: {value}")

            # Create a document to insert into MongoDB
            document = {
                'stock_name': symbol,
                'Cumulative Return': float(metrics['Cumulative Return']),
                'Average Daily Return': float(metrics['Average Daily Return']),
                'Volatility (Standard Deviation)': float(metrics['Volatility (Standard Deviation)']),
                'Sharpe Ratio': float(metrics['Sharpe Ratio']),
                'Sortino Ratio': float(metrics['Sortino Ratio']),
            }

            # Insert the document into MongoDB
            try:
                metrics_collection.insert_one(document)
                print(f"Metrics for {symbol} inserted into MongoDB.")
            except Exception as e:
                print(f"Error inserting metrics for {symbol} into MongoDB: {str(e)}")
        print("\n")
