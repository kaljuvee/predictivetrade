import pytz
import pandas as pd
import time
from datetime import datetime

def gmt_to_est(gmt_datetime):
    """Converts a GMT/UTC datetime to EST or EDT, depending on the date."""
    
    # Check if gmt_datetime is a string and convert it to datetime if necessary
    if isinstance(gmt_datetime, str):
        try:
            gmt_datetime = datetime.strptime(gmt_datetime, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            gmt_datetime = datetime.strptime(gmt_datetime, '%a, %d %b %Y %H:%M %Z')
    
    # Convert the provided datetime to a timezone-aware datetime in GMT
    gmt_timezone = pytz.timezone('GMT')
    gmt_datetime = gmt_timezone.localize(gmt_datetime)
    
    # Convert the GMT datetime to Eastern Time (could be either EST or EDT)
    est_timezone = pytz.timezone('US/Eastern')
    est_datetime = gmt_datetime.astimezone(est_timezone)
    
    return est_datetime

def add_market(news_df):
    try:
        # Define the time boundaries for each trading session
        market_open_start = 9 + 30/60  # 9:30 AM in decimal hours
        market_open_end = 16  # 4:00 PM in decimal hours
        after_hours_end = 20  # 8:00 PM in decimal hours
        pre_market_start = 4  # 7:00 AM in decimal hours
        pre_market_end = 9 + 25/60  # 9:25 AM in decimal hours

        # Initialize the "market" column
        news_df['market'] = 'overnight'

        # Populate the "market" column based on the trading session rules
        news_df.loc[(news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 >= market_open_start) &
                    (news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 < market_open_end), 'market'] = 'market_open'
        news_df.loc[(news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 >= market_open_end) &
                    (news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 < after_hours_end), 'market'] = 'after_hours'
        news_df.loc[(news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 >= pre_market_start) &
                    (news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 < pre_market_end), 'market'] = 'pre_market'

        # Extract the hour of the day on a 24-hour basis
        news_df['hour_of_day'] = news_df['published_est'].dt.hour
    except Exception as e:
        print(f"Error while converting GMT to EST: {e}")
    # Optionally, you can return None or keep the dataframe as it is, depending on your requirements
        return None
    return news_df

def add_published_est(news_df):
    try:
        news_df['published_est'] = news_df['published_gmt'].apply(lambda x: gmt_to_est(x))
        news_df['published_est'] = news_df['published_est'].dt.tz_localize(None)
    except Exception as e:
        print(f"Error while converting GMT to EST: {e}")
    # Optionally, you can return None or keep the dataframe as it is, depending on your requirements
        return None
    return news_df
