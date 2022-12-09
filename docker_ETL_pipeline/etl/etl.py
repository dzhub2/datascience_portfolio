""" 
Extracts data from a MongoDB.
Transforms this data using a sentiment analysis with VADER.
Loads the result of the analysis into a PostgreSQL ddatabase.
"""
import pymongo
import pandas as pd
import sqlalchemy as sqla
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

time.sleep(5)  # seconds, pause to make sure ETL container runs last

def extract():

    # Establish a connection to the MongoDB server
    client = pymongo.MongoClient(host="mongo", port=27017)
    # Select the database you want to use within the MongoDB server
    db = client.stock_news
    # Extract documnets inside the collection "stock_news_col"
    documents = db.stock_news_col.find()

    return documents


def transform(documents):
    # Create a pandas dataframe to populate PostgreSQL from MongoDB collection later
    df = pd.DataFrame()

    # Add the stock news and ticker to df
    for doc in documents:
        tmp = pd.DataFrame(doc, index=['',]) # convert doc into dataframe, where keys are columns
        df = pd.concat([df, tmp], ignore_index=True) # append to large table

    # Perform sentiment analysis using Vader
    s  = SentimentIntensityAnalyzer()
    compound_scores = []
    for news in df['news']:
        sentiment = s.polarity_scores(news)
        compound_scores.append(sentiment['compound'])
    # Calculate the average compound score over all news for this stock
    average_sentiment = sum(compound_scores)/len(compound_scores)

    # create a new column for sentiment score
    df['sentiment_score'] = compound_scores

    # Clean up df
    df.reset_index(drop=True, inplace=True)
    df.drop(columns=['_id'], axis=1, inplace=True)

    # Create a 2nd table where we rank the stocks by popularity
    tickers = df['ticker'].unique()
    # Calculate mean sentiment for each ticker
    mean_sentiment = []
    for ticker in tickers:
        mean_sentiment.append(round(df[df['ticker']==ticker]['sentiment_score'].mean(), 4))
    # Create new DataFrame
    dict = {'ticker': tickers, 'mean_sentiment': mean_sentiment}
    popular_stocks = pd.DataFrame(dict).sort_values(by=['mean_sentiment'], ascending=False)
    popular_stocks.reset_index(inplace=True, drop=True)

    return df, popular_stocks

def load(df, popular_stocks):
    # Connect to PostgreSQL - using standards name + pw
    pg = sqla.create_engine('postgresql://postgres:postgres@postgres:5432/stock_news', echo=False)

    # Populate PostgreSQL DB
    df.to_sql('stock_news', pg, if_exists='replace')
    popular_stocks.to_sql('stock_popularity', pg, if_exists='replace')


if __name__ == "__main__":

    current_time = time.time()  # time in seconds since 1970
    overall_runtime = 6 * 60 * 60

    #while time.time() < current_time + overall_runtime:
    while(True):  # use "while True:" for an infinite loop

        df, popular_stocks = transform(extract())
        load(df, popular_stocks)

        time.sleep(10*60 + 10) # +10 to make sure the new data has been written to MongoDB
