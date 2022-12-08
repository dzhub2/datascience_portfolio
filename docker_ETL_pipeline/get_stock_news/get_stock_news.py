
import requests
import os
API_KEY = os.getenv('ALPHAVANTAGE_API_KEY') # API key stored in environmental variable, else pass it here

import pandas as pd
from datetime import date, timedelta
import logging
import pymongo
from pytickersymbols import PyTickerSymbols
import time

## alpha vantage stock market API functions

def convert_json_to_pandas(header, response_dict):
    """ Converts json output into pandas DataFrame with dateTime index column"""
    df = pd.DataFrame.from_dict(response_dict[header], orient='index')
    #Clean up column names
    df_cols = [i.split('. ')[1] for i in df.columns]
    df.columns = df_cols
    # convert string to float
    for col in df.columns:
        df[col] = df[col].astype(float)
    df.index = pd.to_datetime(df.index)
    return df

def get_short_term_intraday(base_url, symbol):
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

def get_long_term_intraday(base_url, symbol):
    # long term intraday data (trailing 2 years) - ONLY USES CSV
    params = {'function': 'TIME_SERIES_INTRADAY_EXTENDED',
            'symbol': symbol,
            'interval': '1min',
            'slice': 'year1month1', #'year1month2' , ..., 'year2month12'=this is the farthest away
            'adjusted': 'true',
            'apikey': API_KEY}

    try:
        response = requests.get(base_url, params=params)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    #Save CSV to file
    with open('./test.csv', 'wb') as file:
        file.write(response.content)
    df = pd.read_csv('./test.csv') #Create pandas dataframe
    df.set_index('time', inplace=True) #Time-series index
    return df

def extract_yesterdays_stock_data(df):
    # get yesterdays stock
    yesterday = date.today() - timedelta(days=1)
    df = df[df.index.date==yesterday]
    return df

def get_the_news(base_url, tickers):
    # get current news
    params = {'function': 'NEWS_SENTIMENT',
            'tickers': tickers,
            'sort': 'latest',
            'limit': 50, #200 highest or contact support
            #time_from: '20220410T013' 
            'apikey': API_KEY}

    response = requests.get(base_url, params=params)
    data = response.json()
    my_error_code = 0
    if ('Error Message' in data) or ('Invalid' in list(data.values())[0]) or ('Thank you for using Alpha Vantage' in list(data.values())[0]):
        #print(data)
        my_error_code = 1 # the API doesn't return an Exception for these cases -> hand code it
    return data, my_error_code

# get all DAX 40 stock symbols to put them into the API
stock_data = PyTickerSymbols()
german_stocks = list(stock_data.get_stocks_by_index('DAX'))

dax_symbols = []
for i in range(len(german_stocks)):
    dax_symbols.append(german_stocks[i]['symbol'])

# set up connection to mongoDB
client = pymongo.MongoClient(host="mongo", port=27017) #mongo container defined in .yml file
db = client.stock_news #stock_news = DB to be created
db.stock_news_col.drop() #delete collection if it already exists

#get data and store data in mongoDB
logging.info('Storing in mongoDB!')

base_url = 'https://www.alphavantage.co/query?'
data_dict = {}

# use custom symbol list, in case DAX symbols create problems in the API (e.g. finds wrong stock)
# these are the 13 largest NASDAQ stocks, measured by market cap
nasdaq_13 = ['AAPL','MSFT','GOOG','AMZN','TSLA','NVDA','META','PEP','ASML','GEN','AZN','COST','AVGO'] 
nasdaq_5 = ['AAPL','GOOG','AMZN','TSLA','NVDA'] 

while True:
    for ticker in nasdaq_5:
        data, error_code = get_the_news(base_url, ticker) # get data for this ticker

        if error_code == 0: # only save data if API returned news for this symbol
            for item in range(int(data['items'])): #gives the number of requested items, 200 max.
                data_dict.update({'ticker': ticker, 'news': data['feed'][item]['summary']})
                db.stock_news_col.insert_one(data_dict.copy()) #set the collection name here
        
        # time.sleep(20) # have to wait, because the free API only allows 5 calls per minute
        
    time.sleep(60*60) # update the news once every hour.