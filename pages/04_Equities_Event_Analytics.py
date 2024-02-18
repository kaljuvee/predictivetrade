import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from news.util import db_util

st.title("Equities Event Analytics")


df = pd.read_csv('news/models/model_results.csv')
st.write("Latest model runs:", df)
