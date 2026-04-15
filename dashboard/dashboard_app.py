import sys
import os

# Fix module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import ta
import yfinance as yf

from agents.decision_agent import run_decision_agent

st.set_page_config(page_title="QuantAgent India", page_icon="📈", layout="wide")

# =====================
# 🎨 NEXT LEVEL UI CSS
# =====================
st.markdown("""
<style>
body { background-color: #0e1117; color: white; }

.card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
}

.metric { font-size: 22px; font-weight: bold; }
.small-text { color: #9ca3af; font-size: 14px; }

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
# DATA LOADING (FIXED)
# =====================
def load_stock_data(ticker):
    try:
        df = yf.download(f"{ticker}.NS", period="3mo", interval="1d")
        if not df.empty:
            return df[['Open','High','Low','Close','Volume']]
    except:
        pass

    # CSV fallback
    path = f"data/{ticker}_daily.csv"
    df = pd.read_csv(path)

    df = df[df.iloc[:, 0] != 'Ticker']
    df = df[df.iloc[:, 0] != 'Date']

    df.columns = [c.strip() for c in df.columns]
    df.rename(columns={df.columns[0]: 'Date'}, inplace=True)

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df.set_index('Date', inplace=True)

    for col in ['Open','High','Low','Close','Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)
    return df


# =====================
# 📈 MAIN CHART (PRO)
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
        increasing_line_color='#22c55e',
        decreasing_line_color='#ef4444'
    ))

    fig.add_trace(go.Scatter(
        x=recent.index, y=recent['EMA20'],
        line=dict(color='#3b82f6'), name='EMA20'
    ))

    fig.add_trace(go.Scatter(
        x=recent.index, y=recent['EMA50'],
        line=dict(color='#f59e0b'), name='EMA50'
    ))

    if 'support' in result:
        fig.add_hline(y=result['support'], line_dash="dot", line_color="green")
    if 'resistance' in result:
        fig.add_hline(y=result['resistance'], line_dash="dot", line_color="red")

    fig.update_layout(
        template="plotly_dark",
        height=500,
        hovermode="x unified",
        xaxis_rangeslider_visible=False
    )

    return fig


# =====================
# 📉 RSI CHART
# =====================
def build_rsi_chart(ticker):
    df = load_stock_data(ticker)
    recent = df.tail(100)

    rsi = ta.momentum.RSIIndicator(recent['Close'], 14).rsi()

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=recent.index, y=rsi, line=dict(color='#3b82f6')))

    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")

    fig.update_layout(template="plotly_dark", height=250)

    return fig


# =====================
# HEADER
# =====================
st.markdown("""
<h1>📈 QuantAgent India</h1>
<p style="color:gray;">AI-powered stock analysis platform</p>
""", unsafe_allow_html=True)

# =====================
# STOCK LIST
# =====================
STOCKS = [
    "RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK",
    "HINDUNILVR","SBIN","BHARTIARTL","WIPRO","LT",
    "ADANIENT","KOTAKBANK","AXISBANK","HCLTECH","ITC",
    "SUNPHARMA","MARUTI","BAJFINANCE","TECHM","TITAN",
    "ULTRACEMCO","NESTLEIND","POWERGRID","ONGC","NTPC"
]

col1, col2, col3 = st.columns([3,1,1])

with col1:
    selected_stock = st.selectbox("Select Stock", STOCKS)

with col2:
    timeframe = st.selectbox("Timeframe", ["Daily","Weekly"])

with col3:
    run_button = st.button("▶ Run Analysis")

st.markdown("---")

# =====================
# MAIN EXECUTION
# =====================
if run_button:
    progress = st.progress(0)

    try:
        progress.progress(30)
        st.write("Fetching data...")

        progress.progress(60)
        st.write("Running AI...")

        result = run_decision_agent(selected_stock)

        progress.progress(100)

        # 🎯 Decision
        st.markdown("## 🎯 AI Decision")

        if result['decision'] == "BUY":
            st.markdown(f"<div class='buy-box'><h2>BUY 📈</h2>{result['confidence']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='sell-box'><h2>SELL 📉</h2>{result['confidence']}</div>", unsafe_allow_html=True)

        # 📊 Metrics
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<div class='card'><div class='small-text'>Risk</div><div class='metric'>{result['risk_level']}</div></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='card'><div class='small-text'>RR Ratio</div><div class='metric'>{result['risk_reward_ratio']}</div></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='card'><div class='small-text'>Entry</div><div class='metric'>₹{result['entry_price']}</div></div>", unsafe_allow_html=True)

        # 🧠 Reasoning
        st.markdown("## 🧠 AI Reasoning")
        st.markdown(f"<div class='card'>{result['reasoning']}</div>", unsafe_allow_html=True)

        # 📉 Charts
        st.markdown("## 📉 Market Analysis")

        st.plotly_chart(build_chart(selected_stock, result), use_container_width=True)
        st.plotly_chart(build_rsi_chart(selected_stock), use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Check CSV format or internet connection")

else:
    st.markdown("<div class='card'><h3>Welcome 🚀</h3>Select a stock to start</div>", unsafe_allow_html=True)