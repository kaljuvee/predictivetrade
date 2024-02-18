import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from news.util import db_util

st.title("Equities Event Analytics")


df = db_util.get_latest_model_runs()
st.write("Latest model runs:", df)
