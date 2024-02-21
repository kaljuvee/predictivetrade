import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from news.util import db_util
import plotly.express as px

st.title("Equities Event Analytics")

st.subheader('Event Prediction Accuracy Levels by Event Type')

import pandas as pd
import plotly.figure_factory as ff
from sklearn.metrics import confusion_matrix

def display_frequency(df, hour_column):
    """
    Displays a frequency chart for the given DataFrame and hour column.

    Parameters:
    - df: DataFrame containing the data
    - hour_column: String name of the column representing the hour of day
    """
    # Create a frequency count of occurrences per specified hour column
    hourly_counts = df[hour_column].value_counts().reset_index()
    hourly_counts.columns = [hour_column, 'counts']

    # Create the frequency chart using Plotly
    fig = px.bar(hourly_counts, x=hour_column, y='counts',
                 labels={hour_column: 'Hour of Day', 'counts': 'Counts'},
                 title='Frequency Chart by Hour of Day',
                 template="plotly_white")  # Using a white background for better readability

    # Show the figure
    return fig

def get_confusion_matrix(data, actual_col, predicted_col):
    """
    Generates a 2x2 confusion matrix plot for the given DataFrame.

    Parameters:
    - data: pd.DataFrame containing the dataset.
    - actual_col: str, the name of the column with actual values.
    - predicted_col: str, the name of the column with predicted values.

    Returns:
    - A Plotly figure object representing the 2x2 confusion matrix.
    """
    # Remove rows where actual or predicted values are null
    cleaned_data = data.dropna(subset=[actual_col, predicted_col])

    # Determine the top 2 categories in actual and predicted columns
    top_actual_actions = cleaned_data[actual_col].value_counts().nlargest(2).index
    top_predicted_actions = cleaned_data[predicted_col].value_counts().nlargest(2).index

    # Filter data to include only the top 2 categories from both actual and predicted columns
    filtered_data = cleaned_data[(cleaned_data[actual_col].isin(top_actual_actions)) & (cleaned_data[predicted_col].isin(top_predicted_actions))]

    # Calculate the 2x2 confusion matrix
    cm_2x2 = confusion_matrix(filtered_data[actual_col], filtered_data[predicted_col], labels=top_actual_actions)

    # Create a Plotly figure for the 2x2 confusion matrix
    fig_2x2 = ff.create_annotated_heatmap(z=cm_2x2, x=list(top_predicted_actions), y=list(top_actual_actions), colorscale='Blues', annotation_text=cm_2x2)

    # Update layout
    fig_2x2.update_layout(xaxis=dict(title='Predicted Actions'),
                          yaxis=dict(title='Actual Actions'))

    return fig_2x2

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

st.subheader('Confusion Matrix for Actual vs. Predicted Actions')

fig = get_confusion_matrix(prediction_df, 'actual_action', 'predicted_action')
st.plotly_chart(fig)

st.subheader('Event Frequency by Hour of Day')
news_df = db_util.get_news_all()
fig = display_frequency(news_df, 'hour_of_day')
st.plotly_chart(fig)
