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
    image_directory = 'static/user_portfolio_graphs'
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)
    image_path = f"{image_directory}/{username}_portfolio_graph.png"
    plt.savefig(image_path)
    plt.close()
    print(f"{username} Portfolio Graph saved in: {image_path}")

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
    image_directory = 'static/stock_graphs'
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)
    image_path = f"{image_directory}/{symbol}_returns.png"
    plt.savefig(image_path)
    plt.close()
    print(f"Graphed and saved stock graph of {symbol}.")

def find_historical_leaders(username):
    # Directory containing the user portfolios
    directory = 'user_portfolios'

    portfolio_returns = []

    # Loop through each CSV file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            user = filename.replace('_portfolio.csv', '')

            # Skip the portfolio of the current session user
            if user == username:
                continue

            # Load the CSV file into a DataFrame
            df = pd.read_csv(os.path.join(directory, filename), usecols=["Date", "Portfolio"])

            # Convert 'Date' column to datetime and set as index
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)

            # Calculate the normalized return as (last value / first value)
            first_value = df['Portfolio'].iloc[0]
            last_value = df['Portfolio'].iloc[-1]
            normalized_return = last_value / first_value
            print(f"The normalized return of {user} is {normalized_return}")


            # Store the user and their portfolio difference
            portfolio_returns.append({'user': user, 'normalized_return': normalized_return})
    
    print(f"at the end, portfolio_returns looks like: {portfolio_returns}")

    # Convert the list to a DataFrame for easier sorting
    portfolio_returns_df = pd.DataFrame(portfolio_returns)
    top_three_portfolios = portfolio_returns_df.sort_values(by='normalized_return', ascending=False).head(3)

    # Convert df to a dict for passage into plotting method:
    top_three_portfolios = top_three_portfolios.to_dict(orient='records')

    print(f"The type of top_three_portfolios is: {type(top_three_portfolios)}")
    print(top_three_portfolios)
    print("\n\n\n\n")
    return top_three_portfolios

def plot_user_vs_top_three_historical(username, top_three):
    directory = 'user_portfolios'

    print(f"Username: {username} ")

    # Load current user's portfolio
    user_file = f'{directory}/{username}_portfolio.csv'

    print(f"user_file: {user_file}")

    user_df = pd.read_csv(user_file, usecols=["Date", "Portfolio"])
    user_df['Date'] = pd.to_datetime(user_df['Date'])
    user_df.set_index('Date', inplace=True)

    # Plot current user's portfolio
    plt.figure(figsize=(10, 6))
    plt.plot(user_df.index, user_df['Portfolio'], label=username, linewidth=2)

    # Load and plot the top three portfolios (assuming top_three is a list of dictionaries)
    for entry in top_three:
        # Access top_user from the list entry
        top_user = entry['user']
        print(f"type of top_user: {type(top_user)}")
        print(f"top_user: {top_user}")
        
        # Construct the file name directly using an f-string
        top_user_file = f'{directory}/{top_user}_portfolio.csv'
        print(f"top_user_file: {top_user_file}")
        
        # Load the top user's portfolio data
        top_user_df = pd.read_csv(top_user_file, usecols=["Date", "Portfolio"])
        top_user_df['Date'] = pd.to_datetime(top_user_df['Date'])
        top_user_df.set_index('Date', inplace=True)

        # Plot the portfolio of the top user
        plt.plot(top_user_df.index, top_user_df['Portfolio'], label=top_user, linestyle='--')


    # Adding titles and labels
    plt.title('Comparison of User Portfolio vs. Top Three (Based on Normalized Returns)')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.legend(loc='best')

    # Show the plot
    # Save the plot to a file
    image_directory = 'static/temp_graphs'
    if not os.path.exists(image_directory):
        os.makedirs(image_directory)
    image_path = f"{image_directory}/{username}_vs_leaders.png"
    plt.savefig(image_path)
    plt.close()
    print(f"Graphed and saved stock graph of {username} vs top three leaders.")