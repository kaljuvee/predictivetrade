import streamlit as st
import pandas as pd
import plotly.figure_factory as ff

# List of tickers for the axes of the correlation matrix
tickers = [
    "USDT-USD.CC",
    "BNB-USD.CC",
    "SOL-USD.CC",
    "XRP-USD.CC",
    "USDC-USD.CC",
    "ADA-USD.CC",
    "AVAX-USD.CC",
    "DOGE-USD.CC",
    "TRX-USD.CC",
    "DOT-USD.CC",
    "LINK-USD.CC",
    "TON-USD.CC",
    "MATIC-USD.CC",
    "SHIB-USD.CC",
    "ICP-USD.CC",
    "DAI-USD.CC",
    "LTC-USD.CC",
    "BCH-USD.CC",
    "UNI-USD.CC"
]

# Streamlit code to upload CSV file and calculate correlation matrix
st.title('Cryptocurrency Returns Correlation Matrix')

# File uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    df = pd.read_csv(uploaded_file)
    # Filter the dataframe to only include the specified tickers
    df_filtered = df[df['ticker'].isin(tickers)]
    
    # Pivot the DataFrame to have tickers as columns and 'Datetime' as index
    df_pivot = df_filtered.pivot(index='Datetime', columns='ticker', values='price_change')
    
    # Calculate the correlation matrix
    corr_matrix = df_pivot.corr()
    
    # Display the correlation matrix
    st.write('Correlation Matrix:')
    st.dataframe(corr_matrix)
    
    # Create a heatmap using Plotly
    st.write('Heatmap of Correlation Matrix:')
    fig = ff.create_annotated_heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.columns.tolist(),
        annotation_text=corr_matrix.round(2).values,
        showscale=True
    )
    st.plotly_chart(fig, use_container_width=True)
