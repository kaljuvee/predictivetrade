import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import ccxt
from plotly.subplots import make_subplots
import numpy as np
import plotly.express as px
from util import exchange_util, plot_util, backtest_util

title = "Sector Analysis"
st.set_page_config(page_title=title)
st.title(title)

st.markdown("""
## Top Biotech ETFs

* **iShares Nasdaq Biotechnology ETF (IBB)** - one of the largest biotech ETFs, **IBB** tracks the NASDAQ Biotechnology Index and includes stocks of biotechnology and pharmaceutical companies listed on the NASDAQ.

* **SPDR S&P Biotech ETF (XBI)** - this ETF seeks to track the S&P Biotechnology Select Industry Index, which represents the biotechnology sub-industry portion of the S&P Total Markets Index. **XBI** is known for its equal-weighted approach, giving more weight to smaller companies compared to market cap-weighted ETFs.

* **First Trust NYSE Arca Biotechnology Index Fund (FBT)** - **FBT** seeks to track the investment results of the NYSE Arca Biotechnology Index, which includes companies involved in the research, development, manufacturing, and distribution of various biotechnological products.

* **VanEck Vectors Biotech ETF (BBH)** - **BBH** aims to replicate the performance of the MVIS US Listed Biotech 25 Index, which tracks the overall performance of companies involved in the development and production, marketing, and sales of drugs based on genetic analysis and diagnostic equipment.

* **ARK Genomic Revolution ETF (ARKG)** - while not exclusively a biotech ETF, **ARKG** focuses on companies likely to benefit from extending and enhancing the quality of human and other life by incorporating technological and scientific developments, including innovations in genomics.
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
    
# Fetch and display available symbols based on 
# Fetch available symbols
sector_options = ['biotech']

selected_exchange = st.selectbox("Select sector:", sector_options)
available_symbols = exchange_util.biotech_symbols
st.write(f'All available symbols in {selected_exchange}: ', available_symbols)

default_symbols = ['XBI', 'IBB', 'FBT', 'BBH', 'ARKG']

if available_symbols:
    selected_symbols = st.multiselect("Select symbols to download", available_symbols, default = default_symbols)
    st.session_state.symbols = selected_symbols
else:
    st.error(f"Failed to load symbols")

selected_benchmark = st.selectbox("Select ETF benchmark::", ['XBI', 'IBB', 'FBT', 'BBH', 'ARKG'])
selected_interval = st.selectbox("Select tick interval:", ["1m", "5m", "15m", "30m", "1h", "6h", "12h", "1d", "1w"])
selected_timeframe = st.slider("Select lookback window: (days)", min_value=1, max_value=30, value=1, step=1)

# Initialize session state for data
if 'data' not in st.session_state:
    st.session_state.data = None



# Download data button
if st.button('Download Prices'):
    if selected_symbols and selected_timeframe:
        st.session_state.data = exchange_util.get_prices_yfinance(selected_symbols, selected_interval, selected_timeframe)
        st.write('Price data: ', st.session_state.data)
        st.write('Price data dimensions (rows, columns): ', st.session_state.data.shape)
        st.success("Data downloaded successfully!")
    else:
        st.warning("Please select at least one symbol and a timeframe.")

# Plot prices button
if st.button('Plot Prices') and st.session_state.data is not None:
    plot_util.plot_prices(st.session_state.data, st.session_state.symbols, selected_benchmark)

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

# Cointegration button
if st.button('Cointegration') and st.session_state.data is not None:
    coint_pairs = plot_util.plot_cointegration_heatmap(st.session_state.returns)
    st.session_state.coint_pairs = coint_pairs