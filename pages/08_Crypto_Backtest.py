import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import ccxt
from plotly.subplots import make_subplots
import numpy as np
import plotly.express as px
from util import exchange_util, plot_util, backtest_util, db_util

title = "Crypto Backtest"
st.set_page_config(page_title=title)
st.title(title)


st.markdown("""
This tool is identifying trade entry / exit signals based on the basic statistical arbitrage technique. 
Read more about [statistical arbitrage with pairs trading and backtesting](https://medium.com/analytics-vidhya/statistical-arbitrage-with-pairs-trading-and-backtesting-ec657b25a368).
""")

def get_default_symbols(selected_exchange):
    # Fetch default symbols from the database
    available_symbols = db_util.get_symbols(selected_exchange)

    # Fetch all available symbols from the selected exchange
    all_symbols, error_message = exchange_util.get_symbols_usd(selected_exchange)

    if all_symbols:
        # Ensure default symbols are a subset of available symbols
        valid_available_symbols = [symbol for symbol in available_symbols if symbol in all_symbols]
    else:
        # Handle the case where fetching available symbols failed
        st.error(f"Failed to load symbols from {selected_exchange}: {error_message}")
        valid_stored_symbols = []
    return valid_available_symbols, all_symbols, error_message
    
# Initialize session state variables
if 'data' not in st.session_state:
    st.session_state.data = None
if 'pairs' not in st.session_state:
    st.session_state.pairs = None
if 'page_changed' not in st.session_state:
    st.session_state.page_changed = None
if 'symbols' not in st.session_state:
    st.session_state.symbols = None
if 'returns' not in st.session_state:
    st.session_state.returns = None
if 'exchange' not in st.session_state:
    st.session_state.exchange = None
        
# Fetch available symbols
exchange_options = ['bitstamp', 'poloniex', 'kraken', 'binance']
asset_options = [10, 15, 20, 25, 30]
position_options = [10000, 20000, 50000, 100000]
treshold_options = [0.5, 1, 1.5, 2, 2.5]
stop_loss_options = [0.5, 1.0, 1.5, 2.0]
profit_options = [0.5, 1.0, 1.5, 2.0, 2.5]

selected_exchange = st.selectbox("Select Exchange:", exchange_options)
selected_assets = st.selectbox("Number of initial assets:", asset_options)
selected_position = st.selectbox("Select position size (USD) for backtest:", position_options)
selected_treshold = st.selectbox("Select backtest z-score treshold for the **entry signal**:", treshold_options)

# Use st.number_input for stop loss and profit limit
selected_stop = st.number_input("Select stop loss limit (%) for backtest **exit signal**:", min_value=0.0, max_value=100.0, value=1.0, step=0.1, format="%.2f")
selected_profit = st.number_input("Select profit limit (%) for backtest **exit signal**:", min_value=0.0, max_value=100.0, value=1.0, step=0.1, format="%.2f")
bid_ask_spread = st.number_input("Bid-Ask Spread (as %)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)
maker_fee = st.number_input("Maker fee (as %)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)

# New select options for number of days and strategy type
selected_days = st.selectbox("Select number of days to backtest:", [1, 2, 3, 4, 5])
selected_strategy = st.selectbox("Select strategy:", ["One-sided", "Two-sided"])
# Option to choose whether to reinvest profits
reinvest_profits = st.selectbox("Reinvest profits:", [True, False])

top_coins = exchange_util.get_top_coins_by_volume(selected_exchange, selected_assets)

# Fetch and display available symbols based on selected exchange
available_symbols, all_symbols, error_message = get_default_symbols(selected_exchange)
default_symbols = ['BTC/USD', 'ETH/USD']

if default_symbols:
    selected_symbols = st.multiselect("Select symbols to download", available_symbols, default = default_symbols)
    st.session_state.symbols = selected_symbols
else:
    st.error(f"Failed to load symbols from {selected_exchange}: {error_message}")

selected_timeframe = st.selectbox("Select Timeframe", ["1m", "5m", "15m", "30m", "1h", "6h", "12h", "1d", "1w"])

# Button to calculate bid and ask
if st.button('Get Bid Ask Prices'):
    if not st.session_state.data is not None:
        bid_ask_df = db_util.get_prices(st.session_state.exchange, st.session_state.symbols, selected_timeframe, selected_days)
        #bid_ask_df = db_util.get_bid_ask(st.session_state.exchange, st.session_state.symbols)
        st.session_state.bid_ask = bid_ask_df
        st.write('Exchange: ', st.session_state.exchange)
        st.write('Bid-Ask data dimensions (rows, columns): ', st.session_state.bid_ask.shape)
        st.write('Bid-Ask Data:', st.session_state.bid_ask)
        #pivot = bid_ask_df.pivot_table(index='timestamp', columns='symbol', values=['close', 'bid', 'ask'])
        #st.write('Pivoted Bid-Ask Data:', pivot)
    else:
        st.error("No price data available. Please download price data first.")
        
# Backtest button
if st.button('Backtest') and st.session_state.bid_ask is not None:
    # Choose the backtesting function based on the selected strategy
    run_id = backtest_util.get_run_id()
    if selected_strategy == "One-sided":
        pnl = backtest_util.backtest_zscores_one_sided_bid_ask(
            st.session_state.bid_ask, st.session_state.pairs,
            selected_treshold, selected_position, selected_stop, selected_profit, st.session_state.exchange, run_id, maker_fee, reinvest_profits)
        st.session_state.pnl = pnl     
    elif selected_strategy == "Two-sided":
        pnl = backtest_util.backtest_zscores_one_sided_bid_ask(
            st.session_state.bid_ask, st.session_state.pairs,
            selected_treshold, selected_position, selected_stop, selected_profit, st.session_state.exchange, run_id, maker_fee, reinvest_profits)
        st.session_state.pnl = pnl  
    else:
        st.error("Invalid strategy selected.")
        signals = None

    # Display the backtest signals, if any
    if pnl is not None:
        st.write('Backtest PnL: ', pnl)
        # plot_util.plot_equity_line(pnl)
    else:
        st.write("No PnL generated. Please check your input parameters and strategy selection.")

# Backtest button
if st.button('Store PnL') and st.session_state.pnl is not None:
    db_util.write_pnl(st.session_state.pnl )
    st.success("Backtest PnL saved successfully.")

# Plot returns button
if st.button('Correlations') and st.session_state.data is not None:
    returns = backtest_util.calculate_returns(st.session_state.data)
    st.session_state.returns = returns
    st.write('Return data: ', st.session_state.returns)
    st.write('Return data dimensions (rows, columns): ', st.session_state.returns.shape)
    corr_pairs = backtest_util.get_correlation_pairs(st.session_state.returns)
    st.write('Correlation pairs: ', corr_pairs) 

# Correlations button
if st.button('Get Pairs') and st.session_state.data is not None:
    pairs = backtest_util.get_pairs( st.session_state.symbols)
    st.session_state.pairs = pairs
    st.write('Symbol pairs: ', st.session_state.pairs) 

if st.button('Show Available Symbols'):
    st.write('Top symbols by volume: ', top_coins)
    st.write('All available symbols: ', available_symbols)

