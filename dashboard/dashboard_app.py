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


def build_chart(ticker: str, result: dict) -> go.Figure:
    df = load_stock_data(ticker)
    recent = df.tail(60)

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=recent.index,
        open=recent['Open'],
        high=recent['High'],
        low=recent['Low'],
        close=recent['Close'],
        name='Price',
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444',
        increasing_fillcolor='#10b981',
        decreasing_fillcolor='#ef4444'
    ))

    fig.add_hline(
        y=result['support'],
        line_dash="dash",
        line_color="#10b981",
        line_width=1.5,
    )
    fig.add_hline(
        y=result['resistance'],
        line_dash="dash",
        line_color="#ef4444",
        line_width=1.5,
    )

    return fig


def build_rsi_chart(ticker: str) -> go.Figure:
    df = load_stock_data(ticker)
    recent = df.tail(60)
    rsi_series = ta.momentum.RSIIndicator(
        recent['Close'].squeeze(), window=14
    ).rsi()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=recent.index,
        y=rsi_series,
        line=dict(color='#2563eb', width=2),
        name='RSI'
    ))

    return fig


# =====================
# Sidebar (UNCHANGED UI)
# =====================
with st.sidebar:
    st.markdown("## 📈 QuantAgent")

# =====================
# Main UI (UNCHANGED)
# =====================
st.markdown("""
<div class="header-banner">
    <h1>📈 QuantAgent India</h1>
    <p>Multi-Agent AI Trading System</p>
</div>
""", unsafe_allow_html=True)

STOCKS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "SBIN", "WIPRO", "LT", "ITC", "SUNPHARMA"
]

col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    selected_stock = st.selectbox("Select Stock", STOCKS)

with col2:
    timeframe = st.selectbox("Timeframe", ["Daily", "Weekly"])

with col3:
    run_button = st.button("▶ Run Analysis")

st.markdown("<br>", unsafe_allow_html=True)

# =====================
# MAIN LOGIC (FIXED)
# =====================

if run_button:
    with st.spinner(f"🤖 Running all agents for {selected_stock}..."):
        try:
            # ✅ ADDED DEBUG (important)
            st.write("🚀 Running analysis...")

            result = run_decision_agent(selected_stock)

            st.write("✅ Analysis complete")

            # ===== your UI continues exactly =====
            st.json(result)

            price_chart = build_chart(selected_stock, result)
            st.plotly_chart(price_chart, use_container_width=True)

            rsi_chart = build_rsi_chart(selected_stock)
            st.plotly_chart(rsi_chart, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

            # ✅ FIXED MESSAGE
            st.info("Check Streamlit Secrets → GROQ_API_KEY")

else:
    st.markdown("""
    <div class="welcome-box">
        <h2>Welcome to QuantAgent India 🚀</h2>
        <p>Select a stock and click Run Analysis</p>
    </div>
    """, unsafe_allow_html=True)