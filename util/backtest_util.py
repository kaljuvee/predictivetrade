import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import ccxt
from plotly.subplots import make_subplots
import numpy as np
import plotly.express as px
from util import exchange_util, plot_util
from scipy.stats import zscore
import time
import itertools

def get_run_id():
    return int(round(time.time() * 1000))

def get_pairs(crypto_symbols):
    # Generate all permutations of the crypto symbols
    symbol_permutations = itertools.permutations(crypto_symbols, 2)
    # Create a list of dictionaries for the pairs
    pairs = [{'Asset1': symbol1, 'Asset2': symbol2} for symbol1, symbol2 in symbol_permutations]
    # Convert the list of dictionaries to a DataFrame
    pairs_df = pd.DataFrame(pairs)
    return pairs_df  # Return as a DataFrame

# Calculate z-score
def zscore(series):
    return (series - series.mean()) / np.std(series)

def initialize_position(positions, symbol_pair):
    """Initializes the position status for a given symbol pair if not already present."""
    if symbol_pair not in positions:
        positions[symbol_pair] = {
            'open': False,
            'entry_price': 0,
            'lots': 0,
            'cum_pnl': 0
        }

def backtest_zscores_one_sided(prices, sorted_pairs, threshold, position_size, stop_loss_limit, profit_limit, maker_fee=0.1):
    signals_list = []
    positions = {}
    pivot_prices = prices.pivot(index='timestamp', columns='symbol', values='close')
    global_gross_cum_pnl = 0  # Initialize cumulative PnL as a global variable
    global_net_cum_pnl = 0  # Initialize cumulative PnL as a global variable
    stop_loss_limit = stop_loss_limit / 100
    profit_limit = profit_limit / 100
    maker_fee = maker_fee / 100
    
    for index, row in sorted_pairs.iterrows():
        asset1, asset2 = row['Asset1'], row['Asset2']
        symbol_pair = f"{asset1}-{asset2}"
        
        # Ensure each pair's position is tracked individually, but PnL is accumulated globally
        if symbol_pair not in positions:
            positions[symbol_pair] = {'open': False, 'entry_price': 0, 'lots': 0}

        if asset1 in pivot_prices.columns and asset2 in pivot_prices.columns:
            price_ratios = pivot_prices[asset1] / pivot_prices[asset2]
            z_scores = zscore(price_ratios.dropna())

            for timestamp, z_score in zip(price_ratios.index, z_scores):
                position = positions[symbol_pair]

                if not position['open'] and z_score < -threshold:
                    entry_price = pivot_prices.loc[timestamp, asset1]
                    if entry_price > 0:
                        position['open'] = True
                        position['entry_price'] = entry_price
                        position['lots'] = position_size / entry_price
                        signals_list.append({
                            'Pair': symbol_pair, 'Timestamp': timestamp, 'Action': 'Open Position',
                            'Z-Score': z_score, 'Strategy': 'One-sided', 'Price': entry_price, 'Lots': position['lots'], 'Gross PnL': '', 'Net PnL': '',
                            'Cumulative Gross PnL': global_gross_cum_pnl, 'Cumulative Net PnL': global_net_cum_pnl
                        })

                elif position['open']:
                    exit_price = pivot_prices.loc[timestamp, asset1]
                    change_percentage = (exit_price - position['entry_price']) / position['entry_price']                    
                    if change_percentage <= -stop_loss_limit or change_percentage >= profit_limit:
                        position['open'] = False
                        gross_pnl = position['lots'] * (exit_price - position['entry_price'])
                        net_pnl = position['lots'] * (exit_price - position['entry_price']) - maker_fee * position_size
                        global_gross_cum_pnl += gross_pnl
                        global_net_cum_pnl += net_pnl
                        action = 'Closed with Stop Loss' if change_percentage <= -stop_loss_limit else 'Closed with Profit'
                        signals_list.append({
                            'Pair': symbol_pair, 'Timestamp': timestamp, 'Action': action,
                            'Z-Score': z_score, 'Strategy': 'One-sided', 'Price': exit_price, 'Gross PnL': gross_pnl, 'Net PnL': net_pnl,
                            'Cumulative Gross PnL': global_gross_cum_pnl, 'Cumulative Net PnL': global_net_cum_pnl
                        })

    return pd.DataFrame(signals_list)

def get_bid(mid, spread_percentage):
    bid = mid * (1 - 0.5 * spread_percentage / 100)
    return bid

def get_ask(mid, spread_percentage):
    ask = mid * (1 + 0.5 * spread_percentage / 100)
    return ask
    
