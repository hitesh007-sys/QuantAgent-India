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
# 🎨 DARK UI (RESTORED)
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

.metric { font-size: 22px; font-weight: bold; }
.small-text { color: #9ca3af; }

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
# 📡 TELEGRAM ALERT (FIXED)
# =====================
def send_telegram_alert(message):
    try:
        BOT_TOKEN = "8573595454:AAGnZr4AZnJc-Ai5zx0l71mMr5FxU7NNJuc"
        CHAT_ID = "8548569849"

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        requests.post(
            url,
            data={"chat_id": CHAT_ID, "text": message},
            timeout=3   # ✅ prevents freezing
        )
    except Exception as e:
        print("Telegram failed:", e)

# =====================
# DATA LOADING (CLEAN)
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

    # ✅ ensure numeric
    for col in ['Open','High','Low','Close','Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)

    return df

# =====================
# 📈 CHART
# =====================
def build_chart(ticker, result):
    df = load_stock_data(ticker)

    if df is None or df.empty:
        return go.Figure()

    recent = df.tail(100)

    recent['EMA20'] = ta.trend.EMAIndicator(recent['Close'], 20).ema_indicator()
    recent['EMA50'] = ta.trend.EMAIndicator(recent['Close'], 50).ema_indicator()

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=recent.index,
        open=recent['Open'],
        high=recent['High'],
        low=recent['Low'],
        close=recent['Close']
    ))

    fig.add_trace(go.Scatter(x=recent.index, y=recent['EMA20'], name="EMA20"))
    fig.add_trace(go.Scatter(x=recent.index, y=recent['EMA50'], name="EMA50"))

    # ✅ safe support/resistance
    try:
        if 'support' in result:
            fig.add_hline(y=float(result['support']))
        if 'resistance' in result:
            fig.add_hline(y=float(result['resistance']))
    except:
        pass

    fig.update_layout(template="plotly_dark", height=500)

    return fig

# =====================
# 📉 RSI
# =====================
def build_rsi_chart(ticker):
    df = load_stock_data(ticker)

    if df is None or df.empty:
        return go.Figure()

    recent = df.tail(100)

    rsi = ta.momentum.RSIIndicator(recent['Close'], 14).rsi()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=recent.index, y=rsi))

    fig.add_hline(y=70)
    fig.add_hline(y=30)

    fig.update_layout(template="plotly_dark", height=250)

    return fig

# =====================
# HEADER
# =====================
st.markdown("<h1>📈 QuantAgent India</h1>", unsafe_allow_html=True)

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

        # ✅ FIX TYPE ERROR
        try:
            result['entry_price'] = float(result.get('entry_price', 0))
        except:
            result['entry_price'] = 0

        try:
            if 'support' in result:
                result['support'] = float(result['support'])
            if 'resistance' in result:
                result['resistance'] = float(result['resistance'])
        except:
            pass

        st.markdown("## 🎯 Decision")

        if result['decision'] == "BUY":
            st.markdown(f"<div class='buy-box'><h2>BUY 📈</h2>{result['confidence']}</div>", unsafe_allow_html=True)
            st.toast("🚀 BUY Signal Generated!")
            send_telegram_alert(f"BUY {selected_stock} {result['confidence']}")

        else:
            st.markdown(f"<div class='sell-box'><h2>SELL 📉</h2>{result['confidence']}</div>", unsafe_allow_html=True)
            st.toast("⚠️ SELL Signal Generated!")
            send_telegram_alert(f"SELL {selected_stock} {result['confidence']}")

        # Metrics
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<div class='card'>Risk: {result['risk_level']}</div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'>RR: {result['risk_reward_ratio']}</div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'>Entry: ₹{result['entry_price']}</div>", unsafe_allow_html=True)

        st.markdown("## 🧠 Reason")
        st.markdown(f"<div class='card'>{result['reasoning']}</div>", unsafe_allow_html=True)

        st.plotly_chart(build_chart(selected_stock, result), use_container_width=True)
        st.plotly_chart(build_rsi_chart(selected_stock), use_container_width=True)

    except Exception as e:
        st.error(e)

else:
    st.markdown("<div class='card'>Select stock and run analysis</div>", unsafe_allow_html=True)