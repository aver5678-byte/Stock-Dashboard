import yfinance as yf
import pandas as pd
import datetime
import sys

# 強制輸出為 UTF-8 避免亂碼
sys.stdout.reconfigure(encoding='utf-8')

def verify_history_since_1996():
    ticker = "^TWII"
    # 為了讓 1996-01-01 有準確的 SMA40，提前抓 100 週
    df_daily = yf.download(ticker, start="1994-01-01", progress=False) 
    
    if df_daily.empty:
        print("無法取得 yfinance 資料。")
        return
        
    if isinstance(df_daily.columns, pd.MultiIndex):
        df_daily.columns = df_daily.columns.get_level_values(0)
        
    df = df_daily.resample('W-MON').last()
    df['SMA40'] = df['Close'].rolling(window=40).mean()
    df['Bias'] = (df['Close'] - df['SMA40']) / df['SMA40'] * 100
    df = df.dropna(subset=['Bias'])
    
    # 鎖定在 1996 年開始
    df = df[df.index >= '1996-01-01']
    
    events = []
    in_event = False 
    current_event = None
    
    TRIGGER_LEVEL = 20.0
    RESET_LEVEL = 15.0
    
    for date, row in df.iterrows():
        bias = row['Bias']
        price = row['High'] # 使用 High 抓取最高點
        
        if not in_event:
            if bias >= TRIGGER_LEVEL:
                in_event = True
                current_event = {
                    'original_start': date,
                    'calibrated_start': date,
                    'peak_date': date,
                    'peak_price': price,
                    'peak_bias': bias,
                }
        else:
            # 追蹤最高點
            if price > current_event['peak_price']:
                current_event['peak_price'] = price
                current_event['peak_date'] = date
            if bias > current_event['peak_bias']:
                current_event['peak_bias'] = bias
            
            # 再發動校準邏輯 (核心：若之前低於 20 但沒破 15，現在又站上 20)
            prev_idx = df.index.get_loc(date) - 1
            if prev_idx >= 0:
                prev_bias = df.iloc[prev_idx]['Bias']
                if prev_bias < TRIGGER_LEVEL and bias >= TRIGGER_LEVEL:
                    # 更新起點為最後一次衝破 20% 的日期
                    current_event['calibrated_start'] = date
            
            # 結束判定：跌破 15%
            if bias < RESET_LEVEL:
                current_event['end_date'] = date
                events.append(current_event)
                in_event = False
                current_event = None

    if in_event:
        current_event['end_date'] = "ACTIVE"
        events.append(current_event)

    print(f"--- 台股 40週乖離率 20% 歷史事件表 (1996-2026) ---")
    data_list = []
    for i, e in enumerate(events):
        days = (e['peak_date'] - e['calibrated_start']).days
        status = "已結案" if e['end_date'] != "ACTIVE" else "進行中"
        data_list.append({
            '序號': i + 1,
            '觸發日期': e['calibrated_start'].strftime('%Y-%m-%d'),
            '最高日期': e['peak_date'].strftime('%Y-%m-%d'),
            '最高乖離': f"{e['peak_bias']:.2f}%",
            '見頂天數': f"{days}天",
            '狀態': status
        })
    
    # 使用 Pandas 印出漂亮表格
    verify_df = pd.DataFrame(data_list)
    print(verify_df.to_string(index=False))

verify_history_since_1996()