def backtest_zscores_one_sided_ba(prices, sorted_pairs, threshold, position_size, stop_loss_limit, profit_limit, maker_fee=0.1):
    signals_list = []
    positions = {}
    pivot_prices = prices.pivot(index='timestamp', columns='symbol', values='close')
    global_gross_cum_pnl = 0  # Initialize cumulative PnL as a global variable
    global_net_cum_pnl = 0  # Initialize cumulative PnL as a global variable
    stop_loss_limit = stop_loss_limit / 100
    profit_limit = profit_limit / 100
    maker_fee = maker_fee / 100
    spread = 0.1
    
    for index, row in sorted_pairs.iterrows():
        asset1, asset2 = row['Asset1'], row['Asset2']
        symbol_pair = f"{asset1}-{asset2}"
        
        # Ensure each pair's position is tracked individually, but PnL is accumulated globally
        if symbol_pair not in positions:
            positions[symbol_pair] = {'open': False, 'entry_price': 0, 'lots': 0}

        if asset1 in pivot_prices.columns and asset2 in pivot_prices.columns:
            price_ratios = pivot_prices[asset1] / pivot_prices[asset2]
            z_scores = zscore(price_ratios.dropna())

            for timestamp, z_score in zip(price_ratios.index, z_scores):
                position = positions[symbol_pair]

                if not position['open'] and z_score < -threshold:
                    entry_price = pivot_prices.loc[timestamp, asset1]
                    entry_price = get_ask(entry_price, spread)
                    
                    if entry_price > 0:
                        position['open'] = True
                        position['entry_price'] = entry_price
                        position['lots'] = position_size / entry_price
                        signals_list.append({
                            'Pair': symbol_pair, 'Timestamp': timestamp, 'Action': 'Open Position',
                            'Z-Score': z_score, 'Strategy': 'One-sided', 'Price': entry_price, 'Lots': position['lots'], 'Gross PnL': '', 'Net PnL': '',
                            'Cumulative Gross PnL': global_gross_cum_pnl, 'Cumulative Net PnL': global_net_cum_pnl
                        })

                elif position['open']:
                    exit_price = pivot_prices.loc[timestamp, asset1]
                    exit_price = get_bid(entry_price, spread)
                    change_percentage = (exit_price - position['entry_price']) / position['entry_price']                    
                    if change_percentage <= -stop_loss_limit or change_percentage >= profit_limit:
                        position['open'] = False
                        gross_pnl = position['lots'] * (exit_price - position['entry_price'])
                        net_pnl = position['lots'] * (exit_price - position['entry_price']) - maker_fee * position_size
                        global_gross_cum_pnl += gross_pnl
                        global_net_cum_pnl += net_pnl
                        action = 'Closed with Stop Loss' if change_percentage <= -stop_loss_limit else 'Closed with Profit'
                        signals_list.append({
                            'Pair': symbol_pair, 'Timestamp': timestamp, 'Action': action,
                            'Z-Score': z_score, 'Strategy': 'One-sided', 'Price': exit_price, 'Gross PnL': gross_pnl, 'Net PnL': net_pnl,
                            'Cumulative Gross PnL': global_gross_cum_pnl, 'Cumulative Net PnL': global_net_cum_pnl
                        })

    return pd.DataFrame(signals_list)

def get_merge_key(timestamp_series):
    # Rounds the given timestamp Series to the nearest minute
    return timestamp_series.dt.floor('T')

def backtest_zscores_one_sided_bid_ask(prices, sorted_pairs, threshold, position_size, 
                                       stop_loss_limit, profit_limit, exchange, run_id, maker_fee=0.1, reinvest=True):
    pnl_list = []
    global_gross_cum_pnl = 0
    global_net_cum_pnl = 0
    initial_position_size = position_size
    
    stop_loss_limit /= 100
    profit_limit /= 100
    maker_fee  = int(maker_fee)
    maker_fee /= 100

    try:
        positions = initialize_positions(sorted_pairs)
    except Exception as e:
        print(f"Error initializing positions: {e}")
        return

    for index, row in sorted_pairs.iterrows():
        asset1, asset2 = row['Asset1'], row['Asset2']
        symbol_pair = f"{asset1}-{asset2}"
        
        adjusted_position_size = position_size / len(sorted_pairs) if len(sorted_pairs) > 0 else 0

        try:
            merged_prices, z_scores = merge_and_calculate_ratios(prices, asset1, asset2)
        except Exception as e:
            print(f"Error merging prices and calculating ratios for {symbol_pair}: {e}")
            continue

        for i, z_score in enumerate(z_scores):
            timestamp = merged_prices.iloc[i]['timestamp_asset1']
            position = positions[symbol_pair]

            try:
                if not position['open'] and z_score < -threshold:
                    entry_ask_price = merged_prices.iloc[i]['ask_asset1']
                    open_position(position, pnl_list, symbol_pair, timestamp, z_score, entry_ask_price, 
                                  adjusted_position_size, global_gross_cum_pnl, global_net_cum_pnl, exchange, run_id)

                elif position['open']:
                    exit_bid_price = merged_prices.iloc[i]['bid_asset1']
                    change_percentage = (exit_bid_price - position['entry_price']) / position['entry_price']
                    action = 'Closed with Stop Loss' if change_percentage <= -stop_loss_limit else 'Closed with Profit'
                    if change_percentage <= -stop_loss_limit or change_percentage >= profit_limit:
                        global_gross_cum_pnl, global_net_cum_pnl, adjusted_position_size = close_position(
                            position, pnl_list, symbol_pair, timestamp, z_score, exit_bid_price, maker_fee, adjusted_position_size, 
                            global_gross_cum_pnl, global_net_cum_pnl, action, reinvest, exchange, run_id
                        )
            except Exception as e:
                print(f"Error processing position for {symbol_pair} at timestamp {timestamp}: {e}")

    # Update the position size for the next iteration if reinvesting
    if reinvest:
        position_size = initial_position_size + global_net_cum_pnl

    try:
        pnl_df = pd.DataFrame(pnl_list)
        pnl_df['gross_pnl'] = pd.to_numeric(pnl_df['gross_pnl'], errors='coerce').fillna(0)
    except Exception as e:
        print(f"Error creating PnL DataFrame: {e}")
        return
    return pnl_df

def calculate_returns(all_data):
    # Convert columns to numeric types (excluding 'timestamp' and 'symbol')
    numeric_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_cols:
        all_data[col] = pd.to_numeric(all_data[col], errors='coerce')

    # Filter data for each symbol and calculate one-minute returns
    symbols = all_data['symbol'].unique()
    returns = pd.DataFrame(index=all_data['timestamp'].unique())

    for symbol in symbols:
        # Filter data for the current symbol
        symbol_data = all_data[all_data['symbol'] == symbol]

        # Calculate one-minute returns and add to the returns DataFrame
        symbol_returns = symbol_data.set_index('timestamp')['close'].pct_change()
        returns[symbol] = symbol_returns

    return returns
    
