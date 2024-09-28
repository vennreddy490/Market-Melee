import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import math
import os

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

def calculate_stock_stats():
    return 1