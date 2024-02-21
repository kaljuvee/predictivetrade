import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import ccxt
from plotly.subplots import make_subplots
import numpy as np
import plotly.express as px
from util import exchange_util, plot_util, backtest_util, db_util, vbt_util
import vectorbt as vbt

title = "Sector Backtest"
st.set_page_config(page_title=title)
st.title(title)

st.markdown("""
## Top Biotech ETFs

* **iShares Nasdaq Biotechnology ETF (IBB)** - one of the largest biotech ETFs, **IBB** tracks the NASDAQ Biotechnology Index and includes stocks of biotechnology and pharmaceutical companies listed on the NASDAQ.

* **SPDR S&P Biotech ETF (XBI)** - this ETF seeks to track the S&P Biotechnology Select Industry Index, which represents the biotechnology sub-industry portion of the S&P Total Markets Index. **XBI** is known for its equal-weighted approach, giving more weight to smaller companies compared to market cap-weighted ETFs.

* **VanEck Vectors Biotech ETF (BBH)** - **BBH** aims to replicate the performance of the MVIS US Listed Biotech 25 Index, which tracks the overall performance of companies involved in the development and production, marketing, and sales of drugs based on genetic analysis and diagnostic equipment.

* **ARK Genomic Revolution ETF (ARKG)** - while not exclusively a biotech ETF, **ARKG** focuses on companies likely to benefit from extending and enhancing the quality of human and other life by incorporating technological and scientific developments, including innovations in genomics.

* **First Trust NYSE Arca Biotechnology Index Fund (FBT)** - **FBT** seeks to track the investment results of the NYSE Arca Biotechnology Index, which includes companies involved in the research, development, manufacturing, and distribution of various biotechnological products.
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
if 'exchange' not in st.session_state:
    st.session_state.exchange = None

# Fetch available symbols
exchange_options = ['biotech']
position_options = [10000, 20000, 50000, 100000]
treshold_options = [0.5, 1, 1.5, 2, 2.5]
stop_loss_options = [0.5, 1.0, 1.5, 2.0]
profit_options = [0.5, 1.0, 1.5, 2.0, 2.5]

selected_exchange = st.selectbox("Select sector:", exchange_options)
selected_position = st.selectbox("Select position size (USD):", position_options)
selected_treshold = st.selectbox("Select **z-score** treshold for the **entry signal**:", treshold_options)

# Use st.number_input for stop loss and profit limit
selected_stop = st.number_input("Select stop loss limit (%) for **exit signal**:", min_value=0.0, max_value=100.0, value=1.0, step=0.1, format="%.2f")
selected_profit = st.number_input("Select profit limit (%) for **exit signal**:", min_value=0.0, max_value=100.0, value=1.0, step=0.1, format="%.2f")
#maker_fee = st.number_input("Maker fee (as %)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)

# New select options for number of days and strategy type
#selected_days = st.selectbox("Select number of days to backtest:", [1, 2, 3, 4, 5])
#selected_strategy = st.selectbox("Select strategy:", ["One-sided", "Two-sided"])
# Option to choose whether to reinvest profits
#reinvest_profits = st.selectbox("Reinvest profits:", [True, False])
selected_benchmark = st.selectbox("Select ETF benchmark::", ['IBB', 'XBI', 'FBT', 'BBH', 'ARKG'])
selected_interval = st.selectbox("Select tick interval:", ["1m", "5m", "15m", "30m", "1h", "6h", "12h", "1d", "1w"])
selected_lookback = st.slider("Select lookback window: (days)", min_value=1, max_value=30, value=1, step=1)

available_symbols = exchange_util.biotech_symbols
st.write('All available symbols: ', available_symbols)
default_symbols = ['IBB', 'XBI', 'BBH', 'ARKG']

if default_symbols:
    selected_symbols = st.multiselect("Select symbols to simulate: ", available_symbols, default = default_symbols)
    st.session_state.symbols = selected_symbols
else:
    st.error(f"Failed to load symbols from {selected_exchange}: {error_message}")

selected_timeframe = st.selectbox("Select **tick interval:**", ["1m", "5m", "15m", "30m", "1h", "6h", "12h", "1d", "1w"])

# Download data button
if st.button('Plot Prices'):
    if selected_symbols and selected_timeframe:
        st.session_state.data = exchange_util.get_prices_yfinance(selected_symbols, selected_interval, selected_lookback)
        # st.write('Price data: ', st.session_state.data)
        plot_util.plot_prices(st.session_state.data, st.session_state.symbols, selected_benchmark)
    else:
        st.warning("Please select at least one symbol and a timeframe.")

# Backtest button
if st.button('Backtest'):
    asset1 = selected_symbols[0]
    asset2 = selected_symbols[1]
    # Display the backtest signals, if any
    position_size = selected_position
    window = 30
    threshold = selected_treshold
    stop_loss_pct = selected_stop
    take_profit_pct = selected_profit
    input_frequency = selected_interval
    lookback_days = selected_lookback
    portfolio = vbt_util.backtest_zscore(asset1, asset2, window, threshold, position_size,
                    stop_loss_pct, take_profit_pct, input_frequency, lookback_days)
    
    if portfolio is not None:
        st.subheader("Backest Summary")
        st.write(portfolio.stats())
        # Extract trades from the portfolio
        trades = portfolio.trades
        # Convert the trades to a DataFrame
        trades_df = trades.records_readable
        trades_df.columns = trades_df.columns.map(lambda x: x.lower().replace(' ', '_'))
        trades_df.rename(columns={'column': 'action'}, inplace=True)
        st.session_state.trades = trades_df
        st.subheader("Trade Detail")
        st.write(trades_df)
        st.subheader("Returns Relative to the Market Benchmark (SPY)")
        cumulative_portfolio_returns, cumulative_benchmark_returns = vbt_util.benchmark_returns(portfolio, benchmark_ticker='SPY')
        st.write('Cumulative backtest returns:', cumulative_portfolio_returns)
        st.write('Cumulative SPY returns:', cumulative_benchmark_returns)
        st.subheader("Equity Line vs Market Benchmark (SPY)")
        fig = plot_util.plot_benchmark_returns(cumulative_portfolio_returns, cumulative_benchmark_returns, benchmark_ticker='SPY')
        st.plotly_chart(fig)
    else:
        st.write("No PnL generated. Please check your input parameters and strategy selection.")

# Backtest button
if st.button('Store PnL') and st.session_state.trades is not None:
    db_util.store(st.session_state.trades, 'vbt_trades')
    st.success("Backtest PnL saved successfully.")