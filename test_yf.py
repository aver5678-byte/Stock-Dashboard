import yfinance as yf
import pandas as pd

ticker = "^TWII"
start_date = "2024-01-01"
df = yf.download(ticker, start=start_date, threads=False, progress=False)
print("Columns type:", type(df.columns))
print("Columns:", df.columns)
print("Head:\n", df.head())
