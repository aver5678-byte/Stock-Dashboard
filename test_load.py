import yfinance as yf
import pandas as pd
import datetime

def load_data():
    ticker = "^TWII"
    try:
        print("Fetching data from yfinance...")
        df_daily = yf.download(ticker, period="3y", interval="1d", threads=False, progress=False) # Skip 28y to be fast
        if df_daily.empty:
            print("Dataframe is empty!")
            return pd.DataFrame()
            
        if isinstance(df_daily.columns, pd.MultiIndex):
            df_daily.columns = df_daily.columns.get_level_values(0)
            
        latest_trade_date = df_daily.index[-1]
        print(f"Latest trade date: {latest_trade_date}")
            
        logic = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
        df = df_daily.resample('W-MON', label='left', closed='left').apply(logic)
        
        df_daily['temp_date'] = df_daily.index
        week_info = df_daily.resample('W-MON', label='left', closed='left')['temp_date'].agg(['min', 'max'])
        
        df['WeekRange'] = week_info.apply(
            lambda x: f"{x['min'].strftime('%Y/%m/%d')} ~ {x['max'].strftime('%m/%d')}" 
            if pd.notna(x['min']) and pd.notna(x['max']) and x['min'] != x['max']
            else (f"{x['min'].strftime('%Y/%m/%d')}" if pd.notna(x['min']) else "N/A"), axis=1
        )
        
        df = df.dropna(subset=['Close'])
        df['SMA40'] = df['Close'].rolling(window=40).mean()
        df['Bias'] = (df['Close'] - df['SMA40']) / df['SMA40'] * 100
        
        print("Data loaded successfully.")
        print(df.tail(2))
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    load_data()
