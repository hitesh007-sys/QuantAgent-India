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
        annotation_text=f"Support ₹{result['support']}",
        annotation_font_color="#10b981",
        annotation_position="bottom right"
    )
    fig.add_hline(
        y=result['resistance'],
        line_dash="dash",
        line_color="#ef4444",
        line_width=1.5,
        annotation_text=f"Resistance ₹{result['resistance']}",
        annotation_font_color="#ef4444",
        annotation_position="top right"
    )

    last_date  = recent.index[-1]
    last_close = float(recent['Close'].iloc[-1])
    sig_color  = '#10b981' if result['decision'] == 'BUY' else '#ef4444'
    sig_symbol = 'triangle-up' if result['decision'] == 'BUY' else 'triangle-down'

    fig.add_trace(go.Scatter(
        x=[last_date],
        y=[last_close],
        mode='markers+text',
        marker=dict(symbol=sig_symbol, size=24, color=sig_color),
        text=[result['decision']],
        textposition="top center",
        textfont=dict(color=sig_color, size=14, family="Inter", weight="bold"),
        name=result['decision']
    ))

    fig.update_layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#f8fafc',
        font=dict(color='#0f172a', family="Inter"),
        xaxis=dict(
            showgrid=True,
            gridcolor='#e2e8f0',
            rangeslider=dict(visible=False),
            color='#475569'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#e2e8f0',
            title='Price (₹)',
            color='#475569'
        ),
        height=420,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            bgcolor='#ffffff',
            bordercolor='#e2e8f0',
            borderwidth=1,
            font=dict(color='#0f172a')
        )
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
        fill='tonexty',
        fillcolor='rgba(37, 99, 235, 0.1)',
        line=dict(color='#2563eb', width=2),
        name='RSI'
    ))
    fig.add_hline(y=70, line_dash="dash",
                  line_color="#ef4444", line_width=1,
                  annotation_text="Overbought 70",
                  annotation_font_color="#ef4444")
    fig.add_hline(y=30, line_dash="dash",
                  line_color="#10b981", line_width=1,
                  annotation_text="Oversold 30",
                  annotation_font_color="#10b981")
    fig.add_hline(y=50, line_dash="dot",
                  line_color="#94a3b8", line_width=1)

    fig.update_layout(
        paper_bgcolor='#ffffff',
        plot_bgcolor='#f8fafc',
        font=dict(color='#0f172a', family="Inter"),
        height=180,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(
            showgrid=True,
            gridcolor='#e2e8f0',
            color='#475569'
        ),
        yaxis=dict(
            range=[0, 100],
            showgrid=True,
            gridcolor='#e2e8f0',
            color='#475569'
        ),
        title=dict(
            text="RSI Indicator",
            font=dict(color='#1e3a8a', size=14, family="Inter", weight="bold")
        )
    )
    return fig


