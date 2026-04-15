import ta
import pandas as pd


def load_stock(ticker_name: str) -> pd.DataFrame:
    """Load and clean stock data properly."""
    path = f"data/{ticker_name}_daily.csv"

    df = pd.read_csv(path)

    # Drop first row if it contains ticker header info
    if df.iloc[0].astype(str).str.contains(
        'Ticker|Price|RELIANCE|TCS|INFY|NS'
    ).any():
        df = df.iloc[1:].reset_index(drop=True)

    # Clean column names
    df.columns = [c.strip() for c in df.columns]

    # Rename first column to Date
    first_col = df.columns[0]
    df = df.rename(columns={first_col: 'Date'})

    # Convert date safely
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df = df.set_index('Date')

    # Convert all price columns to numbers
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)
    return df


def compute_indicators(df: pd.DataFrame) -> dict:
    """
    Takes a DataFrame with OHLC columns.
    Returns all 5 indicator values as a dictionary.
    """
    close = df["Close"].squeeze()
    high  = df["High"].squeeze()
    low   = df["Low"].squeeze()

    # 1. RSI
    rsi = ta.momentum.RSIIndicator(
        close, window=14
    ).rsi().iloc[-1]

    # 2. MACD
    macd_obj    = ta.trend.MACD(close)
    macd        = macd_obj.macd().iloc[-1]
    macd_signal = macd_obj.macd_signal().iloc[-1]
    macd_hist   = macd_obj.macd_diff().iloc[-1]

    # 3. ROC
    roc = ta.momentum.ROCIndicator(
        close, window=12
    ).roc().iloc[-1]

    # 4. Stochastic
    stoch   = ta.momentum.StochasticOscillator(high, low, close)
    stoch_k = stoch.stoch().iloc[-1]
    stoch_d = stoch.stoch_signal().iloc[-1]

    # 5. Williams %R
    williams_r = ta.momentum.WilliamsRIndicator(
        high, low, close
    ).williams_r().iloc[-1]

    return {
        "RSI":         round(float(rsi), 2),
        "MACD":        round(float(macd), 4),
        "MACD_signal": round(float(macd_signal), 4),
        "MACD_hist":   round(float(macd_hist), 4),
        "ROC":         round(float(roc), 2),
        "Stoch_K":     round(float(stoch_k), 2),
        "Stoch_D":     round(float(stoch_d), 2),
        "Williams_R":  round(float(williams_r), 2)
    }


def interpret_indicators(indicators: dict) -> str:
    """
    Converts indicator values into plain English
    for the LLM prompt.
    """
    lines = []

    # RSI
    rsi = indicators["RSI"]
    if rsi > 70:
        lines.append(f"RSI is {rsi} — overbought, possible price drop soon.")
    elif rsi < 30:
        lines.append(f"RSI is {rsi} — oversold, possible price bounce soon.")
    else:
        lines.append(f"RSI is {rsi} — neutral zone.")

    # MACD
    if indicators["MACD_hist"] > 0:
        lines.append("MACD histogram positive — bullish momentum.")
    else:
        lines.append("MACD histogram negative — bearish momentum.")

    # ROC
    if indicators["ROC"] > 0:
        lines.append(f"ROC is {indicators['ROC']}% — price accelerating upward.")
    else:
        lines.append(f"ROC is {indicators['ROC']}% — price slowing or falling.")

    # Stochastic
    if indicators["Stoch_K"] > 80:
        lines.append("Stochastic overbought — caution on buying.")
    elif indicators["Stoch_K"] < 20:
        lines.append("Stochastic oversold — possible bounce coming.")
    else:
        lines.append(f"Stochastic K is {indicators['Stoch_K']} — neutral.")

    # Williams %R
    if indicators["Williams_R"] > -20:
        lines.append("Williams %R overbought.")
    elif indicators["Williams_R"] < -80:
        lines.append("Williams %R oversold.")
    else:
        lines.append(f"Williams %R is {indicators['Williams_R']} — neutral.")

    return "\n".join(lines)