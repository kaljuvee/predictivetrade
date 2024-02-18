import alpaca_trade_api as tradeapi
from alpaca_trade_api import TimeFrame
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time

# Alpaca API credentials
API_KEY = 'PKWSHV3AS4J71TGOQEOC'
API_SECRET = 'wffi5PYdLHI2N/6Kfqx6LBTuVlfURGgOp9u5mXo5'
BASE_URL = 'https://paper-api.alpaca.markets'  # Use the paper trading URL for testing

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Define your pair and parameters
asset_1 = 'AAPL'
asset_2 = 'MSFT'
window = 60  # Lookback window for calculating statistics
z_entry_threshold = 1  # Z-score threshold to enter trades
z_exit_threshold = 0  # Z-score threshold to exit trades
trading_qty = 1000  # Quantity to trade

def fetch_price_data(symbol, start_date, end_date):
    # Using get_bars instead of get_barset
    bars = api.get_bars(symbol, tradeapi.TimeFrame.Day, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')).df
    return bars

def calculate_spread_zscore(asset_1_prices, asset_2_prices, window=window):
    spread = asset_1_prices - asset_2_prices
    spread_mean = spread.rolling(window=window).mean()
    spread_std = spread.rolling(window=window).std()
    zscore = (spread - spread_mean) / spread_std
    return zscore

def check_positions():
    positions = api.list_positions()
    positions_dict = {position.symbol: position for position in positions}
    return positions_dict

def trade_logic():
        # Example start and end dates for fetching price data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)  # Fetch data for the last 30 days

    asset_1_prices = fetch_price_data(asset_1, start_date, end_date)
    asset_2_prices = fetch_price_data(asset_2, start_date, end_date)
    zscore = calculate_spread_zscore(asset_1_prices, asset_2_prices)

    current_zscore = zscore.iloc[-1]
    positions = check_positions()

    if current_zscore > z_entry_threshold:
        # Short asset_1 and Long asset_2
        if asset_1 not in positions or positions[asset_1].side == 'long':
            api.submit_order(symbol=asset_1, qty=trading_qty, side='sell', type='market', time_in_force='gtc')
        if asset_2 not in positions or positions[asset_2].side == 'short':
            api.submit_order(symbol=asset_2, qty=trading_qty, side='buy', type='market', time_in_force='gtc')
    elif current_zscore < -z_entry_threshold:
        # Long asset_1 and Short asset_2
        if asset_1 not in positions or positions[asset_1].side == 'short':
            api.submit_order(symbol=asset_1, qty=trading_qty, side='buy', type='market', time_in_force='gtc')
        if asset_2 not in positions or positions[asset_2].side == 'long':
            api.submit_order(symbol=asset_2, qty=trading_qty, side='sell', type='market', time_in_force='gtc')
    elif abs(current_zscore) < z_exit_threshold:
        # Close positions if they exist
        if asset_1 in positions:
            api.submit_order(symbol=asset_1, qty=abs(int(positions[asset_1].qty)), side='buy' if positions[asset_1].side == 'short' else 'sell', type='market', time_in_force='gtc')
        if asset_2 in positions:
            api.submit_order(symbol=asset_2, qty=abs(int(positions[asset_2].qty)), side='buy' if positions[asset_2].side == 'short' else 'sell', type='market', time_in_force='gtc')

# Main trading function
def run_strategy():
    while True:
        trade_logic()
        # Sleep to avoid hitting rate limits, adjust the sleep time as needed
        time.sleep(60)

if __name__ == "__main__":
    run_strategy()
