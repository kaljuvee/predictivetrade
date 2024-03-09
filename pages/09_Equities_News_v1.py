import streamlit as st
import pandas as pd
from alpaca_trade_api import REST
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Access the environment variables
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_API_SECRET')

# List of tickers
keys_list = [
    "FBIO", "KA", "QGEN", "DYAI", "JSPR", "ANAB", "ECOR", "ELOX", "MDWD", "RAD.AX",
    "EYEN", "PYPD", "SCLX", "TALS", "SNCE", "ORIC", "TTOO", "ADXN", "SPRY", "IMNN",
    "ADTX", "OCUP", "ARQT", "IMCR", "ORPHA.CO", "VIR", "DBVT", "ICCC", "ONCT", "ALVO",
    "EVAX", "CHRS", "MYNZ", "SCPH", "MDAI", "BIOR", "MLYS", "LGVN", "BMRA", "KRON",
    "CDTX", "NTLA", "ARQT", "TLSA", "PCIB.OL", "SANN.SW"
]

#st.cache(show_spinner=False)
def get_news(ticker, start_date, end_date, limit=50):
    rest_client = REST(API_KEY, API_SECRET)
    news_items = rest_client.get_news(ticker, start_date, end_date)
    news_items = news_items[:limit]  # Limit the number of news items to the specified limit
    news_df = pd.DataFrame([item._raw for item in news_items])

    # Add ticker column with hyperlink
    news_df['ticker'] = '<a href="https://www.marketwatch.com/investing/stock/' + ticker + '" target="_blank">' + ticker + '</a>'

    # Check if 'created_at' exists and convert to EST
    if 'created_at' in news_df.columns:
        est = pytz.timezone('US/Eastern')
        news_df['created_at'] = pd.to_datetime(news_df['created_at']).dt.tz_convert(est)
        news_df.rename(columns={'created_at': 'created_est'}, inplace=True)
    else:
        news_df['created_est'] = 'N/A'  # Placeholder if 'created_at' does not exist

    # Drop unnecessary columns
    columns_to_drop = ['author', 'content', 'id', 'images', 'summary', 'updated_at']
    news_df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    # Create 'title' column if 'url' exists
    if 'url' in news_df.columns and 'headline' in news_df.columns:
        news_df['title'] = '<a href="' + news_df['url'] + '" target="_blank">' + news_df['headline'] + '</a>'
        news_df.drop(columns=['headline', 'url'], inplace=True)
    else:
        news_df['title'] = 'N/A'  # Placeholder if 'url' or 'headline' does not exist

    return news_df

st.title("Equity Sector News - Biotech (Benzinga)")

# Setting up dates
end_date = datetime.now().date()
start_date = end_date - timedelta(days=5)

def fetch_and_display_news():
    try:
        with st.spinner('Fetching news...'):
            # Check if news data is already stored in session state
            if 'all_news' in st.session_state:
                # Display cached news from session state
                html = st.session_state.all_news.to_html(escape=False, index=False)
                st.markdown(html, unsafe_allow_html=True)
                st.write("Showing cached news. Refresh to get the latest.")

            # Fetch new news data
            all_news = pd.DataFrame()
            for ticker in keys_list:
                news_df = get_news(ticker, start_date, end_date, limit=50)
                all_news = pd.concat([all_news, news_df], ignore_index=True)

            # Update session state with new news data
            st.session_state.all_news = all_news

            # Convert DataFrame to HTML and then use st.markdown to render it
            # Only do this if there was no cached news, or after fetching new news
            if 'all_news' not in st.session_state or not st.session_state.get('used_cache', False):
                html = all_news.to_html(escape=False, index=False)
                st.markdown(html, unsafe_allow_html=True)
                st.session_state.used_cache = True  # Mark that cached news has been used/displayed

    except Exception as e:
        st.error(f"An error occurred: {e}")
        # Optionally, display cached news if available when there's an error fetching new news
        if 'all_news' in st.session_state:
            st.write("Displaying cached news due to an error.")
            html = st.session_state.all_news.to_html(escape=False, index=False)
            st.markdown(html, unsafe_allow_html=True)

# Fetch and display news immediately when the app loads
fetch_and_display_news()

# Refresh button to refetch and display news
if st.button('Refresh'):
    fetch_and_display_news()