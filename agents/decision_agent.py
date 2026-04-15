import os
import sys
import json
sys.path.append('tools')
sys.path.append('agents')

from dotenv import load_dotenv
from compute_indicators import load_stock, compute_indicators, interpret_indicators
from pattern_agent import analyze_pattern
from trend_agent import compute_trendlines, analyze_trend
from risk_agent import compute_risk, format_risk_summary
from groq import Groq

load_dotenv()

# Safe API Key Fetching for both Cloud and Local
try:
    import streamlit as st
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)


DECISION_PROMPT = """
You are an expert high-frequency trading analyst for Indian stock markets.
You MUST issue either BUY or SELL. HOLD is not allowed.
Forecast horizon: next 3 candlesticks.

You have received three reports:

INDICATOR REPORT:
{indicator_summary}

PATTERN REPORT:
{pattern_summary}

TREND REPORT:
{trend_summary}

Decision Rules:
- Act only when at least 2 out of 3 reports agree.
- If all 3 conflict, go with the trend direction.
- Explain reasoning in simple language a beginner can understand.

You MUST respond ONLY as valid JSON like this:
{{
  "decision": "BUY or SELL",
  "confidence": "High or Medium or Low",
  "reasoning": "2-3 sentence plain English explanation"
}}
"""


def run_decision_agent(ticker_name: str) -> dict:
    """
    Runs all 4 agents and makes final BUY/SELL decision.
    Returns complete analysis as dictionary.
    """
    print(f"\nAnalyzing {ticker_name}...")
    print("="*50)

    # Step 1 - Run Indicator Agent
    print("Running IndicatorAgent...")
    df = load_stock(ticker_name)
    indicators = compute_indicators(df)
    indicator_summary = interpret_indicators(indicators)
    print("IndicatorAgent done.")

    # Step 2 - Run Pattern Agent
    print("Running PatternAgent...")
    pattern_summary = analyze_pattern(ticker_name)
    print("PatternAgent done.")

    # Step 3 - Run Trend Agent
    print("Running TrendAgent...")
    trend_data = compute_trendlines(ticker_name)
    trend_summary = analyze_trend(ticker_name)
    print("TrendAgent done.")

    # Step 4 - Run Decision Agent
    print("Running DecisionAgent...")
    prompt = DECISION_PROMPT.format(
        indicator_summary=indicator_summary,
        pattern_summary=pattern_summary,
        trend_summary=trend_summary
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=400
    )

    raw = response.choices[0].message.content.strip()

    # Clean JSON response
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        decision = json.loads(raw)
    except json.JSONDecodeError:
        decision = {
            "decision": "BUY",
            "confidence": "Low",
            "reasoning": raw
        }

    # Step 5 - Run Risk Agent (Now Dynamic!)
    entry_price = float(df['Close'].iloc[-1])
    risk_data = compute_risk(
        entry_price=entry_price,
        direction=decision['decision'],
        support=trend_data['support'],
        resistance=trend_data['resistance']
    )

    # Combine everything
    result = {
        "ticker":           ticker_name,
        "decision":         decision['decision'],
        "confidence":       decision['confidence'],
        "risk_level":       risk_data['risk_level'],
        "reasoning":        decision['reasoning'],
        "risk_reward_ratio": risk_data['rr_ratio'],
        "entry_price":      risk_data['entry'],
        "stop_loss":        risk_data['stop_loss'],
        "take_profit":      risk_data['take_profit'],
        "potential_profit": risk_data['potential_profit'],
        "potential_loss":   risk_data['potential_loss'],
        "indicators":       indicators,
        "trend":            trend_data['trend'],
        "support":          trend_data['support'],
        "resistance":       trend_data['resistance']
    }

    return result