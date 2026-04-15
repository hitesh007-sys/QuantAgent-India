import sys
sys.path.append('tools')

from compute_indicators import load_stock, compute_indicators

stocks = [
    'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK',
    'HINDUNILVR', 'SBIN', 'BHARTIARTL', 'WIPRO', 'LT',
    'ADANIENT', 'KOTAKBANK', 'AXISBANK', 'HCLTECH', 'ITC',
    'SUNPHARMA', 'MARUTI', 'BAJFINANCE', 'TECHM', 'TITAN',
    'ULTRACEMCO', 'NESTLEIND', 'POWERGRID', 'ONGC', 'NTPC'
]

print("Testing all 25 stocks...\n")

success = 0
failed = 0

for stock in stocks:
    try:
        df = load_stock(stock)
        ind = compute_indicators(df)
        print(f"✓ {stock}: RSI={ind['RSI']} | MACD={ind['MACD']} | ROC={ind['ROC']}")
        success += 1
    except Exception as e:
        print(f"✗ {stock}: ERROR — {e}")
        failed += 1

print(f"\nDone! Success: {success} | Failed: {failed}")