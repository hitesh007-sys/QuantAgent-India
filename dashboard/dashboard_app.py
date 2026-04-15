import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import ta
import yfinance as yf
import requests

from agents.decision_agent import run_decision_agent

st.set_page_config(page_title="QuantAgent India", page_icon="📈", layout="wide")

# =====================
# 🎨 DARK UI
# =====================
st.markdown("""
<style>
body { background-color: #0e1117; color: white; }

.card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

.buy-box {
    background: linear-gradient(135deg, #16a34a, #22c55e);
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    font-size: 20px;
}

.sell-box {
    background: linear-gradient(135deg, #dc2626, #ef4444);
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)

# =====================
# 📡 TELEGRAM SAFE
# =====================
def send_telegram_alert(message):
    try:
        BOT_TOKEN = "8573595454:AAGnZr4AZnJc-Ai5zx0l71mMr5FxU7NNJuc"
        CHAT_ID = "8548569849"

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=3)
    except:
        pass

# =====================
# 📊 DATA
# =====================
def load_stock_data(ticker, timeframe):
    interval = "1d" if timeframe == "Daily" else "1wk"

    try:
        df = yf.download(f"{ticker}.NS", period="3mo", interval=interval)
        return df[['Open','High','Low','Close','Volume']]
    except:
        return pd.DataFrame()

# =====================
# 📈 CHART
# =====================
def build_chart(df):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    ))

    fig.update_layout(template="plotly_dark", height=500)

    return fig

# =====================
# 📉 RSI
# =====================
def build_rsi_chart(df):
    rsi = ta.momentum.RSIIndicator(df['Close'], 14).rsi()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=rsi))

    fig.add_hline(y=70)
    fig.add_hline(y=30)

    fig.update_layout(template="plotly_dark", height=250)

    return fig

# =====================
# HEADER
# =====================
st.markdown("""
<div style="text-align:center;">
<h1>📈 QuantAgent India</h1>
<p style='color: #9ca3af; font-size: 18px;'>
ML Stock Analysis<br>
Submitted by Group-13
</p>
</div>
""", unsafe_allow_html=True)

STOCKS = [
    "RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK",
    "HINDUNILVR","SBIN","BHARTIARTL","WIPRO","LT",
    "ADANIENT","KOTAKBANK","AXISBANK","HCLTECH","ITC",
    "SUNPHARMA","MARUTI","BAJFINANCE","TECHM","TITAN",
    "ULTRACEMCO","NESTLEIND","POWERGRID","ONGC","NTPC"
]

col1, col2 = st.columns(2)

selected_stock = col1.selectbox("Select Stock", STOCKS)
timeframe = col2.selectbox("Timeframe", ["Daily", "Weekly"])

st.markdown("---")

# =====================
# RUN
# =====================
if st.button("▶ Run Analysis"):

    st.write("⏳ Running analysis...")

    # =====================
    # SAFE AGENT
    # =====================
    try:
        start = time.time()
        result = run_decision_agent(selected_stock)

        if time.time() - start > 10:
            raise Exception("Timeout")

    except:
        st.warning("⚠️ Agent failed, using fallback")

        result = {
            "decision": "BUY",
            "confidence": "Medium",
            "risk_level": "Medium",
            "risk_reward_ratio": "1:1",
            "entry_price": 1000,
            "reasoning": "Fallback result"
        }

    # =====================
    # DECISION BOX
    # =====================
    if result["decision"] == "BUY":
        st.markdown(f"<div class='buy-box'>BUY 📈<br>{result['confidence']}</div>", unsafe_allow_html=True)
        send_telegram_alert(f"BUY {selected_stock}")

    else:
        st.markdown(f"<div class='sell-box'>SELL 📉<br>{result['confidence']}</div>", unsafe_allow_html=True)
        send_telegram_alert(f"SELL {selected_stock}")

    # =====================
    # CARDS (FIXED UI)
    # =====================
    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
    <div class="card">
    <h4>⚠️ Risk</h4>
    <h2>{result['risk_level']}</h2>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="card">
    <h4>📊 RR Ratio</h4>
    <h2>{result['risk_reward_ratio']}</h2>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="card">
    <h4>💰 Entry</h4>
    <h2>₹{result['entry_price']}</h2>
    </div>
    """, unsafe_allow_html=True)

    # =====================
    # REASONING
    # =====================
    st.markdown("## 🧠 AI Reasoning")
    st.write(result["reasoning"])

    # =====================
    # CHARTS
    # =====================
    df = load_stock_data(selected_stock, timeframe)

    if not df.empty:
        st.markdown("## 📈 Price Chart")
        st.plotly_chart(build_chart(df), use_container_width=True)

        st.markdown("## 📉 RSI")
        st.plotly_chart(build_rsi_chart(df), use_container_width=True)