import yfinance as yf
import pandas as pd

ticker = "^TWII"
df_long = yf.download(ticker, start="2010-01-01", end="2021-07-01", interval="1d", progress=False)
if isinstance(df_long.columns, pd.MultiIndex):
    df_long.columns = df_long.columns.get_level_values(0)

logic = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}
df = df_long.resample('W-MON', label='left', closed='left').apply(logic)
# Filter NaNs first!
df = df.dropna(subset=['Close'])
df['SMA40'] = df['Close'].rolling(window=40).mean()
df['Bias'] = (df['Close'] - df['SMA40']) / df['SMA40'] * 100

print(df.loc['2021-03-01':'2021-06-01', ['Close', 'Bias', 'SMA40']])
