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