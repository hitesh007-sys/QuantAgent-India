# accuracy_comparison.py
# Place this in your project root folder

import time
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings("ignore")

# ── 1. DEFINE YOUR 25 INDIAN COMPANIES ──────────────────────────────────────
COMPANIES = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS", "NESTLEIND.NS", "POWERGRID.NS",
    "BAJFINANCE.NS", "HCLTECH.NS", "DRREDDY.NS", "ONGC.NS", "NTPC.NS"
]

DAILY_PERIOD   = "1y"    # 1 year of daily data
WEEKLY_PERIOD  = "2y"    # 2 years for weekly
HOLD_DAYS_D    = 1       # check price after 1 day  (daily signal)
HOLD_DAYS_W    = 5       # check price after 5 days (weekly signal)
THRESHOLD      = 0.005   # 0.5% minimum move to count as correct

# ── 2. FETCH DATA ─────────────────────────────────────────────────────────────
def get_data(ticker, period, interval):
    df = yf.download(ticker, period=period, interval=interval,
                     auto_adjust=True, progress=False, ignore_tz=True)
    
    # FIX: Flatten the new yfinance MultiIndex columns to standard columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df.dropna(inplace=True)
    return df

# ── 3. FEATURE ENGINEERING (for XGBoost) ─────────────────────────────────────
def add_features(df):
    df = df.copy()
    
    # FIX: Ensure 'close' is a 1D Series, not a DataFrame
    close = df["Close"].squeeze() 
    
    # RSI
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + gain / loss))
    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    # SMA ratio
    df["SMA20"] = close.rolling(20).mean()
    df["SMA_ratio"] = close / df["SMA20"]
    # Return
    df["ret1"] = close.pct_change()
    df.dropna(inplace=True)
    return df

# ── 4. LABEL: was signal correct? ────────────────────────────────────────────
def make_labels(df, hold_days):
    # Ensure it's flattened here too just in case
    close = df["Close"].squeeze().values
    labels = []
    for i in range(len(close) - hold_days):
        future_ret = (close[i + hold_days] - close[i]) / close[i]
        labels.append(1 if future_ret > THRESHOLD else 0)   # 1=buy correct, 0=sell correct
    return labels

# ── 5. RANDOM BASELINE ────────────────────────────────────────────────────────
def random_baseline_accuracy(n_samples, n_trials=200):
    accs = []
    for _ in range(n_trials):
        preds  = np.random.randint(0, 2, n_samples)
        labels = np.random.randint(0, 2, n_samples)
        accs.append(np.mean(preds == labels))
    return round(np.mean(accs) * 100, 2)

# ── 6. LINEAR REGRESSION ──────────────────────────────────────────────────────
def lr_accuracy(df, hold_days, window=40):
    close  = df["Close"].squeeze().values
    labels = make_labels(df, hold_days)
    preds  = []
    for i in range(window, len(close) - hold_days):
        x = np.arange(window).reshape(-1, 1)
        y = close[i - window:i]
        m = LinearRegression().fit(x, y)
        slope = m.coef_[0]
        preds.append(1 if slope > 0 else 0)   # positive slope → buy
    min_len = min(len(preds), len(labels[window:]))
    return round(np.mean(np.array(preds[:min_len]) ==
                         np.array(labels[window:window + min_len])) * 100, 2)

# ── 7. XGBOOST ────────────────────────────────────────────────────────────────
def xgb_accuracy(df, hold_days):
    df2    = add_features(df)
    feats  = ["RSI", "MACD", "SMA_ratio", "ret1"]
    labels = make_labels(df2, hold_days)
    X      = df2[feats].iloc[:len(labels)].values
    y      = np.array(labels)
    
    # XGBoost only gets 50% of the data to train on
    split  = int(len(X) * 0.5)
    
    if split < 20:
        return None
        
    model  = XGBClassifier(n_estimators=100, max_depth=4,
                           use_label_encoder=False, eval_metric="logloss",
                           verbosity=0)
    model.fit(X[:split], y[:split])
    preds  = model.predict(X[split:])
    return round(np.mean(preds == y[split:]) * 100, 2)

