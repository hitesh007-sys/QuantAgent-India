import pandas as pd
import mplfinance as mpf
import os

def load_clean_data(ticker_name: str, n_bars: int = 50) -> pd.DataFrame:
    """Load and clean stock data properly."""
    path = f"data/{ticker_name}_daily.csv"
    
    # Read raw file
    df = pd.read_csv(path)
    
    # Drop first row if it contains ticker info
    if df.iloc[0].astype(str).str.contains('Ticker|Price|RELIANCE|TCS').any():
        df = df.iloc[1:].reset_index(drop=True)
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    
    # Rename first column to Date if needed
    first_col = df.columns[0]
    df = df.rename(columns={first_col: 'Date'})
    
    # Convert date
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df = df.set_index('Date')
    
    # Convert prices to numbers
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df.dropna(inplace=True)
    return df.tail(n_bars)


def generate_candlestick_chart(ticker_name: str, n_bars: int = 50) -> str:
    """Generates and saves candlestick chart. Returns path."""
    recent = load_clean_data(ticker_name, n_bars)
    os.makedirs("charts", exist_ok=True)
    save_path = f"charts/{ticker_name}_chart.png"
    mpf.plot(
        recent,
        type='candle',
        style='charles',
        title=f'{ticker_name} - Last {n_bars} Days',
        ylabel='Price (INR)',
        volume=False,
        savefig=dict(fname=save_path, dpi=80, format='png')
    )
    print(f"Chart saved: {save_path}")
    return save_path


def describe_chart_pattern(ticker_name: str, n_bars: int = 50) -> str:
    """Returns text description of price pattern for LLM."""
    recent = load_clean_data(ticker_name, n_bars)
    
    close = recent['Close']
    high  = recent['High']
    low   = recent['Low']

    current_price    = round(float(close.iloc[-1]), 2)
    highest_price    = round(float(high.max()), 2)
    lowest_price     = round(float(low.min()), 2)
    price_range      = round(highest_price - lowest_price, 2)
    start_price      = round(float(close.iloc[0]), 2)
    end_price        = round(float(close.iloc[-1]), 2)
    price_change     = round(end_price - start_price, 2)
    price_change_pct = round((price_change / start_price) * 100, 2)

    recent_10   = close.tail(10)
    recent_high = round(float(recent_10.max()), 2)
    recent_low  = round(float(recent_10.min()), 2)

    first_half  = close.iloc[:25]
    second_half = close.iloc[25:]
    first_avg   = round(float(first_half.mean()), 2)
    second_avg  = round(float(second_half.mean()), 2)

    if second_avg > first_avg * 1.02:
        trend_direction = "upward"
    elif second_avg < first_avg * 0.98:
        trend_direction = "downward"
    else:
        trend_direction = "sideways"

    mid   = len(close) // 2
    low1  = float(close.iloc[:mid].min())
    low2  = float(close.iloc[mid:].min())
    high1 = float(close.iloc[:mid].max())
    high2 = float(close.iloc[mid:].max())

    double_bottom_hint = abs(low1 - low2) / low1 < 0.03
    double_top_hint    = abs(high1 - high2) / high1 < 0.03

    description = f"""
Stock: {ticker_name}
Period: Last {n_bars} trading days
Current Price: {current_price}
Price {n_bars} days ago: {start_price}
Overall Change: {price_change} ({price_change_pct}%)
Highest Price in period: {highest_price}
Lowest Price in period: {lowest_price}
Price Range: {price_range}
Recent 10-day High: {recent_high}
Recent 10-day Low: {recent_low}
Overall Trend Direction: {trend_direction}
Possible Double Bottom: {double_bottom_hint}
Possible Double Top: {double_top_hint}
First half average price: {first_avg}
Second half average price: {second_avg}
"""
    return description.strip()