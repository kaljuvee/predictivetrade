import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from util import db_util

st.title("Equities Event Based Prediction")

def format_colours(df):
    # Function to apply color based on the condition for 'daily_alpha' column
    def color_daily_alpha(val):
        color = 'red' if val < 0 else 'green'
        return f'color: {color}'

    # Function to apply color based on the condition for 'actual_action' and 'predicted_action' columns
    def color_actions(val):
        color = 'green' if val == 'long' else 'red'
        return f'color: {color}'

    # Apply formatting to 'daily_alpha', 'actual_action', and 'predicted_action' columns
    styled_df = df.style.map(color_daily_alpha, subset=['daily_alpha'])\
                        .map(color_actions, subset=['actual_action', 'predicted_action'])
    
    return styled_df


def get_news():
    try:
        # Fetch news data using db_util
        news_df = db_util.get_news_prediction()
        
        # Format the 'ticker' column with hyperlinks
        news_df['ticker'] = '<a href="https://www.marketwatch.com/investing/stock/' + news_df['ticker'] + '" target="_blank">' + news_df['ticker'] + '</a>'
        
        # Format the 'title' column with hyperlinks
        news_df['title'] = '<a href="' + news_df['link'] + '" target="_blank">' + news_df['title'] + '</a>'
        
        # Drop the 'link' column
        news_df = news_df.drop(columns=['link'])

        # Apply formatting to the DataFrame and obtain a Styler object for display
        
        # Return the original DataFrame for data manipulations and the Styler for display
        return news_df
    
    except Exception as e:
        print(f"An error occurred while fetching and processing news: {e}")
        # Return an empty DataFrame in case of error
        return pd.DataFrame() # Return two empty DataFrames to match the expected return type


import streamlit as st

def display_paginated_df(news_df, page_size=50):
    try:
        provider_options = ['Globenewswire']
        selected_provided = st.selectbox("Select provider:", provider_options)

        sector_options = ['biotech']
        selected_sector = st.selectbox("Select sector:", sector_options)
        
        # Ensure the DataFrame is sorted by 'published_est' in descending order
        news_df = news_df.sort_values(by='published_est', ascending=False)
    
        # Search box to filter by ticker
        search_query = st.text_input("Filter by ticker:", "")

        # Filter the DataFrame based on the search query
        if search_query:
            # Ensure case-insensitive search by converting both to uppercase
            filtered_df = news_df[news_df['ticker'].str.upper().str.contains(search_query.upper())]
        else:
            filtered_df = news_df

        # Pagination setup for the filtered DataFrame
        total_pages = len(filtered_df) // page_size + (len(filtered_df) % page_size > 0)
        selected_page = st.selectbox("Select page:", list(range(total_pages)))

        # Calculate start and end row indices for the current page
        start_row = page_size * selected_page
        end_row = start_row + page_size

        # Displaying the filtered DataFrame slice
        st.write(f"Displaying rows {start_row+1} to {min(end_row, len(filtered_df))} of {len(filtered_df)}")
        st.markdown(filtered_df.iloc[start_row:end_row].to_html(escape=False, index=False), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


# Usage:
# Assuming 'get_news' function is defined and fetches the news DataFrame
news_df = get_news()
# Define the columns to include in display_df
columns_to_include = ['ticker', 'title', 'topic', 'published_est', 'daily_alpha', 'actual_action', 'predicted_action', 'confidence']
display_df = news_df[columns_to_include].copy()  # Create a copy for display

# Call the simplified function without the need for a button
display_paginated_df(display_df, page_size=50)