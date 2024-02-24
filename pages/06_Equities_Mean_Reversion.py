import streamlit as st
import vectorbt as vbt
import pandas as pd

st.title('Mean Reversion Strategy Backtesting')

def fetch_data(stocks, start_date, end_date):
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_timestamp = pd.to_datetime(start_date_str).tz_localize('UTC')
    end_timestamp = pd.to_datetime(end_date_str).tz_localize('UTC')
    data = vbt.YFData.download(stocks, start=start_timestamp, end=end_timestamp).get('Close')
    if isinstance(data, pd.Series):
        data = data.to_frame()
    return data

def generate_signals(stock_data):
    daily_returns = stock_data.pct_change()
    buy_signals = daily_returns < -0.01
    return buy_signals, pd.DataFrame(False, index=buy_signals.index, columns=buy_signals.columns)

def backtest_strategy(stock_data, buy_signals, sell_signals):
    return vbt.Portfolio.from_signals(stock_data, buy_signals, sell_signals, init_cash=10000, freq='1D')

selected_stocks = st.multiselect('Select Stocks', ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'], default=['AAPL'])
start_date = st.date_input('Start Date', value=pd.to_datetime('2023-01-01'))
end_date = st.date_input('End Date', value=pd.to_datetime('2024-01-01'))

if st.button('Run Backtest'):
    with st.spinner('Backtesting in progress...'):
        def run_backtest(stocks, start_date, end_date):
            try:
                stock_data = fetch_data(stocks, start_date, end_date)
                benchmark_data = fetch_data(['SPY'], start_date, end_date)

                if 'SPY' in benchmark_data.columns:
                    benchmark_data = benchmark_data['SPY']
                else:
                    if benchmark_data.empty or len(benchmark_data.columns) != 1:
                        raise ValueError("Fetched benchmark data is not in the expected format.")
                    benchmark_data = benchmark_data.iloc[:, 0]

                buy_signals, sell_signals = generate_signals(stock_data)
                portfolio = backtest_strategy(stock_data, buy_signals, sell_signals)

                benchmark_returns = (1 + benchmark_data.pct_change()).cumprod() - 1
                benchmark_returns.name = 'SPY Benchmark'

                # Plot strategy cumulative returns and get the figure object
                fig = portfolio.cumulative_returns().vbt.plot()
                
                # Plot benchmark cumulative returns on the same figure
                benchmark_returns.vbt.plot(fig=fig)

                # Use Streamlit to display the figure
                st.plotly_chart(fig, use_container_width=True)

                # Display performance summary
                st.write(portfolio.stats())
            except Exception as e:
                st.error(f"An error occurred during backtesting: {e}")

        run_backtest(selected_stocks, start_date, end_date)