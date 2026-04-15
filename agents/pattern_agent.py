import sys
sys.path.append('tools')

import streamlit as st
from groq import Groq
from generate_chart import describe_chart_pattern


# ✅ Ensure API key exists (important for deployment)
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ GROQ_API_KEY not found in Streamlit Secrets. Please add it.")
    st.stop()

# ✅ Correct way to initialize client in Streamlit Cloud
client = Groq(api_key=st.secrets["GROQ_API_KEY"])


PATTERN_LIBRARY = """
1. Double Bottom (W shape) — bullish reversal
2. Double Top (M shape) — bearish reversal
3. Descending Triangle — bearish continuation
4. Ascending Triangle — bullish continuation
5. Falling Wedge — bullish reversal
6. Rising Wedge — bearish reversal
7. Bullish Flag — bullish continuation
8. Bearish Flag — bearish continuation
9. V-shaped Reversal — sharp recovery
10. Rounded Bottom — slow bullish reversal
11. Head and Shoulders — bearish reversal
12. Inverse Head and Shoulders — bullish reversal
13. Sideways Rectangle — no clear direction
"""


def analyze_pattern(ticker_name: str) -> str:
    """
    Analyzes chart pattern for a stock using Groq LLM.
    Returns plain English pattern analysis.
    """

    chart_description = describe_chart_pattern(ticker_name)

    prompt = f"""
You are an expert stock chart pattern analyst for Indian markets.

Here is the price data summary for {ticker_name}:
{chart_description}

Here are the classic patterns to compare against:
{PATTERN_LIBRARY}

Based on the price data above:
1. Which pattern best matches this stock?
2. What does this pattern suggest about future price movement?
3. Is this a bullish or bearish signal?

Reply in 3 short sentences maximum. Be specific and clear.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()