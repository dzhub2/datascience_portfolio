# <ins>Data Science Portfolio</ins>

* [AWS Cloud Dashboard](#aws-cloud-dashboard)<br>
* [Docker ETL Pipeline (in development)](#docker-etl-pipeline-(in-development))<br>
* [Animated Scatter Plot App](#animated-scatter-plot-app)<br>
* [Classification - Titanic Kaggle Competetion](#classification---titanic-kaggle-competetion)<br>
* [Regression - Bike Sharing Kaggle Competetion](#regression---bike-sharing-kaggle-competetion)<br>
* [Song Lyrics Predictor](#song-lyrics-predictor)<br>


## AWS Cloud Dashboard

On this [AWS EC2 Server](http://ec2-18-194-162-57.eu-central-1.compute.amazonaws.com/public/dashboard/2c90b9eb-2f04-44e1-8e4f-27ada1177b57), I deployed a Metabase Dashboard by connecting it to a PostgreSQL database using AWS RDS. The data was taken from the Microsoft Azure Northwind database, located in [this](https://github.com/dzhub2/datascience_portfolio/tree/master/sql_northwind) folder.

<ins>Methods:</ins> AWS EC2 and RDS, PostgreSQL, Metabase, Dashboarding, SQLAlchemy

## Docker ETL Pipeline (in development)

In this Docker Image (TBD), I built an ETL pipeline consisting of a Stock Market API, MongoDB, sentiment analysis and PostgreSQL to determine the most important stock market news of the day.

<ins>Methods:</ins> Docker, API, MongoDB, PostgreSQL, Sentiment analysis

## Animated Scatter Plot App

On this [website](https://dzhub2.pythonanywhere.com), I deployed an animated scatter plot app. [Here](https://github.com/dzhub2/datascience_portfolio/blob/master/population_dash_app/animated_scatter_by_population.ipynb) is the notebook version, which can be run locally without the website.

<ins>Methods:</ins> Plotly Express, Dash, Pandas

## Classification - Titanic Kaggle Competetion

[Here](https://github.com/dzhub2/datascience_portfolio/blob/master/kaggle_titanic/titanic_submission.ipynb), I built a Machine Learning classification model to predict the survival of passengers on the Titanic. This project is part of a [Kaggle competition](https://www.kaggle.com/competitions/titanic/overview/description) and received a score of 0.78.

<ins>Methods:</ins> Feature Engineering, XGBoost

## Regression - Bike Sharing Kaggle Competetion

[Here](https://github.com/dzhub2/datascience_portfolio/blob/master/kaggle_bike_rental/bike_project.ipynb), I built several Machine Learning regression models to forecast the use of a city bikeshare system. This project is part of a [Kaggle competition](https://www.kaggle.com/competitions/bike-sharing-demand/overview) and received a score of 0.40 (Top 7%).

<ins>Methods:</ins> Exploratory Data Analysis, Feature Engineering, ML Regression Models

## Song Lyrics Predictor

[Here](https://github.com/dzhub2/datascience_portfolio/blob/master/lyric_classification/lyric_classification.ipynb), I implemented a web scrapper collecting song lyrics from different artists to build a Bag of Words NLP model. For any user input-sentence, the program predicts which artist most likely used this sentence in one of their lyrics.

<ins>Methods:</ins> Web scrapping (BeautifulSoup), RegEx, NLP vectorizer, Classification, Hyperparameter tuning