# =====================
# Sidebar
# =====================
with st.sidebar:
    st.markdown("""
    <div style='padding: 20px 0; text-align: center;'>
        <h2 style='color: #1e3a8a; font-size: 2.2rem;
                   font-weight: 800; margin-bottom: 5px;'>
            📈 QuantAgent
        </h2>
        <p style='color: #64748b; font-size: 0.9rem; font-weight: 500;'>
            Multi-Agent AI Trading
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='color: #475569; font-size: 0.8rem; font-weight: 700;
                text-transform: uppercase; letter-spacing: 1.5px;
                margin-bottom: 12px; margin-top: 10px; padding-left: 5px;'>
        Available Stocks
    </div>
    """, unsafe_allow_html=True)

    stocks_display = [
        ("📦", "Reliance"), ("💻", "TCS"),
        ("🖥️", "Infosys"), ("🏦", "HDFC Bank"),
        ("🏦", "ICICI Bank"), ("🏛️", "SBI"),
        ("📡", "Airtel"), ("💊", "Sun Pharma"),
        ("🚗", "Maruti"), ("⚡", "NTPC"),
        ("🛢️", "ONGC"), ("🏗️", "L&T"),
        ("💰", "Bajaj Finance"), ("💎", "Titan"),
        ("🍭", "ITC"), ("🌐", "Wipro"),
        ("☁️", "HCL Tech"), ("🏦", "Kotak"),
        ("🏦", "Axis Bank"), ("⚡", "Powergrid"),
        ("🏭", "Ultratech"), ("🍫", "Nestle"),
        ("📱", "Tech Mahindra"), ("🏢", "Adani"),
        ("🧴", "HUL")
    ]

    # Container for stocks to allow scrolling while keeping footer at bottom
    st.markdown("<div style='height: 400px; overflow-y: auto; padding-right: 10px;'>", unsafe_allow_html=True)
    for icon, name in stocks_display:
        st.markdown(f"""
        <div style='padding: 8px 12px; border-radius: 8px;
                    color: #334155; font-size: 0.95rem; font-weight: 500;
                    margin-bottom: 4px; background: #f8fafc; border: 1px solid #e2e8f0;'>
            <span style='margin-right: 10px;'>{icon}</span> {name}
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Group 13 Submission text
    st.markdown("""
    <div style='margin-top: 40px; padding: 20px 15px;
                background: #eff6ff; border-radius: 12px; border: 1px solid #bfdbfe;
                color: #1e3a8a; text-align: center;'>
        <strong style='font-size: 1rem; display: block; margin-bottom: 5px;'>ML Stock Analysis</strong>
        <span style='font-size: 0.85rem; color: #3b82f6; font-weight: 600;'>Submitted by Group-13</span>
    </div>
    """, unsafe_allow_html=True)


# =====================
# Main Content
# =====================

# Header
st.markdown("""
<div class="header-banner">
    <h1>📈 QuantAgent India</h1>
    <p>Multi-Agent AI Trading System for Indian Stock Markets</p>
</div>
""", unsafe_allow_html=True)

STOCKS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "HINDUNILVR", "SBIN", "BHARTIARTL", "WIPRO", "LT",
    "ADANIENT", "KOTAKBANK", "AXISBANK", "HCLTECH", "ITC",
    "SUNPHARMA", "MARUTI", "BAJFINANCE", "TECHM", "TITAN",
    "ULTRACEMCO", "NESTLEIND", "POWERGRID", "ONGC", "NTPC"
]

# Config Row
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    selected_stock = st.selectbox(
        "Select Stock",
        STOCKS,
        index=0,
        label_visibility="collapsed"
    )
with col2:
    timeframe = st.selectbox(
        "Timeframe",
        ["Daily", "Weekly"],
        label_visibility="collapsed"
    )
with col3:
    run_button = st.button(
        "▶  Run Analysis",
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)

if run_button:
    with st.spinner(
        f"🤖 Running all agents for {selected_stock}..."
    ):
        try:
            result = run_decision_agent(selected_stock)

            # ── Summary Metrics ──
            st.markdown("""
            <div class="section-title">📊 Analysis Summary</div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">60</div>
                    <div class="label">Data Points</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{timeframe}</div>
                    <div class="label">Timeframe</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{selected_stock}</div>
                    <div class="label">Asset</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Decision ──
            st.markdown("""
            <div class="section-title">🎯 Final Trading Decision</div>
            """, unsafe_allow_html=True)

            left, mid, right = st.columns([1, 2, 1])
            with mid:
                dec_class = (
                    "decision-buy"
                    if result['decision'] == "BUY"
                    else "decision-sell"
                )
                st.markdown(
                    f'<div style="text-align:center">'
                    f'<span class="{dec_class}">'
                    f'{result["decision"]}</span></div>',
                    unsafe_allow_html=True
                )

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{result['confidence']}</div>
                    <div class="label">Confidence</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{result['risk_level']}</div>
                    <div class="label">Risk Level</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{result['risk_reward_ratio']}</div>
                    <div class="label">Risk / Reward</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="reasoning-box">
                <strong style="color:#2563eb; font-size: 1.1rem; display: block; margin-bottom: 8px;">
                    AI Reasoning & Justification:
                </strong>
                {result['reasoning']}
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Charts ──
            st.markdown("""
            <div class="section-title">📉 Price & Indicator Charts</div>
            """, unsafe_allow_html=True)

            price_chart = build_chart(selected_stock, result)
            st.plotly_chart(
                price_chart, use_container_width=True
            )

            rsi_chart = build_rsi_chart(selected_stock)
            st.plotly_chart(
                rsi_chart, use_container_width=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Trade Setup ──
            st.markdown("""
            <div class="section-title">💰 Trade Setup Parameters</div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
                <div class="trade-row">
                    <span class="trade-label">Target Entry Price</span>
                    <span class="trade-value" style="color: #2563eb !important;">
                        ₹{result['entry_price']:.2f}
                    </span>
                </div>
                <div class="trade-row">
                    <span class="trade-label">Calculated Stop Loss</span>
                    <span class="trade-value" style="color:#ef4444 !important;">
                        ₹{result['stop_loss']:.2f}
                    </span>
                </div>
                <div class="trade-row">
                    <span class="trade-label">Take Profit Target</span>
                    <span class="trade-value" style="color:#10b981 !important;">
                        ₹{result['take_profit']:.2f}
                    </span>
                </div>
                <div class="trade-row">
                    <span class="trade-label">Risk / Reward Ratio</span>
                    <span class="trade-value" style="color:#4f46e5 !important;">
                        {result['risk_reward_ratio']}
                    </span>
                </div>
                <div class="trade-row">
                    <span class="trade-label">Potential Profit Margin</span>
                    <span class="trade-value" style="color:#10b981 !important;">
                        ₹{result['potential_profit']:.2f}
                    </span>
                </div>
                <div class="trade-row" style="border:none">
                    <span class="trade-label">Maximum Potential Loss</span>
                    <span class="trade-value" style="color:#ef4444 !important;">
                        ₹{result['potential_loss']:.2f}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Indicator Agent ──
            st.markdown("""
            <div class="section-title">📊 Technical Indicator Analysis</div>
            """, unsafe_allow_html=True)

            ind = result['indicators']
            indicators_data = [
                ("RSI",    ind['RSI'],    "RSI"),
                ("MACD",   ind['MACD'],   "MACD"),
                ("ROC",    ind['ROC'],    "ROC"),
                ("Stoch K", ind['Stoch_K'], "Stoch"),
                ("Williams %R", ind['Williams_R'], "RSI")
            ]

            cols = st.columns(5)
            for i, (label, value, ind_type) in enumerate(
                indicators_data
            ):
                signal_text, signal_type = get_signal(
                    value, ind_type
                )
                with cols[i]:
                    st.markdown(f"""
                    <div class="indicator-pill">
                        <div class="ind-value">{value}</div>
                        <div class="ind-label">{label}</div>
                        <div class="ind-signal
                            signal-{signal_type}">
                            {signal_text}
                        </div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Trend Agent ──
            st.markdown("""
            <div class="section-title">📈 Trend Detection Agent</div>
            """, unsafe_allow_html=True)

            trend_color = (
                "#10b981"
                if result['trend'] == "Uptrend"
                else "#ef4444"
                if result['trend'] == "Downtrend"
                else "#3b82f6"
            )

            st.markdown(f"""
            <div class="card">
                <div style="display:flex;
                            justify-content:space-around;
                            align-items:center;">
                    <div style="text-align:center">
                        <div style="font-size:1.6rem;
                                    font-weight:800;
                                    color:{trend_color}">
                            {result['trend']}
                        </div>
                        <div style="color:#64748b;font-size:0.8rem; font-weight:600;
                                    text-transform:uppercase;
                                    letter-spacing:1px; margin-top:5px;">
                            Trend Direction
                        </div>
                    </div>
                    <div style="text-align:center">
                        <div style="font-size:1.6rem;
                                    font-weight:800;
                                    color:#10b981">
                            ₹{result['support']}
                        </div>
                        <div style="color:#64748b;font-size:0.8rem; font-weight:600;
                                    text-transform:uppercase;
                                    letter-spacing:1px; margin-top:5px;">
                            Support Level
                        </div>
                    </div>
                    <div style="text-align:center">
                        <div style="font-size:1.6rem;
                                    font-weight:800;
                                    color:#ef4444">
                            ₹{result['resistance']}
                        </div>
                        <div style="color:#64748b;font-size:0.8rem; font-weight:600;
                                    text-transform:uppercase;
                                    letter-spacing:1px; margin-top:5px;">
                            Resistance Level
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Risk Agent ──
            st.markdown("""
            <div class="section-title">⚠️ Risk Assessment Agent</div>
            """, unsafe_allow_html=True)

            risk_color = (
                "#10b981" if result['risk_level'] == "Low"
                else "#f59e0b" if result['risk_level'] == "Medium"
                else "#ef4444"
            )

            st.markdown(f"""
            <div class="card">
                <div style="display:flex;
                            justify-content:space-around;
                            align-items:center;">
                    <div style="text-align:center">
                        <div style="font-size:1.6rem;
                                    font-weight:800;
                                    color:{risk_color}">
                            {result['risk_level']}
                        </div>
                        <div style="color:#64748b;font-size:0.8rem; font-weight:600;
                                    text-transform:uppercase;
                                    letter-spacing:1px; margin-top:5px;">
                            Risk Level
                        </div>
                    </div>
                    <div style="text-align:center">
                        <div style="font-size:1.6rem;
                                    font-weight:800;
                                    color:#ef4444">
                            ₹{result['potential_loss']:.2f}
                        </div>
                        <div style="color:#64748b;font-size:0.8rem; font-weight:600;
                                    text-transform:uppercase;
                                    letter-spacing:1px; margin-top:5px;">
                            Potential Loss
                        </div>
                    </div>
                    <div style="text-align:center">
                        <div style="font-size:1.6rem;
                                    font-weight:800;
                                    color:#4f46e5">
                            {result['risk_reward_ratio']}
                        </div>
                        <div style="color:#64748b;font-size:0.8rem; font-weight:600;
                                    text-transform:uppercase;
                                    letter-spacing:1px; margin-top:5px;">
                            Risk / Reward
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <br>
            <div style="text-align:center; color:#94a3b8;
                        font-size:0.85rem; padding:20px;">
                ⚠️ For educational purposes only. Not financial advice.
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info(
                "Make sure your .env file "
                "has GROQ_API_KEY set correctly."
            )

else:
    st.markdown("""
    <div class="welcome-box">
        <h2>Welcome to QuantAgent India 🚀</h2>
        <p>Select a stock from the dropdown above and click <br>
           <strong style="color:#2563eb">Run Analysis</strong>
           to generate your intelligent report.</p>
        <br>
        <p style="color:#64748b; font-size:0.9rem; font-weight: 500;">
            Powered by Groq LLM · 4 AI Agents · 25 Indian Stocks
        </p>
    </div>
    """, unsafe_allow_html=True)

