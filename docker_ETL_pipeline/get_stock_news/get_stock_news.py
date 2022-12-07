
import requests
import os
API_KEY = os.getenv('ALPHAVANTAGE_API_KEY') # API key stored in environmental variable, else pass it here

import pandas as pd
from datetime import date, timedelta
import logging
import pymongo

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

    response = requests.get(base_url, params=params)
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

    response = requests.get(base_url, params=params)
    #Save CSV to file
    with open('./test.csv', 'wb') as file:
        file.write(response.content)
    df = pd.read_csv('./test.csv') #Create pandas dataframe
    df.set_index('time', inplace=True) #Time-series index
    return df

def get_yesterdays_data(df):
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
    return data

# get most recent stock news for a ticker
base_url = 'https://www.alphavantage.co/query?'
tickers = ['TSLA']

data = get_the_news(base_url, tickers) 

# set up connection to mongoDB
client = pymongo.MongoClient(host="mongo", port=27017) #my_mongodb container defined in .yml file
db = client.stock_news #stock_news = DB to be created
db.stock_news_col.drop() #delete collection if it already exists

#store data in mongoDB
logging.info('Storing in mongoDB!')

data_dict = {}

for item in range(int(data['items'])): #gives the number of requested items, 200 max.
    data_dict.update({'ticker': tickers[0], 'news': data['feed'][item]['summary']})
    db.stock_news_col.insert_one(data_dict.copy()) #set the collection name here