
import pandas as pd
import feedparser
import yaml
from bs4 import BeautifulSoup
import time
from datetime import timedelta, datetime
import os
from sqlalchemy import create_engine
from sqlalchemy import text
import argparse
import news_util
import pytz
from db_util import engine
import db_util

sector = 'biotech'
# Initialize rss_dict as a global variable
rss_dict = {}

# Initialize added_links as an empty list
global added_links
added_links = []

def init_links():
    # Fetch distinct links from the database and populate the added_links list
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DISTINCT link FROM news_item"))
        added_links = [row[0] for row in result]
        
def clean_text(raw_html):
    cleantext = BeautifulSoup(raw_html, "lxml").text
    return cleantext

def fetch_news(rss_dict):
    cols = ['ticker', 'title', 'summary', 'published_gmt', 'description', 'link', 'language', 'topic', 'sector']
    all_news_items = []

    current_time = datetime.now()
    print(f"Starting new iteration at {current_time}")
    for key, rss_url in rss_dict.items():
        print(f"Fetching news for ticker: {key}")
        feed = feedparser.parse(rss_url)

        for newsitem in feed['items']:
            last_subject = newsitem['tags'][-1]['term'] if 'tags' in newsitem and newsitem['tags'] else None
            all_news_items.append({
                'ticker': key,
                'title': newsitem['title'],
                'summary': clean_text(newsitem['summary']),
                'published_gmt': newsitem['published'],
                'description': clean_text(newsitem['description']),
                'link': newsitem['link'],
                'language': newsitem.get('dc_language', None),  # Extracted language from the provided feed
                'topic': last_subject,
                'sector': sector
            })

    return pd.DataFrame(all_news_items, columns=cols)

def process_news(df):
    df = df[~df['link'].isin(added_links)]
    if not df.empty:
        print("Writing new row for: ", df['ticker'])
        print(df[['ticker', 'topic','published_gmt', 'published_est']].head())
        df['topic'] = df['topic'].str.lower().str.replace(" ", "_").str.replace("/", "_").str.replace("&", "").replace("'", "")
        db_util.write_news_item(df)
        added_links.extend(df['link'].tolist())

    return df

def load_config(sector):
    config_file = f"{sector}.yaml"
    try:
        with open(config_file, 'r') as file:
            rss_dict = yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading {config_file}: {e}")
        return None
    return rss_dict

def main(sector):
    print(f"Fetching news for sector: {sector}")
    
    rss_dict = load_config(sector)
    
    if rss_dict is None:
        print("Failed to load config.")
        return
        
    init_links()
    news_df = fetch_news(rss_dict)
    news_df = news_util.add_published_est(news_df)
    news_df = news_util.add_market(news_df)
    process_news(news_df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch news for a specific sector.")
    parser.add_argument("-s", "--sector", default="biotech", help="Name of the sector. Default is 'biotech'")
    args = parser.parse_args()

    while True:
        main(args.sector)
        print("Waiting for the next iteration...")
        time.sleep(300)  # Adjusted to 5 minutes
