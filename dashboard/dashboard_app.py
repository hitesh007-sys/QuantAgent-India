import sys
import os

# ✅ Fix module path for Streamlit Cloud
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import ta

# ✅ Correct import
from agents.decision_agent import run_decision_agent


# ❌ REMOVE dotenv (not needed in deployment)
# from dotenv import load_dotenv
# load_dotenv()


st.set_page_config(
    page_title="QuantAgent India",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================
# Helper Functions
# =====================
def load_stock_data(ticker_name: str) -> pd.DataFrame:
    path = f"data/{ticker_name}_daily.csv"
    df = pd.read_csv(path)

    if df.iloc[0].astype(str).str.contains(
        'Ticker|Price|RELIANCE|TCS|NS'
    ).any():
        df = df.iloc[1:].reset_index(drop=True)

    df.columns = [c.strip() for c in df.columns]
    first_col = df.columns[0]
    df = df.rename(columns={first_col: 'Date'})
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df = df.set_index('Date')

    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)
    return df


def get_signal(value, indicator):
    if indicator == "RSI":
        if value > 70: return "Overbought", "bearish"
        elif value < 30: return "Oversold", "bullish"
        else: return "Neutral", "neutral"
    elif indicator == "MACD":
        if value > 0: return "Bullish", "bullish"
        else: return "Bearish", "bearish"
    elif indicator == "ROC":
        if value > 0: return "Rising", "bullish"
        else: return "Falling", "bearish"
    elif indicator == "Stoch":
        if value > 80: return "Overbought", "bearish"
        elif value < 20: return "Oversold", "bullish"
        else: return "Neutral", "neutral"
    return "Neutral", "neutral"


# (बाकी पूरा UI code same रहेगा — no need to change anything below)