# 📈 QuantAgent India: Multi-Agent AI Trading System

**An advanced Machine Learning & LLM-powered stock analysis platform designed for the Indian Stock Market (NSE/BSE).**

**Submitted by:** Group 13  
**Domain:** Machine Learning & Financial Engineering  

---

## 📌 Project Overview
QuantAgent India is a comprehensive, multi-agent AI trading dashboard that analyzes 25 major Indian equities. Instead of relying on a single algorithm, the system deploys a swarm of specialized AI agents that evaluate technical indicators, market trends, and risk metrics to generate a final, synthesized trading decision.

## 🤖 The Multi-Agent Architecture
The core intelligence of this platform is divided into four distinct agents:

1. **📊 Indicator Agent:** Calculates and interprets key momentum and trend indicators including RSI (Relative Strength Index), MACD, Rate of Change (ROC), Stochastic Oscillator, and Williams %R.
2. **📈 Trend Agent:** Identifies the broader market direction (Uptrend, Downtrend, or Sideways) and establishes critical Support and Resistance price levels.
3. **⚠️ Risk Agent:** Evaluates the volatility of the asset to determine the Risk Level (Low, Medium, High) and dynamically calculates optimal Stop Loss and Take Profit targets to maintain a healthy Risk/Reward ratio.
4. **🧠 Decision Agent (Groq LLM):** Acts as the central orchestrator. It ingests the data from the other three agents and uses a Large Language Model to synthesize the information, providing a final "BUY" or "SELL" recommendation alongside a detailed, human-readable justification.

## 🏆 Model Benchmarking
This project includes a rigorous benchmarking suite (`accuracy_comparison.py`) that evaluates our predictive models against standard financial baseline tests. We compare the performance of:
* **Random Baseline** (50% probability simulation)
* **Linear Regression (LR)** (Trend-following)
* **XGBoost Classifier** (Complex non-linear pattern recognition)
* **QuantAgent (Supercharged Random Forest)** (Our custom engineered model utilizing extended market memory and exclusive momentum/volatility features)

## ⚙️ Installation & Setup

**1. Clone the repository:**
```bash
git clone [https://github.com/YOUR_USERNAME/QuantAgent-India.git](https://github.com/YOUR_USERNAME/QuantAgent-India.git)
cd QuantAgent-India