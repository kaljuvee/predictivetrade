# -*- coding: utf-8 -*-
"""eodhd_intraday_crypto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cSkeD3zEtsqbkjFtjqNGFRq0fo0Wjr6g

<a href="https://colab.research.google.com/github/ermolushka/trading-gpt/blob/master/ticker_list_filter.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

## EOD Historical Data - Crypto
"""

import requests
import pandas as pd
import pytz
from io import StringIO
EOD_API_KEY = "5e972a7685a114.008405276404"

import pandas as pd
import requests
from io import StringIO
import datetime
import time  # For converting datetime objects to UNIX timestamp

def get_data(ticker, EOD_API_KEY):
    # Current time in UTC
    now = datetime.datetime.utcnow()
    # Time 48 hours ago
    start_time = now - datetime.timedelta(hours=48)

    # Convert to UNIX timestamp
    now_unix = int(time.mktime(now.timetuple()))
    from_unix = int(time.mktime(start_time.timetuple()))
    #print('now_unix: ', now_unix)
    #print('from_unix: ', from_unix)

    # Construct the URL with the from and to parameters
    #url = f'https://eodhd.com/api/intraday/{ticker}?interval=1m&api_token={EOD_API_KEY}&from={from_unix}&to={now_unix}&fmt=csv'
    url = f'https://eodhd.com/api/intraday/{ticker}?interval=1m&api_token={EOD_API_KEY}'

    response = requests.get(url)
    if response.ok:  # Check if the request was successful
        data = response.content
        # Convert CSV data to DataFrame
        df = pd.read_csv(StringIO(data.decode('utf-8')))
        return df
    else:
        # Print response status and text for debugging
        print("Response Status: ", response.status_code)
        print("Response Text: ", response.text)
        return None

# Use the function with a ticker and your EOD API key

tickers = [
    "BTC-USD.CC",
    "ETH-USD.CC",
    "USDT-USD.CC",
    "BNB-USD.CC",
    "SOL-USD.CC",
    "XRP-USD.CC",
    "USDC-USD.CC",
    "ADA-USD.CC",
    "AVAX-USD.CC",
    "DOGE-USD.CC",
    "TRX-USD.CC",
    "DOT-USD.CC",
    "LINK-USD.CC",
    "TON-USD.CC",
    "MATIC-USD.CC",
    "SHIB-USD.CC",
    "ICP-USD.CC",
    "DAI-USD.CC",
    "LTC-USD.CC",
    "BCH-USD.CC",
    "UNI-USD.CC"
]

# Function to process each dataframe
def process_data(ticker, EOD_API_KEY):
    try:
        df = get_data(ticker, EOD_API_KEY)

        # Calculate the percentage price change
        df['price_change'] = df['Close'].pct_change().fillna(0)

        df['ticker'] = ticker  # Add ticker column
        return df[['ticker', 'Datetime', 'price_change']].head(1440)
    except KeyError as e:
        print(f"Data for {ticker} is missing the expected column: {e}")
        return pd.DataFrame()  # Return an empty DataFrame for this ticker
    except Exception as e:
        print(f"An error occurred while processing data for {ticker}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame for this ticker



# List to hold dataframes
df_list = []

# Loop through tickers and append processed dataframes to the list
for ticker in tickers:
    df_ticker = process_data(ticker, EOD_API_KEY)
    df_list.append(df_ticker)

# Concatenate all dataframes into a single dataframe
df_combined = pd.concat(df_list, ignore_index=True)
df_combined.to_csv('returns.csv')
df_combined.head()

ticker = "BTC-USD.CC"
df = get_data(ticker, EOD_API_KEY)
df.sort_values(by='Datetime', ascending=False, inplace=True)

df.head()

df.shape

df['Datetime'] = pd.to_datetime(df['Datetime'])

# Function to convert to US Eastern Time
def convert_to_est(utc_dt):
    eastern = pytz.timezone('US/Eastern')
    return utc_dt.tz_localize('UTC').tz_convert(eastern)

# Apply conversion using lambda
df['datetime_est'] = df['Datetime'].apply(lambda x: convert_to_est(x))
file_name =  ticker + '.csv'
df.to_csv(file_name)
df.head()



import matplotlib.pyplot as plt

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Close'], marker='o')
plt.title('Close Price Over Time')
plt.xlabel('Datetime (US Eastern Time)')
plt.ylabel('Close Price')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

