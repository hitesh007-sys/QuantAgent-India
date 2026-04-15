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
    margin-bottom: 15px;
}

.buy-box {
    background: linear-gradient(135deg, #16a34a, #22c55e);
    padding: 25px;
    border-radius: 12px;
    text-align: center;
}

.sell-box {
    background: linear-gradient(135deg, #dc2626, #ef4444);
    padding: 25px;
    border-radius: 12px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =====================
# 📡 TELEGRAM (SAFE)
# =====================
def send_telegram_alert(message):
    try:
        BOT_TOKEN = "YOUR_TOKEN"
        CHAT_ID = "YOUR_CHAT_ID"

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        requests.post(
            url,
            data={"chat_id": CHAT_ID, "text": message},
            timeout=3
        )
    except:
        pass

# =====================
# DATA WITH TIMEFRAME
# =====================
def load_stock_data(ticker, timeframe):
    try:
        if timeframe == "Daily":
            interval = "1d"
        else:
            interval = "1wk"

        df = yf.download(f"{ticker}.NS", period="3mo", interval=interval)

        if not df.empty:
            return df[['Open','High','Low','Close','Volume']]
    except:
        pass

    return pd.DataFrame()

# =====================
# CHART
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
# HEADER
# =====================
st.title("📈 QuantAgent India")

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

if st.button("Run Analysis"):

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
            "reasoning": "Fallback result due to timeout"
        }

    # =====================
    # DISPLAY
    # =====================
    if result["decision"] == "BUY":
        st.markdown(f"<div class='buy-box'>BUY 📈<br>{result['confidence']}</div>", unsafe_allow_html=True)
        st.toast("BUY Signal")
        send_telegram_alert(f"BUY {selected_stock} ({timeframe})")

    else:
        st.markdown(f"<div class='sell-box'>SELL 📉<br>{result['confidence']}</div>", unsafe_allow_html=True)
        st.toast("SELL Signal")
        send_telegram_alert(f"SELL {selected_stock} ({timeframe})")

    st.write("Risk:", result["risk_level"])
    st.write("RR:", result["risk_reward_ratio"])
    st.write("Entry:", result["entry_price"])
    st.write(result["reasoning"])

    # =====================
    # CHART WITH TIMEFRAME
    # =====================
    df = load_stock_data(selected_stock, timeframe)

    if not df.empty:
        st.plotly_chart(build_chart(df), use_container_width=True)