""" 
Loads the result of the sentiment analysis from the PostgreSQL database and plots the results inside the terminal.
"""
import pandas as pd
import sqlalchemy as sqla
import time
import plotext as plt
import requests
import os
from datetime import date, timedelta
import logging

API_KEY = os.getenv('ALPHAVANTAGE_API_KEY') # API key stored in environmental variable, else pass it here

time.sleep(10)  # seconds, pause to make sure plot container runs after ETL

def extract():
    """Extracts a table from a postgreSQL DB as a pandas Frame"""

    # Connect to PostgreSQL - using standards name + pw
    pg = sqla.create_engine('postgresql://postgres:postgres@postgres:5432/stock_news', echo=False)

    # Get popular tock table data
    popular_stocks = pd.read_sql_table(table_name='stock_popularity', con=pg)
    popular_stocks.reset_index(drop=True, inplace=True)

    return popular_stocks

def get_short_term_intraday(symbol, base_url='https://www.alphavantage.co/query?'):
    # short term intraday data (1-2 months)
    params = {'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': '1min',
            'datatype': 'json',
            'outputsize': 'full',
            'apikey': API_KEY}
    try:
        response = requests.get(base_url, params=params)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    response_dict = response.json()
    _, header = response.json()

    return header, response_dict

def plot_candlestick(best_stock_symbol, stock):
    """Plots the candlestick chart for a given symbol, inside the terminal.
    Limit time window to current 2 days."""

    plt.date_form('Y-m-d H:M:S')

    close_list = [float(stock[key]['4. close']) for key in stock.keys()]
    open_list = [float(stock[key]['1. open']) for key in stock.keys()]
    high_list = [float(stock[key]['2. high']) for key in stock.keys()]
    low_list = [float(stock[key]['3. low']) for key in stock.keys()]

    # fix data types and limit data to Today
    data_dict = {'Open': open_list, 'Close': close_list, 'High': high_list, 'Low': low_list}
    date_list = list(stock.keys())
    date_list_dt = [plt.string_to_datetime(date) for date in date_list]

    df = pd.DataFrame(data_dict, index= date_list_dt)
    df.index.name='Date'

    today = date.today() - timedelta(days=1)
    df = df[df.index.date>=today]
    date_list = df.index.strftime('%Y-%m-%d %H:%M:%S')

    plt.candlestick(date_list, df)

    plt.title(best_stock_symbol + " Stock Price - Short-Term")
    plt.xlabel("Date")
    plt.ylabel("Stock Price in $")
    plt.limit_size(True, True)
    plt.plotsize(plt.terminal_width(), plt.terminal_height())
    plt.show()

def plot_line(best_stock_symbol, stock):
    """Plots the lineplot for a given symbol, inside the terminal.
    Limit time window to current 2 days."""

    plt.date_form('Y-m-d H:M:S')

    close_list = [float(stock[key]['4. close']) for key in stock.keys()]
    open_list = [float(stock[key]['1. open']) for key in stock.keys()]
    high_list = [float(stock[key]['2. high']) for key in stock.keys()]
    low_list = [float(stock[key]['3. low']) for key in stock.keys()]

    # fix data types and limit data to Today
    data_dict = {'Open': open_list, 'Close': close_list, 'High': high_list, 'Low': low_list}
    date_list = list(stock.keys())
    date_list_dt = [plt.string_to_datetime(date) for date in date_list]

    df = pd.DataFrame(data_dict, index= date_list_dt)
    df.index.name='Date'

    today = date.today() - timedelta(days=1)
    df = df[df.index.date>=today]
    date_list = df.index.strftime('%Y-%m-%d %H:%M:%S')
    close_list = df['Close']

    plt.plot(date_list, close_list, marker='hd')

    plt.title(best_stock_symbol + " Stock Price - Short-Term")
    plt.xlabel("Date")
    plt.ylabel("Stock Price $")
    plt.limit_size(True, True)
    plt.plotsize(plt.terminal_width(), plt.terminal_height())
    plt.show()

########################################################################################    
if __name__ == "__main__":

    current_time = time.time()  # time in seconds since 1970
    overall_runtime = 6 * 60 * 60

    #while time.time() < current_time + overall_runtime:
    while(True):  # use "while True:" for an infinite loop

        popular_stocks = extract()
        best_stock_symbol = popular_stocks['ticker'][0] # get symbol of  most popular stock
        popular_stocks = popular_stocks.rename(columns={"ticker":"Ticker", "mean_sentiment":"Mean Sentiment Score"})
        print("\n")
        print("############## Up-to-date Stock News Sentiment #############")
        print("\n")
        print(popular_stocks[['Ticker', 'Mean Sentiment Score']])
        print("\n")
        print("Plotting highest sentiment stock chart. Waiting for API ...")
        print("\n")
        time.sleep(65) # need to wait for API requests to reset
        data = get_short_term_intraday(best_stock_symbol)
        stock = data[1]['Time Series (1min)']

        #plot_candlestick(best_stock_symbol, stock)
        plot_line(best_stock_symbol, stock)
        print("\n")