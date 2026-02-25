import yfinance as yf
import pandas as pd

def fetch_data(ticker, start_date="2000-01-01"):
    """
    Fetch historical daily data from Yahoo Finance.
    
    Args:
        ticker (str): The ticker symbol (e.g., '^GSPC' for S&P 500, '^IXIC' for NASDAQ, '^TWII' for Taiwan)
        start_date (str): The start date in YYYY-MM-DD format.
        
    Returns:
        pd.DataFrame: DataFrame containing Date, High, Low, Close prices.
    """
    print(f"Fetching data for {ticker} from {start_date}...")
    df = yf.download(ticker, start=start_date)
    
    if df.empty:
        raise ValueError(f"No data found for ticker {ticker}.")
        
    # Handle multi-level columns if present (yfinance >= 0.2.0 behavior)
    if isinstance(df.columns, pd.MultiIndex):
        # Extract columns for this specific ticker
        if ticker in df.columns.levels[1]:
            df = df.xs(ticker, axis=1, level=1)
        else:
            # Maybe the top level is Price, and bottom is ticker, let's flatten or just take the first level
            df.columns = [col[0] for col in df.columns]
            
    # Keep only needed columns and drop missing values
    columns_to_keep = ['High', 'Low', 'Close']
    missing_cols = [c for c in columns_to_keep if c not in df.columns]
    if missing_cols:
         raise ValueError(f"Missing columns: {missing_cols}. Available columns: {df.columns}")
         
    df = df[columns_to_keep].dropna()
    
    return df
