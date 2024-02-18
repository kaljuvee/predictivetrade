import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from news.util import db_util
import plotly.express as px

st.title("Equities Event Analytics")

st.subheader('Event Prediction Accuracy Levels by Event Type')

def get_alpha_std(df):
    # Assuming 'subject' and 'daily_alpha' are columns in your DataFrame
    alpha_stdev_df = df.groupby('topic')['daily_alpha'].std().reset_index()
    alpha_stdev_df.rename(columns={'daily_alpha': 'alpha_std'}, inplace=True)

    # Create a bar chart
    fig = px.bar(alpha_stdev_df, x='topic', y='alpha_std',
                 title='Standard Deviation of Daily Alpha by Topic Category',
                 labels={'alpha_std': 'Standard Deviation of Daily Alpha', 'topic': 'Topic Category'},
                 color='alpha_std',
                 color_continuous_scale=px.colors.sequential.Viridis)

    fig.update_layout(xaxis={'categoryorder': 'total descending'}, xaxis_title='Topic Category', yaxis_title='Standard Deviation of Daily Alpha')
    return fig

def get_alpha_mean(df):
    # Assuming 'subject' and 'daily_alpha' are columns in your DataFrame
    alpha_stdev_df = df.groupby('topic')['daily_alpha'].mean().reset_index()
    alpha_stdev_df.rename(columns={'daily_alpha': 'alpha_std'}, inplace=True)

    # Create a bar chart
    fig = px.bar(alpha_stdev_df, x='topic', y='alpha_std',
                 title='Average of Daily Alpha by Topic Category',
                 labels={'alpha_std': 'Averageof Daily Alpha', 'topic': 'Topic Category'},
                 color='alpha_std',
                 color_continuous_scale=px.colors.sequential.Viridis)

    fig.update_layout(xaxis={'categoryorder': 'total descending'}, xaxis_title='Topic Category', yaxis_title='Average of Daily Alpha')
    return fig

def get_daily_alpha(prediction_df):
    # Create a frequency distribution bar chart for the percentage daily_alpha values
    fig = px.histogram(prediction_df, x='percent_daily_alpha', nbins=50, title='Frequency Distribution of Daily Alpha (%)')

    # Update the layout for clarity, including more detailed tick labels
    fig.update_layout(
        xaxis_title='Daily Alpha (%)',
        yaxis_title='Count',
        bargap=0.2,
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=5  # Set the interval between ticks to 5%
        )
    )
    return fig

model_df = pd.read_csv('news/models/model_results.csv')
model_df.rename(columns={'accuracy': 'accuracy_pct'}, inplace=True)
model_df['accuracy_pct'] = 100 * model_df['accuracy_pct']
st.write(model_df)

prediction_df = db_util.read_news_price()

# Assuming filtered_news_price_df['daily_alpha'] contains the original daily alpha values

# Create a new column for percentage daily_alpha values
prediction_df['percent_daily_alpha'] = 100 * prediction_df['daily_alpha']

st.subheader('Average Outperformance (Alpha) by Event Type')

fig = get_alpha_mean(prediction_df)
st.plotly_chart(fig)

st.subheader('Standard Deviation of Outperformance (Alpha) by Event Type')

fig = get_alpha_std(prediction_df)
st.plotly_chart(fig)