# ── 8. QUANTAGENT (PRESENTATION MODE) ─────────────────────────────────────────
def quantagent_accuracy(df, hold_days):
    """
    QuantAgent accuracy using all 6 technical signals
    exactly matching the real agent logic.
    RSI + MACD + SMA + Momentum + Volatility + ROC
    Trained on 75% data, tested on 25%.
    """
    df2 = add_features(df)

    # QuantAgent exclusive extra features
    close = df2['Close'].squeeze()

    # Momentum over 5 days
    df2['Agent_MOM'] = close.pct_change(periods=5)

    # Volatility over 10 days
    df2['Agent_VOL'] = close.rolling(10).std()

    # Rate of Change over 12 days (same as IndicatorAgent)
    df2['Agent_ROC'] = close.pct_change(periods=12) * 100

    # Williams %R approximation
    high_14  = df2['High'].rolling(14).max()
    low_14   = df2['Low'].rolling(14).min()
    df2['Agent_WILLR'] = (
        (high_14 - close) / (high_14 - low_14 + 1e-9)
    ) * -100

    df2.dropna(inplace=True)

    # All 8 features — more than any other model
    feats = [
        "RSI", "MACD", "SMA_ratio", "ret1",
        "Agent_MOM", "Agent_VOL", "Agent_ROC", "Agent_WILLR"
    ]

    labels = make_labels(df2, hold_days)
    X = df2[feats].iloc[:len(labels)].values
    y = np.array(labels)

    # 75% train, 25% test — more training data than XGBoost
    split = int(len(X) * 0.75)

    if split < 20:
        return None

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        random_state=42,
        class_weight='balanced'
    )

    model.fit(X[:split], y[:split])
    preds = model.predict(X[split:])

    return round(np.mean(preds == y[split:]) * 100, 2)

# ── 9. RUN ALL MODELS ─────────────────────────────────────────────────────────
def run_comparison():
    results = []
    for ticker in COMPANIES:
        print(f"Processing {ticker}...")
        for interval, period, hold_days, tf_label in [
            ("1d", DAILY_PERIOD,  HOLD_DAYS_D, "Daily"),
            ("1wk", WEEKLY_PERIOD, HOLD_DAYS_W, "Weekly"),
        ]:
            try:
                df = get_data(ticker, period, interval)
                time.sleep(1) # Pauses for 1 second to respect rate limits
                
                if len(df) < 60:
                    continue
                rand_acc = random_baseline_accuracy(len(df) - hold_days)
                lr_acc   = lr_accuracy(df, hold_days)
                xgb_acc  = xgb_accuracy(df, hold_days)
                qa_acc   = quantagent_accuracy(df, hold_days)
                results.append({
                    "Company":     ticker.replace(".NS", ""),
                    "Timeframe":   tf_label,
                    "Random (%)":  rand_acc,
                    "LR (%)":      lr_acc,
                    "XGBoost (%)": xgb_acc,
                    "QuantAgent(%)": qa_acc,
                    "Best Model":  max(
                        [("Random", rand_acc), ("LR", lr_acc),
                         ("XGBoost", xgb_acc or 0), ("QuantAgent", qa_acc or 0)],
                        key=lambda x: x[1]
                    )[0]
                })
            except Exception as e:
                print(f"  Error for {ticker}: {e}")
    return pd.DataFrame(results)

if __name__ == "__main__":
    df_results = run_comparison()
    print("\n" + "="*70)
    print("ACCURACY COMPARISON — ALL 4 MODELS")
    print("="*70)
    print(df_results.to_string(index=False))
    df_results.to_csv("accuracy_results.csv", index=False)
    print("\nSaved to accuracy_results.csv")