import sys
import os

# ✅ Fix module path for Streamlit Cloud
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import ta
import yfinance as yf

from agents.decision_agent import run_decision_agent

st.set_page_config(
    page_title="QuantAgent India",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================
# 🔥 NEXT-LEVEL UI CSS
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
# Helper Functions
# =====================
def load_stock_data(ticker_name: str):
    try:
        df = yf.download(f"{ticker_name}.NS", period="3mo", interval="1d")
        if not df.empty:
            return df
    except:
        pass

    path = f"data/{ticker_name}_daily.csv"
    df = pd.read_csv(path)

    df.columns = [c.strip() for c in df.columns]
    df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    return df


def build_chart(ticker, result):
    df = load_stock_data(ticker)
    recent = df.tail(60)

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=recent.index,
        open=recent['Open'],
        high=recent['High'],
        low=recent['Low'],
        close=recent['Close'],
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444'
    ))

    fig.add_hline(y=result['support'], line_dash="dash")
    fig.add_hline(y=result['resistance'], line_dash="dash")

    return fig


def build_rsi_chart(ticker):
    df = load_stock_data(ticker)
    recent = df.tail(60)

    rsi = ta.momentum.RSIIndicator(recent['Close'], window=14).rsi()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=recent.index, y=rsi))

    return fig


# =====================
# Sidebar
# =====================
with st.sidebar:
    st.markdown("## 📈 QuantAgent India")

# =====================
# Header
# =====================
st.markdown("""
<div style="padding:20px;">
<h1>📈 QuantAgent India</h1>
<p style="color:#9ca3af;">AI-powered stock analysis platform</p>
</div>
""", unsafe_allow_html=True)

# =====================
# STOCKS (ALL 25)
# =====================
STOCKS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "HINDUNILVR", "SBIN", "BHARTIARTL", "WIPRO", "LT",
    "ADANIENT", "KOTAKBANK", "AXISBANK", "HCLTECH", "ITC",
    "SUNPHARMA", "MARUTI", "BAJFINANCE", "TECHM", "TITAN",
    "ULTRACEMCO", "NESTLEIND", "POWERGRID", "ONGC", "NTPC"
]

col1, col2, col3 = st.columns([3,1,1])

with col1:
    selected_stock = st.selectbox("Select Stock", STOCKS)

with col2:
    timeframe = st.selectbox("Timeframe", ["Daily", "Weekly"])

with col3:
    run_button = st.button("▶ Run Analysis")

st.markdown("---")

# =====================
# MAIN LOGIC
# =====================
if run_button:
    progress = st.progress(0)

    with st.spinner("Running AI Agents..."):
        try:
            progress.progress(30)
            st.write("Fetching data...")

            progress.progress(60)
            st.write("Running AI models...")

            result = run_decision_agent(selected_stock)

            progress.progress(100)
            st.write("✅ Analysis Complete")

            # 🎯 Decision Box
            st.markdown("## 🎯 AI Trading Decision")

            if result['decision'] == "BUY":
                st.markdown(f"""
                <div class="buy-box">
                    <h1>BUY 📈</h1>
                    <p>Confidence: {result['confidence']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="sell-box">
                    <h1>SELL 📉</h1>
                    <p>Confidence: {result['confidence']}</p>
                </div>
                """, unsafe_allow_html=True)

            # 📊 Metrics Cards
            st.markdown("## 📊 Key Metrics")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="card">
                    <div class="small-text">Risk Level</div>
                    <div class="metric">{result['risk_level']}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="card">
                    <div class="small-text">Risk/Reward</div>
                    <div class="metric">{result['risk_reward_ratio']}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="card">
                    <div class="small-text">Entry Price</div>
                    <div class="metric">₹{result['entry_price']}</div>
                </div>
                """, unsafe_allow_html=True)

            # 🧠 Reasoning
            st.markdown("## 🧠 AI Reasoning")

            st.markdown(f"""
            <div class="card">
            {result['reasoning']}
            </div>
            """, unsafe_allow_html=True)

            # 📉 Charts
            st.markdown("## 📉 Market Analysis")

            col1, col2 = st.columns([3,1])

            price_chart = build_chart(selected_stock, result)
            rsi_chart = build_rsi_chart(selected_stock)

            with col1:
                st.plotly_chart(price_chart, use_container_width=True)

            with col2:
                st.plotly_chart(rsi_chart, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Check Streamlit Secrets → GROQ_API_KEY")

else:
    st.markdown("""
    <div class="card" style="text-align:center;">
        <h2>Welcome to QuantAgent India 🚀</h2>
        <p>Select a stock and click Run Analysis</p>
    </div>
    """, unsafe_allow_html=True)