import yfinance as yf
import pandas as pd

def check_insider_data(symbol):
    print(f"--- Checking {symbol} ---")
    ticker = yf.Ticker(symbol)
    
    print("\n[Insider Transactions]")
    try:
        insider = ticker.insider_transactions
        if insider is not None and not insider.empty:
            print(insider.head())
        else:
            print("No insider transactions found.")
    except Exception as e:
        print(f"Error fetching insider transactions: {e}")

    print("\n[Major Holders]")
    try:
        major = ticker.major_holders
        if major is not None and not major.empty:
            print(major)
        else:
            print("No major holders found.")
    except Exception as e:
        print(f"Error fetching major holders: {e}")

if __name__ == "__main__":
    check_insider_data("NVDA")
    check_insider_data("AAPL")
