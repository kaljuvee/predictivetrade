import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import ccxt
from plotly.subplots import make_subplots
import numpy as np
import plotly.express as px
from util import exchange_util, plot_util, backtest_util

title = "Statistical Arbitrage Research"
st.set_page_config(page_title=title)
st.title(title)

st.markdown("""
This tool is identifying trade entry / exit signals based on the basic statistical arbitrage technique. 
Read more about [statistical arbitrage with pairs trading and backtesting](https://medium.com/analytics-vidhya/statistical-arbitrage-with-pairs-trading-and-backtesting-ec657b25a368).
""")

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
    
# Fetch available symbols
exchange_options = ['bitstamp', 'poloniex', 'kraken', 'binance']
asset_options = [10, 15, 20, 25, 30]
treshold_options = [2.5, 2, 1.5, 1, 0.5]
position_options = [10000, 20000, 50000, 100000]
stop_loss_options = [0.5, 1.0, 1.5, 2.0]
profit_options = [1.0, 1.5, 2.0, 2.5]

selected_exchange = st.selectbox("Select Exchange:", exchange_options)
selected_assets = st.selectbox("Number of initial assets:", asset_options)
selected_treshold = st.selectbox("Select backtest z-score treshold:", treshold_options)
selected_position = st.selectbox("Select position size (USD) for backtest:", position_options)
selected_stop = st.selectbox("Select stop loss limit (%) for backtest:", stop_loss_options)
selected_profit = st.selectbox("Select profit limit (%) for backtest:", profit_options)

top_coins = exchange_util.get_top_coins_by_volume(selected_exchange, selected_assets)
st.write('Top symbols by volume: ', top_coins)
# Fetch and display available symbols based on selected exchange
available_symbols, error_message = exchange_util.get_symbols_usd(selected_exchange)
st.write('All available symbols: ', available_symbols)

if available_symbols:
    selected_symbols = st.multiselect("Select symbols to download", available_symbols, default = available_symbols[:selected_assets])
    st.session_state.symbols = selected_symbols
else:
    st.error(f"Failed to load symbols from {selected_exchange}: {error_message}")

selected_timeframe = st.selectbox("Select Timeframe", ["1m", "5m", "15m", "30m", "1h", "6h", "12h", "1d", "1w"])

# Initialize session state for data
if 'data' not in st.session_state:
    st.session_state.data = None

# Download data button
if st.button('Download Data'):
    if selected_symbols and selected_timeframe:
        st.session_state.data = exchange_util.get_prices(selected_exchange, selected_symbols, selected_timeframe)
        st.write('Price data: ', st.session_state.data)
        st.write('Price data dimensions (rows, columns): ', st.session_state.data.shape)
        st.success("Data downloaded successfully!")
    else:
        st.warning("Please select at least one symbol and a timeframe.")

# Plot prices button
if st.button('Plot Prices') and st.session_state.data is not None:
    plot_util.plot_prices(st.session_state.data, st.session_state.symbols)

# Plot returns button
if st.button('Plot Returns') and st.session_state.data is not None:
    returns = plot_util.plot_returns(st.session_state.data)
    st.session_state.returns = returns
    st.write('Return data: ', st.session_state.returns)
    st.write('Return data dimensions (rows, columns): ', st.session_state.returns.shape)
    
# Correlations button
if st.button('Correlations') and st.session_state.data is not None:
    pairs = plot_util.plot_correlations(st.session_state.returns)
    st.session_state.pairs = pairs
    
if 'page' not in st.session_state:
    st.session_state.page = 0

# Display the z-scores for the current page
if st.button('Display All Spreads') and st.session_state.pairs is not None:
    plot_util.plot_all_zscores(st.session_state.data, st.session_state.pairs, st.session_state.page)

# Setup for paging
pairs_per_page = 5
if st.session_state.pairs is not None:
    num_pages = len(st.session_state.pairs) // pairs_per_page + (len(st.session_state.pairs) % pairs_per_page != 0)

    # Previous and Next buttons for paging
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Previous'):
            if st.session_state.page > 0:
                st.session_state.page -= 1

    with col2:
        if st.button('Next'):
            if st.session_state.page < num_pages - 1:
                st.session_state.page += 1

    # Update the display based on new page number
    if st.session_state.page_changed:
        plot_util.plot_all_zscores(st.session_state.data, st.session_state.pairs, st.session_state.page)
        st.session_state.page_changed = False
        
# Backtest button
if st.button('Backtest') and st.session_state.data is not None:
    signals = backtest_util.backtest_zscores(st.session_state.data,  st.session_state.pairs, selected_treshold, selected_position, selected_stop, selected_profit)
    st.write('Backtest signals: ', signals)
    #backtest_util.perform_backtest(st.session_state.data, st.session_state.pairs)


# Cointegration button
if st.button('Cointegration') and st.session_state.data is not None:
    coint_pairs = plot_util.plot_cointegration_heatmap(st.session_state.returns)
    st.session_state.coint_pairs = coint_pairs
