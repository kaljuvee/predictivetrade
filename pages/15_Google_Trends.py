import streamlit as st
from pytrends.request import TrendReq
import plotly.express as px
import pandas as pd
import yfinance as yf

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=360)

def load_data(keyword, start_date, end_date, frequency):
    try:
        pytrends.build_payload([keyword], cat=0, timeframe=f'{start_date} {end_date}', geo='', gprop='')
        data = pytrends.interest_over_time()

        if not data.empty:
            data = data.drop(labels=['isPartial'], axis='columns')
            # Handle frequency conversion
            if frequency == 'daily':
                data = data.asfreq('D', method='pad')
            elif frequency == 'weekly':
                # Resample to weekly frequency
                data = data.resample('W').mean()
            elif frequency == 'monthly':
                data = data.asfreq('M', method='pad')
            return data
        else:
            return pd.DataFrame()

    except KeyError as e:
        st.error(f"An error occurred while fetching the data: {e}")
        return pd.DataFrame()

    except ValueError as e:
        st.error(f"An error occurred with the frequency selection: {e}")
        return pd.DataFrame()

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

def normalize_data(data):
    # Normalize the data to a 0-100 scale
    return (data - data.min()) / (data.max() - data.min()) * 100

def get_price_data(ticker, start_date, end_date, frequency):
    # Fetch historical market data
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if not data.empty:
        # Adjust frequency if needed
        if frequency == 'weekly':
            data = data.resample('W').mean()  # Use mean for weekly aggregation
        elif frequency == 'monthly':
            data = data.resample('M').mean()  # Use mean for monthly aggregation
        
        # Normalize the 'Adj Close' column
        normalized_data = normalize_data(data['Adj Close'])
        
        return normalized_data
    else:
        return pd.DataFrame()

def plot_trends(trends_data, price_data, keyword, ticker):
    # Create a Plotly graph with Google Trends data
    fig = px.line(trends_data, y=keyword, title=f'Google Trends vs. Stock Price for "{keyword}" and "{ticker}"')
    
    # Update the legend name for Google Trends data
    fig.data[0].name = f'Google Trends: {keyword}'
    fig.data[0].showlegend = True

    # Add price data to the plot and update the legend name for Stock Price data
    fig.add_scatter(x=price_data.index, y=price_data, mode='lines', name=f'Stock Price: {ticker}')
    
    # Update layout options if necessary
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Normalized Scale (0-100)',
        legend_title='Data Source'
    )
    
    st.plotly_chart(fig)


def main():
    # Streamlit app title and user inputs
    st.title('Google Trends and Stock Price Data Visualization')
    term = st.text_input('Enter a Google Trends term:')
    ticker = st.text_input('Enter a Stock Ticker:')
    start_date = st.date_input('Start Date')
    end_date = st.date_input('End Date')
    frequency = st.selectbox('Select Frequency:', ['daily', 'weekly', 'monthly'])

    if st.button('Search'):
        trends_data = load_data(term, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), frequency)
        price_data = get_price_data(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), frequency)
        
        if not trends_data.empty and not price_data.empty:
            plot_trends(trends_data, price_data, term, ticker)
        else:
            st.write("No data available for the entered term or ticker.")

if __name__ == "__main__":
    main()
