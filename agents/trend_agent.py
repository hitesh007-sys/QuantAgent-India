import os
import sys
import numpy as np
import pandas as pd
sys.path.append('tools')

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Safe API Key Fetching
try:
    import streamlit as st
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)


def load_clean_data(ticker_name: str, n_bars: int = 40) -> pd.DataFrame:
    """Load and clean stock data."""
    path = f"data/{ticker_name}_daily.csv"
    df = pd.read_csv(path)

    if df.iloc[0].astype(str).str.contains('Ticker|Price|RELIANCE|TCS').any():
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
    return df.tail(n_bars)


def compute_trendlines(ticker_name: str, n_bars: int = 40) -> dict:
    """
    Computes support and resistance trendlines using OLS regression.
    """
    df = load_clean_data(ticker_name, n_bars)

    x      = np.arange(len(df))
    highs  = df["High"].values
    lows   = df["Low"].values
    closes = df["Close"].values

    mr, br = np.polyfit(x, highs, 1)
    ms, bs = np.polyfit(x, lows, 1)

    kappa = (mr + ms) / 2

    if kappa > 0.001:
        trend = "Uptrend"
    elif kappa < -0.001:
        trend = "Downtrend"
    else:
        trend = "Sideways"

    last_idx     = len(df) - 1
    support_val  = round(float(ms * last_idx + bs), 2)
    resist_val   = round(float(mr * last_idx + br), 2)
    current_price = round(float(closes[-1]), 2)

    near_support  = abs(current_price - support_val) / current_price < 0.02
    near_resist   = abs(current_price - resist_val) / current_price < 0.02

    gap_start = float((mr * 0 + br) - (ms * 0 + bs))
    gap_end   = float((mr * last_idx + br) - (ms * last_idx + bs))
    converging = gap_end < gap_start * 0.7

    return {
        "trend":          trend,
        "slope":          round(float(kappa), 6),
        "support":        support_val,
        "resistance":     resist_val,
        "current_price":  current_price,
        "near_support":   near_support,
        "near_resistance": near_resist,
        "converging":     converging
    }


def analyze_trend(ticker_name: str) -> str:
    """
    Analyzes trend using Groq LLM.
    """
    trend_data = compute_trendlines(ticker_name)

    prompt = f"""
You are an expert stock trend analyst for Indian markets.

Here is the trend data for {ticker_name}:
- Current Price: {trend_data['current_price']}
- Trend Direction: {trend_data['trend']}
- Slope: {trend_data['slope']}
- Support Level: {trend_data['support']}
- Resistance Level: {trend_data['resistance']}
- Price near Support: {trend_data['near_support']}
- Price near Resistance: {trend_data['near_resistance']}
- Trendlines Converging: {trend_data['converging']}

Based on this data:
1. What is the current trend strength?
2. Is price likely to bounce or break through support/resistance?
3. What should a trader watch for?

Reply in 3 short sentences. Be specific and clear.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()