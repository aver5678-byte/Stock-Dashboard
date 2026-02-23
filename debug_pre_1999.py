import yfinance as yf
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

def debug_specific_dates():
    ticker = "^TWII"
    df_daily = yf.download(ticker, start="1994-01-01", progress=False)
    
    if df_daily.empty:
        print("無法取得 yfinance 資料。")
        return
    
    # 扁平化 MultiIndex 欄位 (yfinance 新版行為)
    if isinstance(df_daily.columns, pd.MultiIndex):
        df_daily.columns = df_daily.columns.get_level_values(0)
        
    df = df_daily.resample('W-MON').last()
    df['SMA40'] = df['Close'].rolling(window=40).mean()
    df['Bias'] = (df['Close'] - df['SMA40']) / df['SMA40'] * 100
    
    check_dates = ['1996-04-08', '1997-03-03', '1997-06-30']
    
    print("--- 指定日期數據查核 (yfinance 源) ---")
    for d_str in check_dates:
        d = pd.to_datetime(d_str)
        if d in df.index:
            row = df.loc[d]
            print(f"日期: {d_str} | 收盤: {row['Close']:.2f} | 40W均線: {row['SMA40'] if not pd.isna(row['SMA40']) else 0:.2f} | 乖離率: {row['Bias'] if not pd.isna(row['Bias']) else 0:.2f}%")
        else:
            print(f"日期: {d_str} | 警告: yfinance 數據庫中查無此日。")

    print("\n--- 資料庫最早與最晚日期 ---")
    print(f"Start: {df_daily.index[0]}")
    print(f"End: {df_daily.index[-1]}")

debug_specific_dates()
