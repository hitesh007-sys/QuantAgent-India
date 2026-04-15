import sys
sys.path.append('tools')
sys.path.append('agents')

from trend_agent import compute_trendlines, analyze_trend
from risk_agent import compute_risk, format_risk_summary

print("Testing TrendAgent...\n")

# Test trend data
trend = compute_trendlines('RELIANCE')
print("RELIANCE Trend Data:")
for k, v in trend.items():
    print(f"  {k}: {v}")

print("\nRELIANCE Trend Analysis (LLM):")
analysis = analyze_trend('RELIANCE')
print(analysis)

print("\n" + "="*50 + "\n")

print("Testing RiskAgent...\n")

# Test risk calculation for BUY
risk_buy = compute_risk(
    entry_price=2500.00,
    direction="BUY",
    rr_ratio=1.5
)
print("Risk Summary for BUY:")
print(format_risk_summary(risk_buy))

print("\n" + "="*50 + "\n")

# Test risk calculation for SELL
risk_sell = compute_risk(
    entry_price=2500.00,
    direction="SELL",
    rr_ratio=1.3
)
print("Risk Summary for SELL:")
print(format_risk_summary(risk_sell))