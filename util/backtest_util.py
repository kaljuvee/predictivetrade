import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import ccxt
from plotly.subplots import make_subplots
import numpy as np
import plotly.express as px
from util import exchange_util, plot_util
from scipy.stats import zscore

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

def backtest_zscores_one_sided_bid_ask(prices, sorted_pairs, threshold, position_size, stop_loss_limit, profit_limit, maker_fee=0.1):
    signals_list = []
    positions = {}
    global_gross_cum_pnl = 0  # Initialize gross cumulative PnL as a global variable
    global_net_cum_pnl = 0  # Initialize net cumulative PnL as a global variable
    
    # Adjust limits and fees to decimal form
    stop_loss_limit /= 100
    profit_limit /= 100
    maker_fee /= 100
    
    for index, row in sorted_pairs.iterrows():
        asset1, asset2 = row['Asset1'], row['Asset2']
        symbol_pair = f"{asset1}-{asset2}"
        
        if symbol_pair not in positions:
            positions[symbol_pair] = {'open': False, 'entry_price': 0, 'lots': 0}

        try:
            # Filter prices for each asset and create a merge key
            prices_asset1 = prices[prices['symbol'] == asset1].copy()
            prices_asset2 = prices[prices['symbol'] == asset2].copy()
            prices_asset1['merge_key'] = get_merge_key(prices_asset1['timestamp'])
            prices_asset2['merge_key'] = get_merge_key(prices_asset2['timestamp'])

            # Perform an inner join on the merge key to ensure matching rows
            merged_prices = pd.merge(prices_asset1, prices_asset2, on='merge_key', suffixes=('_asset1', '_asset2'), how='inner')

            if not merged_prices.empty:
                # Calculate price ratios using aligned data from the merged DataFrame
                price_ratios = merged_prices['close_asset1'] / merged_prices['close_asset2']
                z_scores = zscore(price_ratios)

                for i, z_score in enumerate(z_scores):
                    timestamp = merged_prices.iloc[i]['timestamp_asset1']  # Use the timestamp from asset1
                    position = positions[symbol_pair]

                    if not position['open'] and z_score < -threshold:
                        entry_ask_price = merged_prices.iloc[i]['ask_asset1']
                        if entry_ask_price > 0:
                            position['open'] = True
                            position['entry_price'] = entry_ask_price
                            position['lots'] = position_size / entry_ask_price
                            signals_list.append({
                                'Pair': symbol_pair, 'Timestamp': timestamp, 'Action': 'Open Position',
                                'Z-Score': z_score, 'Strategy': 'One-sided', 'Price': entry_ask_price, 'Lots': position['lots'], 'Gross PnL': '', 'Net PnL': '',
                                'Cumulative Gross PnL': global_gross_cum_pnl, 'Cumulative Net PnL': global_net_cum_pnl
                            })

                    elif position['open']:
                        exit_bid_price = merged_prices.iloc[i]['bid_asset1']
                        change_percentage = (exit_bid_price - position['entry_price']) / position['entry_price']
                        if change_percentage <= -stop_loss_limit or change_percentage >= profit_limit:
                            position['open'] = False
                            gross_pnl = position['lots'] * (exit_bid_price - position['entry_price'])
                            net_pnl = gross_pnl - maker_fee * position_size
                            global_gross_cum_pnl += gross_pnl
                            global_net_cum_pnl += net_pnl
                            action = 'Closed with Stop Loss' if change_percentage <= -stop_loss_limit else 'Closed with Profit'
                            signals_list.append({
                                'Pair': symbol_pair, 'Timestamp': timestamp, 'Action': action,
                                'Z-Score': z_score, 'Strategy': 'One-sided', 'Price': exit_bid_price, 'Gross PnL': gross_pnl, 'Net PnL': net_pnl,
                                'Cumulative Gross PnL': global_gross_cum_pnl, 'Cumulative Net PnL': global_net_cum_pnl
                            })
            else:
                print(f"No matching timestamps found for pair {symbol_pair}")
        except Exception as e:
            print(f"Error processing {symbol_pair}: {e}")
    return pd.DataFrame(signals_list)

def get_correlation_pairs(returns):
    # Compute the correlation matrix
    correlation_matrix = returns.corr()

    # Flatten the correlation matrix and reset index
    corr_pairs = correlation_matrix.unstack().reset_index()

    # Rename columns for clarity
    corr_pairs.columns = ['Asset1', 'Asset2', 'Correlation']

    # Remove self-correlation
    corr_pairs = corr_pairs[corr_pairs['Asset1'] != corr_pairs['Asset2']]

    # Filter out duplicate pairs by ensuring Asset1 < Asset2
    corr_pairs = corr_pairs[corr_pairs['Asset1'] < corr_pairs['Asset2']]

    # Sort by absolute correlation values
    corr_pairs['Absolute Correlation'] = corr_pairs['Correlation'].abs()
    sorted_pairs = corr_pairs.sort_values(by='Absolute Correlation', ascending=False)

    return sorted_pairs[['Asset1', 'Asset2', 'Correlation']]

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
    
