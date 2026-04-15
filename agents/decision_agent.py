import os
import sys
import json
import time

sys.path.append('tools')
sys.path.append('agents')

from dotenv import load_dotenv
from compute_indicators import load_stock, compute_indicators, interpret_indicators
from pattern_agent import analyze_pattern
from trend_agent import compute_trendlines, analyze_trend
from risk_agent import compute_risk
from groq import Groq

load_dotenv()

# =====================
# SAFE API KEY
# =====================
try:
    import streamlit as st
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# =====================
# PROMPT
# =====================
DECISION_PROMPT = """
You are an expert trading analyst.

INDICATOR REPORT:
{indicator_summary}

PATTERN REPORT:
{pattern_summary}

TREND REPORT:
{trend_summary}

Give BUY or SELL only.

Respond in JSON:
{{
 "decision": "BUY or SELL",
 "confidence": "High/Medium/Low",
 "reasoning": "short explanation"
}}
"""

# =====================
# FALLBACK
# =====================
def fallback(ticker):
    return {
        "ticker": ticker,
        "decision": "BUY",
        "confidence": "Low",
        "risk_level": "Medium",
        "reasoning": "Fallback due to slow or failed analysis",
        "risk_reward_ratio": "1:1",
        "entry_price": 1000.0,
        "stop_loss": 950.0,
        "take_profit": 1100.0,
        "potential_profit": 100,
        "potential_loss": 50,
        "support": 950.0,
        "resistance": 1100.0,
        "trend": "sideways"
    }

# =====================
# MAIN AGENT
# =====================
def run_decision_agent(ticker_name: str) -> dict:
    start = time.time()

    try:
        # =====================
        # INDICATOR
        # =====================
        df = load_stock(ticker_name)

        if df is None or df.empty:
            return fallback(ticker_name)

        indicators = compute_indicators(df)
        indicator_summary = interpret_indicators(indicators)

        # =====================
        # PATTERN
        # =====================
        pattern_summary = analyze_pattern(ticker_name)

        # =====================
        # TREND
        # =====================
        trend_data = compute_trendlines(ticker_name)
        trend_summary = analyze_trend(ticker_name)

        # =====================
        # TIMEOUT CHECK
        # =====================
        if time.time() - start > 8:
            return fallback(ticker_name)

        # =====================
        # GROQ CALL (SAFE)
        # =====================
        prompt = DECISION_PROMPT.format(
            indicator_summary=indicator_summary,
            pattern_summary=pattern_summary,
            trend_summary=trend_summary
        )

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300,
            )

            raw = response.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()

            decision = json.loads(raw)

        except:
            decision = {
                "decision": "BUY",
                "confidence": "Low",
                "reasoning": "LLM failed, fallback used"
            }

        # =====================
        # RISK
        # =====================
        entry_price = float(df['Close'].iloc[-1])

        risk_data = compute_risk(
            entry_price=entry_price,
            direction=decision['decision'],
            support=float(trend_data['support']),
            resistance=float(trend_data['resistance'])
        )

        # =====================
        # FINAL RESULT
        # =====================
        return {
            "ticker": ticker_name,
            "decision": decision.get("decision", "BUY"),
            "confidence": decision.get("confidence", "Low"),
            "risk_level": risk_data.get("risk_level", "Medium"),
            "reasoning": decision.get("reasoning", ""),
            "risk_reward_ratio": risk_data.get("rr_ratio", "1:1"),
            "entry_price": float(risk_data.get("entry", entry_price)),
            "stop_loss": float(risk_data.get("stop_loss", entry_price * 0.95)),
            "take_profit": float(risk_data.get("take_profit", entry_price * 1.05)),
            "potential_profit": float(risk_data.get("potential_profit", 0)),
            "potential_loss": float(risk_data.get("potential_loss", 0)),
            "support": float(trend_data.get("support", entry_price * 0.95)),
            "resistance": float(trend_data.get("resistance", entry_price * 1.05)),
            "trend": trend_data.get("trend", "unknown")
        }

    except Exception as e:
        return fallback(ticker_name)