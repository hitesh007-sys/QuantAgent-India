import yfinance as yf
import pandas as pd
import os
import time

STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "WIPRO.NS", "LT.NS",
    "ADANIENT.NS", "KOTAKBANK.NS", "AXISBANK.NS", "HCLTECH.NS", "ITC.NS",
    "SUNPHARMA.NS", "MARUTI.NS", "BAJFINANCE.NS", "TECHM.NS", "TITAN.NS",
    "ULTRACEMCO.NS", "NESTLEIND.NS", "POWERGRID.NS", "ONGC.NS", "NTPC.NS"
]

def fetch_all_stocks():
    os.makedirs("data", exist_ok=True)

    for ticker in STOCKS:
        print(f"Fetching {ticker}...")
        try:
            # Daily data for 3 years
            df = yf.download(ticker, period="3y", interval="1d", auto_adjust=True)
            df.dropna(inplace=True)

            if len(df) < 10:
                print(f"  WARNING: Very little data for {ticker}, skipping.")
                continue

            name = ticker.replace(".NS", "")
            df.to_csv(f"data/{name}_daily.csv")
            print(f"  Saved {name}_daily.csv — {len(df)} rows")

        except Exception as e:
            print(f"  ERROR fetching {ticker}: {e}")

        time.sleep(1)  # avoid rate limiting

    print("\nAll stocks fetched successfully!")

if __name__ == "__main__":
    fetch_all_stocks()