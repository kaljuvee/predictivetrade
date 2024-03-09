import requests
import streamlit as st
import pandas as pd
import datetime
from dotenv import load_dotenv
import os
# Load the environment variables from the .env file
load_dotenv()

# Access the environment variables
api_key = os.getenv('EOD_API_KEY')
# Your EOD Historical Data API key

# List of available currency pairs
symbols = {
    '': '',
    'GOOG.US': 'GOOG.US',
    'AMZN.US': 'AMZN.US',
    'NFLX.US': 'NFLX.US',
    'TSLA.US': 'TSLA.US',
    'AAPL.US': 'AAPL.US',
    'MSFT.US': 'MSFT.US',
    'META.US': 'META.US',
    'NVDA.US': 'NVDA.US',
}

# list of tags available from eod

tags = {
    '': '',
    'balance sheet': 'balance sheet',
    'capital employed': 'capital employed',
    'class action': 'class action',
    'company announcement': 'company announcement',
    'consensus eps estimate': 'consensus eps estimate',
    'consensus estimate': 'consensus estimate',
    'credit rating': 'credit rating',
    'discounted cash flow': 'discounted cash flow',
    'dividend payments': 'dividend payments',
    'earnings estimate': 'earnings estimate',
    'earnings growth': 'earnings growth',
    'earnings per share': 'earnings per share',
    'earnings release': 'earnings release',
    'earnings report': 'earnings report',
    'earnings results': 'earnings results',
    'earnings surprise': 'earnings surprise',
    'estimate revisions': 'estimate revisions',
    'european regulatory news': 'european regulatory news',
    'financial results': 'financial results',
    'fourth quarter': 'fourth quarter',
    'free cash flow': 'free cash flow',
    'future cash flows': 'future cash flows',
    'growth rate': 'growth rate',
    'initial public offering': 'initial public offering',
    'insider ownership': 'insider ownership',
    'insider transactions': 'insider transactions',
    'institutional investors': 'institutional investors',
    'institutional ownership': 'institutional ownership',
    'intrinsic value': 'intrinsic value',
    'market research reports': 'market research reports',
    'net income': 'net income',
    'operating income': 'operating income',
    'present value': 'present value',
    'press releases': 'press releases',
    'price target': 'price target',
    'quarterly earnings': 'quarterly earnings',
    'quarterly results': 'quarterly results',
    'ratings': 'ratings',
    'research analysis and reports': 'research analysis and reports',
    'return on equity': 'return on equity',
    'revenue estimates': 'revenue estimates',
    'revenue growth': 'revenue growth',
    'roce': 'roce',
    'roe': 'roe',
    'share price': 'share price',
    'shareholder rights': 'shareholder rights',
    'shareholder': 'shareholder',
    'shares outstanding': 'shares outstanding',
    'split': 'split',
    'strong buy': 'strong buy',
    'total revenue': 'total revenue',
    'zacks investment research': 'zacks investment research',
    'zacks rank': 'zacks rank'
}

def fetch_news(symbol, start_date, end_date, api_key, tag):
    start_date_fmt = start_date.strftime('%Y-%m-%d')
    end_date_fmt = end_date.strftime('%Y-%m-%d')

    if symbol and tag:
        url = f"https://eodhistoricaldata.com/api/news?api_token={api_key}&s={symbol}&t={tag}&from={start_date_fmt}&to={end_date_fmt}&fmt=json"
    elif symbol:
        url = f"https://eodhistoricaldata.com/api/news?api_token={api_key}&s={symbol}&from={start_date_fmt}&to={end_date_fmt}&fmt=json"
    elif tag:
        url = f"https://eodhistoricaldata.com/api/news?api_token={api_key}&t={tag}&from={start_date_fmt}&to={end_date_fmt}&fmt=json"
    else:
        return
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)[:20]  # Take the latest 20 news items
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if request fails

# Streamlit app setup
st.title('Equities News - EOD Historical Data')

# Dropdown for currency pair selection
selected_pair = st.selectbox('Select ticker: ', list(symbols.keys()))

# Dropdown for tag selection
selected_tag = st.selectbox('Select tag', list(tags.keys()))

# Get the symbol for the selected currency pair
selected_symbol_cur = symbols[selected_pair]

# Get the symbol for the selected tag
selected_symbol_tag = tags[selected_tag]


# Date selection with default values
today = datetime.date.today()
start_date_default = today - datetime.timedelta(days=7)
start_date = st.date_input('Start date: ', value=start_date_default)
end_date = st.date_input('End date: ', value=today)

# Fetch FX news for the selected symbol and date range
if (selected_symbol_cur or selected_symbol_tag) and start_date and end_date:
    news_df = fetch_news(selected_symbol_cur, start_date, end_date, api_key, selected_symbol_tag)

    # Display the news in a table
    if not news_df.empty:
        st.write(news_df)
    else:
        st.write("No news found for the selected symbol and date range.")

