import sys
import os

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
# 🎨 WHITE + BLUE UI
# =====================
st.markdown("""
<style>
body { background-color: #f5f7fb; color: #111827; }

.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

.metric { font-size: 22px; font-weight: bold; color: #1e3a8a; }
.small-text { color: #6b7280; }

.buy-box {
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: white;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
}

.sell-box {
    background: linear-gradient(135deg, #ef4444, #f87171);
    color: white;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =====================
# 📡 TELEGRAM ALERT (HARDCODED)
# =====================
def send_telegram_alert(message):
    try:
        BOT_TOKEN = "8573595454:AAGnZr4AZnJc-Ai5zx0l71mMr5FxU7NNJuc"
        CHAT_ID = "8548569849"

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": message
        })
    except:
        pass

# =====================
# DATA LOADING
# =====================
def load_stock_data(ticker):
    try:
        df = yf.download(f"{ticker}.NS", period="3mo", interval="1d")
        if not df.empty:
            return df[['Open','High','Low','Close','Volume']]
    except:
        pass

    path = f"data/{ticker}_daily.csv"
    df = pd.read_csv(path)

    df = df[df.iloc[:, 0] != 'Ticker']
    df.columns = [c.strip() for c in df.columns]

    df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    df.dropna(inplace=True)
    df.set_index('Date', inplace=True)

    return df

# =====================
# 📈 CHART
# =====================
def build_chart(ticker, result):
    df = load_stock_data(ticker)
    recent = df.tail(100)

    recent['EMA20'] = ta.trend.EMAIndicator(recent['Close'], 20).ema_indicator()
    recent['EMA50'] = ta.trend.EMAIndicator(recent['Close'], 50).ema_indicator()

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=recent.index,
        open=recent['Open'],
        high=recent['High'],
        low=recent['Low'],
        close=recent['Close'],
        increasing_line_color='#3b82f6',
        decreasing_line_color='#ef4444'
    ))

    fig.add_trace(go.Scatter(x=recent.index, y=recent['EMA20'], name="EMA20", line=dict(color='#2563eb')))
    fig.add_trace(go.Scatter(x=recent.index, y=recent['EMA50'], name="EMA50", line=dict(color='#60a5fa')))

    fig.update_layout(template="plotly_white", height=500, hovermode="x unified")

    return fig

# =====================
# 📉 RSI
# =====================
def build_rsi_chart(ticker):
    df = load_stock_data(ticker)
    recent = df.tail(100)

    rsi = ta.momentum.RSIIndicator(recent['Close'], 14).rsi()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=recent.index, y=rsi, line=dict(color='#2563eb')))

    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")

    fig.update_layout(template="plotly_white", height=250)

    return fig

# =====================
# HEADER
# =====================
st.markdown("""
<h1 style="color:#1e3a8a;">📈 QuantAgent India</h1>
<p style="color:#6b7280;">AI-powered stock analysis platform</p>
""", unsafe_allow_html=True)

# =====================
# STOCKS
# =====================
STOCKS = [
    "RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK",
    "HINDUNILVR","SBIN","BHARTIARTL","WIPRO","LT",
    "ADANIENT","KOTAKBANK","AXISBANK","HCLTECH","ITC",
    "SUNPHARMA","MARUTI","BAJFINANCE","TECHM","TITAN",
    "ULTRACEMCO","NESTLEIND","POWERGRID","ONGC","NTPC"
]

col1, col2, col3 = st.columns([3,1,1])

selected_stock = col1.selectbox("Stock", STOCKS)
timeframe = col2.selectbox("Timeframe", ["Daily","Weekly"])
run_button = col3.button("▶ Run")

st.markdown("---")

# =====================
# MAIN
# =====================
if run_button:
    try:
        result = run_decision_agent(selected_stock)

        st.markdown("## 🎯 Decision")

        if result['decision'] == "BUY":
            st.markdown(f"<div class='buy-box'><h2>BUY 📈</h2>{result['confidence']}</div>", unsafe_allow_html=True)
            st.toast("🚀 BUY Signal Generated!")
            send_telegram_alert(f"🚀 BUY SIGNAL\n{selected_stock}\nConfidence: {result['confidence']}")
        else:
            st.markdown(f"<div class='sell-box'><h2>SELL 📉</h2>{result['confidence']}</div>", unsafe_allow_html=True)
            st.toast("⚠️ SELL Signal Generated!")
            send_telegram_alert(f"⚠️ SELL SIGNAL\n{selected_stock}\nConfidence: {result['confidence']}")

        # Metrics
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<div class='card'><div class='small-text'>Risk</div><div class='metric'>{result['risk_level']}</div></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><div class='small-text'>RR Ratio</div><div class='metric'>{result['risk_reward_ratio']}</div></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><div class='small-text'>Entry</div><div class='metric'>₹{result['entry_price']}</div></div>", unsafe_allow_html=True)

        st.markdown("## 🧠 Reasoning")
        st.markdown(f"<div class='card'>{result['reasoning']}</div>", unsafe_allow_html=True)

        st.markdown("## 📉 Market Analysis")
        st.plotly_chart(build_chart(selected_stock, result), use_container_width=True)
        st.plotly_chart(build_rsi_chart(selected_stock), use_container_width=True)

    except Exception as e:
        st.error(e)

else:
    st.markdown("<div class='card'>Select stock and run analysis</div>", unsafe_allow_html=True)