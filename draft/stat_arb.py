import pandas as pd
from util import exchange_util, backtest_util, db_util
import math
# Define global variables
assets = 10
position = 10000
threshold = 1.0
stop_loss = 1.0
profit_limit = 1.0
days = 1
strategy = "One-sided"
reinvest_profits = False
bid_ask_spread = 0.1
maker_fee = 0.1
timeframe = "1d"
symbols = ['BTC/USD', 'ETH/USD']
exchange = 'bitstamp'
reinvest = True

def fetch_price_data(exchange, symbols, timeframe, days):
    try:
        price_data = exchange_util.get_prices(exchange, symbols, timeframe, days)
        print("Price data fetched successfully.")
        return price_data
    except Exception as e:
        print(f"Failed to fetch price data: {e}")
        return pd.DataFrame()

def get_bid_ask(exchange):
    try:
        bid_ask_data = db_util.get_bid_ask(exchange)
        print("Got bid-Ask successfully.")
        return bid_ask_data
    except Exception as e:
        print(f"Failed to get bid-ask data: {e}")
        return pd.DataFrame()

def get_returns(data):
    try:
        returns = backtest_util.calculate_returns(data)
        print("Returns calculated successfully.")
        return returns
    except Exception as e:
        print(f"Failed to calculate returns: {e}")
        return pd.DataFrame()

def perform_backtest(data, pairs, threshold, position, stop_loss, profit_limit, exchange, strategy, maker_fee, reinvest):
    try:
        run_id = backtest_util.get_run_id()
        if strategy == "One-sided":
            pnl = backtest_util.backtest_zscores_one_sided_bid_ask(data, pairs, threshold, position, stop_loss, profit_limit, exchange, run_id, maker_fee, reinvest)
        elif strategy == "Two-sided":
            pnl = backtest_util.backtest_zscores_two_sided_bid_ask(data, pairs, threshold, position, stop_loss, profit_limit, exchange, run_id, maker_fee, reinvest)
        else:
            raise ValueError("Invalid strategy selected.")
        
        print("Backtest performed successfully.")
        return pnl
    except Exception as e:
        print(f"Failed to perform backtest: {e}")
        return pd.DataFrame()

def store_pnl(pnl):
    try:
        db_util.write_pnl(pnl)
        print("Backtest PnL saved successfully.")
    except Exception as e:
        print(f"Failed to store PnL: {e}")

def main():

    # Calculate Bid-Ask
    bid_ask_data = get_bid_ask(exchange)
    print('bid_ask_data data: ', bid_ask_data.shape)

    # Calculate Returns
    returns_data = get_returns(bid_ask_data)
    pairs = backtest_util.get_pairs(symbols)
    # Perform Backtest
    pnl = perform_backtest(bid_ask_data, pairs, threshold, position, stop_loss, profit_limit, exchange, strategy, maker_fee, reinvest)
    print('pnl: ', pnl.head())
    # Store PnL
    store_pnl(pnl)


if __name__ == "__main__":
    main()
