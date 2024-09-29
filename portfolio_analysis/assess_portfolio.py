import pandas as pd
import numpy as np
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import math
import os

matplotlib.use('Agg')  # Set non-interactive backend

def get_data(symbols, dates, path="data"):
    df_final = pd.DataFrame(index=dates)

    symbol = symbols[0]

    file_path = os.path.join(path, f"{symbol}.csv")

    df_temp = pd.read_csv(file_path,
                          index_col='Date',
                          parse_dates=True,
                          usecols=['Date', 'Adj Close'],
                          na_values='NaN')
    
    df_temp = df_temp.rename(columns={'Adj Close': symbol})

    df_final = df_final.join(df_temp, how="left")

    for symbol in symbols[1:]:
        file_path = os.path.join(path, f"{symbol}.csv")
        df_temp = pd.read_csv(file_path,
                              index_col='Date',
                              parse_dates=True,
                              usecols=['Date', 'Adj Close'],
                              na_values='NaN')
        df_temp = df_temp.rename(columns={'Adj Close': symbol})
        df_final = df_final.join(df_temp, how='left')
        df_final = df_final.dropna()

    return df_final

def get_portfolio_returns(prices, allocations, start_val=10000):
    
    
    stock_symbols = prices.columns.values
    portfolio_by_symbol = {symbol: None for symbol in stock_symbols}

    # Stores each df in the dict, instead of making a temp one for each, so I can join them all at once,
    # saving memory and increasing speed
    for i in range(0, len(prices.columns)):
        temp_df = prices[prices.columns[i]]
        portfolio_by_symbol[stock_symbols[i]] = ((temp_df/temp_df[0]) * allocations[i] * start_val).round(3)

    total_portfolio = pd.concat(portfolio_by_symbol.values(), axis=1)
    total_portfolio = total_portfolio.sum(axis=1)
    return total_portfolio

def plot_user_portfolio(username):
    # Set up titles and labels
    title = f"{username}'s Portfolio Performance Over Time"
    xlabel = "Date"
    ylabel = "Normalized Portfolio Value"
    
    # Define file paths
    directory = 'user_portfolios'
    filename = f"{username}_portfolio.csv"
    file_path = f"{directory}/{filename}"

    # Read the portfolio CSV file
    df = pd.read_csv(file_path)

    # Convert 'Date' column to datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # Normalize the portfolio values
    df['Portfolio_normalized'] = df['Portfolio'] / df['Portfolio'].iloc[0]

    # Set the plot style
    plt.style.use('seaborn-v0_8-poster')

    # Create a figure and axis object
    plt.figure(figsize=(12, 6))

    # Plot the normalized portfolio
    df['Portfolio_normalized'].plot(color='#1f77b4', linewidth=2, label='Portfolio')

    # Set title and labels with increased font sizes
    plt.title(title, fontsize=16)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)

    # Format the x-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.xticks(rotation=45)  # Rotate date labels for better fit

    # Customize the legend
    plt.legend(loc='upper left', fontsize=12)

    # Add gridlines
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Adjust layout
    plt.tight_layout()

    # Save the plot to a file
    image_directory = 'user_portfolio_graphs'
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)
    image_path = f"{image_directory}/{username}_portfolio_graph.png"
    plt.savefig(image_path)
    plt.close()

def plot_solo_stock(symbol):
    # Set up titles and labels
    title = f"{symbol}'s Historical Performance"
    xlabel = "Date"
    ylabel = "Stock Value"
    
    # Define file paths
    file_path = f'data/{symbol}.csv'

    # Read the stock CSV, only keeps the Date and Adj Close cols
    df = pd.read_csv(file_path, usecols=["Date", "Adj Close"])

    # Convert 'Date' column to datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # Plot the 'Adj Close' prices
    plt.figure(figsize=(10,6))
    df['Adj Close'].plot(title=title, xlabel=xlabel, ylabel=ylabel)
    plt.grid(True)

    # Save the plot to a file
    image_directory = 'stock_graphs'
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)
    image_path = f"{image_directory}/{symbol}_returns.png"
    plt.savefig(image_path)
    plt.close()
    print(f"Graphed and saved stock graph of {symbol}.")
