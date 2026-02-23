import yfinance as yf
import pandas as pd
import datetime
import sys

# 強制輸出為 UTF-8 避免亂碼
sys.stdout.reconfigure(encoding='utf-8')

def verify_history_refined():
    ticker = "^TWII"
    # yfinance ^TWII 通常從 1997 年才有資料，我們盡力抓取
    df_daily = yf.download(ticker, start="1990-01-01", progress=False) 
    
    if df_daily.empty:
        print("無法取得 yfinance 資料。")
        return
        
    if isinstance(df_daily.columns, pd.MultiIndex):
        df_daily.columns = df_daily.columns.get_level_values(0)
        
    df = df_daily.resample('W-MON').last()
    df['SMA40'] = df['Close'].rolling(window=40).mean()
    df['Bias'] = (df['Close'] - df['SMA40']) / df['SMA40'] * 100
    df = df.dropna(subset=['Bias'])
    
    events = []
    in_trigger_zone = False 
    current_event = None
    
    TRIGGER_LEVEL = 20.0
    RESET_LEVEL = 15.0
    
    for date, row in df.iterrows():
        bias = row['Bias']
        price = row['High']
        
        if not in_trigger_zone:
            if bias >= TRIGGER_LEVEL:
                in_trigger_zone = True
                current_event = {
                    'start_date': date,
                    'calibrated_start': date,
                    'peak_date': date,
                    'peak_price': price,
                    'peak_bias': bias,
                }
        else:
            if price > current_event['peak_price']:
                current_event['peak_price'] = price
                current_event['peak_date'] = date
            if bias > current_event['peak_bias']:
                current_event['peak_bias'] = bias
            
            # 再發動校準邏輯
            prev_idx = df.index.get_loc(date) - 1
            if prev_idx >= 0:
                prev_bias = df.iloc[prev_idx]['Bias']
                if prev_bias < TRIGGER_LEVEL and bias >= TRIGGER_LEVEL:
                    # 重新站上，且之前沒破 15 (因為破 15 就會結束事件了)
                    current_event['calibrated_start'] = date
            
            # 結束判定
            if bias < RESET_LEVEL:
                current_event['end_date'] = date
                events.append(current_event)
                in_trigger_zone = False
                current_event = None

    if in_trigger_zone:
        current_event['end_date'] = "ACTIVE"
        events.append(current_event)

    print("--- 台股 40週乖離率 20% 門檻歷史事件表 (1997-2026) ---")
    print(f"{'序號':<4} | {'觸發日期':<12} | {'最高日期':<12} | {'最高乖離':<8} | {'見頂天數':<6} | {'狀態'}")
    print("-" * 75)
    for i, e in enumerate(events):
        days = (e['peak_date'] - e['calibrated_start']).days
        status = "已結案" if e['end_date'] != "ACTIVE" else "進行中"
        print(f"{i+1:<4} | {str(e['calibrated_start'].date()):<12} | {str(e['peak_date'].date()):<12} | {e['peak_bias']:>7.2f}% | {days:>4}天 | {status}")

verify_history_refined()
