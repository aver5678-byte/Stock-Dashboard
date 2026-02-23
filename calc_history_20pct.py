import yfinance as yf
import pandas as pd
import datetime

def verify_history_refined():
    ticker = "^TWII"
    df_daily = yf.download(ticker, start="1987-01-01", progress=False) # 抓早一點確保 SMA40 準確
    
    if df_daily.empty:
        return
        
    if isinstance(df_daily.columns, pd.MultiIndex):
        df_daily.columns = df_daily.columns.get_level_values(0)
        
    df = df_daily.resample('W-MON').last()
    df['SMA40'] = df['Close'].rolling(window=40).mean()
    df['Bias'] = (df['Close'] - df['SMA40']) / df['SMA40'] * 100
    df = df.dropna(subset=['Bias'])
    
    # 僅保留 1989 年以後的資料
    df = df[df.index >= '1989-01-01']
    
    events = []
    
    in_trigger_zone = False # 是否處於 >= 20% 的狀態
    current_event = None
    
    for date, row in df.iterrows():
        bias = row['Bias']
        price = row['High']
        
        # 門檻定義
        TRIGGER_LEVEL = 20.0
        RESET_LEVEL = 15.0
        EXIT_LEVEL = 0.0
        
        if not in_trigger_zone:
            if bias >= TRIGGER_LEVEL:
                in_trigger_zone = True
                current_event = {
                    '觸發起點': date,
                    '原初起點': date,
                    '最高點日期': date,
                    '最高價': price,
                    '最高乖離': bias,
                    '狀態': 'RUNNING'
                }
        else:
            # 追蹤最高點
            if price > current_event['最高價']:
                current_event['最高價'] = price
                current_event['最高點日期'] = date
            if bias > current_event['最高乖離']:
                current_event['最高乖離'] = bias
            
            # 處理再發動 (校準邏輯)
            # 如果之前掉下去過 (但沒破 15)，現在又重新站上 20
            # 我們檢查前一週是否低於 20 且本週回到 20
            # 這裡簡化邏輯：如果在 zone 裡面，且目前 bias 重新穿越 20
            # 為了避免頻繁跳動，我們定義：如果過去幾週曾低於 20 但高於 15，現在站回 20，重置起點
            # 但實務上使用者要的是「最後一波發動點」
            
            # 重置判定：如果 bias 之前掉到 20 以下 (但 >= 15)，這週又回到 20
            # 我們需要知道「上週狀態」
            prev_idx = df.index.get_loc(date) - 1
            if prev_idx >= 0:
                prev_bias = df.iloc[prev_idx]['Bias']
                if prev_bias < TRIGGER_LEVEL and bias >= TRIGGER_LEVEL:
                    if prev_bias >= RESET_LEVEL:
                        # 本週是「重新站上」，校準起點
                        current_event['觸發起點'] = date
            
            # 結束判定：徹底跌破 15% 或 0%
            # 注意：使用者說「跌落 20 跌破 15 才算重置」，或者「跌破 0 才算結案」
            # 這裡我們採用：跌破 15% 就結案 (因為這代表熱度已退，下次再上算新事件)
            if bias < RESET_LEVEL:
                current_event['結束日期'] = date
                events.append(current_event)
                in_trigger_zone = False
                current_event = None
            elif bias < EXIT_LEVEL: # 安全起見
                current_event['結束日期'] = date
                events.append(current_event)
                in_trigger_zone = False
                current_event = None

    if in_trigger_zone:
        current_event['結束日期'] = "進行中"
        events.append(current_event)

    print(f"| 序號 | 觸發起點 (校準後) | 最高點日期 | 最高乖離 | 見頂天數 | 結束日期 |")
    print(f"| :--- | :--- | :--- | :--- | :--- | :--- |")
    for i, e in enumerate(events):
        days = (e['最高點日期'] - e['觸發起點']).days
        print(f"| {i+1} | {e['觸發起點'].date()} | {e['最高點日期'].date()} | {e['最高乖離']:.2f}% | {days}天 | {e['結束日期'] if isinstance(e['結束日期'], str) else e['結束日期'].date()} |")

verify_history_refined()
