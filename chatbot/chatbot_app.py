import os
import sys
sys.path.append('tools')
sys.path.append('agents')

import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from decision_agent import run_decision_agent, format_final_output

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# All 25 Indian stocks
STOCK_MAP = {
    "reliance":    "RELIANCE",
    "tcs":         "TCS",
    "infosys":     "INFY",
    "infy":        "INFY",
    "hdfc":        "HDFCBANK",
    "hdfcbank":    "HDFCBANK",
    "icici":       "ICICIBANK",
    "icicibank":   "ICICIBANK",
    "hindustan":   "HINDUNILVR",
    "hul":         "HINDUNILVR",
    "sbi":         "SBIN",
    "bharti":      "BHARTIARTL",
    "airtel":      "BHARTIARTL",
    "wipro":       "WIPRO",
    "lt":          "LT",
    "larsen":      "LT",
    "adani":       "ADANIENT",
    "kotak":       "KOTAKBANK",
    "axis":        "AXISBANK",
    "hcl":         "HCLTECH",
    "itc":         "ITC",
    "sunpharma":   "SUNPHARMA",
    "sun":         "SUNPHARMA",
    "maruti":      "MARUTI",
    "bajaj":       "BAJFINANCE",
    "bajfinance":  "BAJFINANCE",
    "techm":       "TECHM",
    "tech mahindra": "TECHM",
    "titan":       "TITAN",
    "ultratech":   "ULTRACEMCO",
    "nestle":      "NESTLEIND",
    "powergrid":   "POWERGRID",
    "ongc":        "ONGC",
    "ntpc":        "NTPC"
}


def extract_ticker(user_message: str) -> str:
    """
    Extracts stock ticker from user message.
    Returns ticker name or None if not found.
    """
    message_lower = user_message.lower()

    # Check direct match
    for keyword, ticker in STOCK_MAP.items():
        if keyword in message_lower:
            return ticker

    # Ask Groq to extract ticker
    prompt = f"""
The user said: "{user_message}"

From this message, identify which Indian stock they are asking about.
The available stocks are: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK,
HINDUNILVR, SBIN, BHARTIARTL, WIPRO, LT, ADANIENT, KOTAKBANK,
AXISBANK, HCLTECH, ITC, SUNPHARMA, MARUTI, BAJFINANCE, TECHM,
TITAN, ULTRACEMCO, NESTLEIND, POWERGRID, ONGC, NTPC

Reply with ONLY the ticker name like: RELIANCE
If no stock is mentioned reply with: NONE
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=20
    )
    ticker = response.choices[0].message.content.strip().upper()

    if ticker in [v for v in STOCK_MAP.values()]:
        return ticker
    return None


def format_chat_response(result: dict) -> str:
    """
    Formats the result in a friendly chatbot style.
    """
    emoji = "🟢" if result['decision'] == "BUY" else "🔴"
    confidence_emoji = (
        "💪" if result['confidence'] == "High"
        else "👍" if result['confidence'] == "Medium"
        else "⚠️"
    )
    risk_emoji = (
        "✅" if result['risk_level'] == "Low"
        else "⚠️" if result['risk_level'] == "Medium"
        else "🚨"
    )

    response = f"""
{emoji} **{result['ticker']} Analysis**

**Decision: {result['decision']}**
{confidence_emoji} Confidence: {result['confidence']}
{risk_emoji} Risk Level: {result['risk_level']}

**What does this mean?**
{result['reasoning']}

**Trade Setup:**
| | |
|---|---|
| Entry Price | ₹{result['entry_price']} |
| Stop Loss | ₹{result['stop_loss']} |
| Take Profit | ₹{result['take_profit']} |
| Risk/Reward | {result['risk_reward_ratio']} |
| Potential Profit | ₹{result['potential_profit']} |
| Potential Loss | ₹{result['potential_loss']} |

**Technical Summary:**
- Trend: {result['trend']}
- Support: ₹{result['support']}
- Resistance: ₹{result['resistance']}
- RSI: {result['indicators']['RSI']}
- MACD: {result['indicators']['MACD']}

*Disclaimer: This is for educational purposes only. Not financial advice.*
"""
    return response.strip()


# =====================
# Streamlit UI
# =====================

st.set_page_config(
    page_title="QuantAgent India",
    page_icon="📈",
    layout="centered"
)

st.title("📈 QuantAgent India")
st.caption("AI-powered stock analysis for Indian markets")

# Sidebar with available stocks
with st.sidebar:
    st.header("Available Stocks")
    st.write("You can ask about:")
    stocks_list = [
        "Reliance", "TCS", "Infosys", "HDFC Bank",
        "ICICI Bank", "SBI", "Wipro", "HCL Tech",
        "Airtel", "ITC", "Sun Pharma", "Maruti",
        "Bajaj Finance", "Titan", "ONGC", "NTPC",
        "Kotak Bank", "Axis Bank", "L&T", "Adani",
        "Nestle", "Powergrid", "Tech Mahindra",
        "Ultratech", "HUL"
    ]
    for stock in stocks_list:
        st.write(f"• {stock}")

    st.divider()
    st.caption("Powered by Groq LLM + QuantAgent")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    welcome = """
👋 **Welcome to QuantAgent India!**

I can analyze any of the top 25 Indian stocks for you.

**Try asking:**
- "Should I buy Reliance today?"
- "What is TCS doing right now?"
- "Give me analysis for INFY"
- "Is SBI a good buy?"

Just type your question below!
"""
    st.session_state.messages.append({
        "role": "assistant",
        "content": welcome
    })

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about any Indian stock..."):

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process and respond
    with st.chat_message("assistant"):

        # Extract ticker from message
        ticker = extract_ticker(prompt)

        if ticker is None:
            response = """
I could not identify a stock in your message.

Please mention a specific stock like:
- "Analyze Reliance"
- "Should I buy TCS?"
- "What about INFY?"
"""
            st.markdown(response)

        else:
            with st.spinner(f"Analyzing {ticker}... this takes about 20 seconds"):
                try:
                    result = run_decision_agent(ticker)
                    response = format_chat_response(result)
                    st.markdown(response)
                except Exception as e:
                    response = f"Sorry, something went wrong: {str(e)}"
                    st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })