import yfinance as yf
import pandas as pd

def find_all_events():
    ticker = "^TWII"
    df_daily = yf.download(ticker, start="1987-01-01", progress=False)
    if df_daily.empty: return
    if isinstance(df_daily.columns, pd.MultiIndex):
        df_daily.columns = df_daily.columns.get_level_values(0)
        
    df = df_daily.resample('W-MON').last()
    df['SMA40'] = df['Close'].rolling(window=40).mean()
    df['Bias'] = (df['Close'] - df['SMA40']) / df['SMA40'] * 100
    df = df.dropna(subset=['Bias'])
    
    events = []
    in_zone = False
    cur = None
    
    TRIGGER = 20.0
    RESET = 15.0
    
    for date, row in df.iterrows():
        bias = row['Bias']
        high = row['High']
        if not in_zone:
            if bias >= TRIGGER:
                in_zone = True
                cur = {'start': date, 'peak_date': date, 'peak_bias': bias, 'peak_price': high}
        else:
            if high > cur['peak_price']:
                cur['peak_price'] = high
                cur['peak_date'] = date
            if bias > cur['peak_bias']:
                cur['peak_bias'] = bias
                
            # Calibration
            prev_idx = df.index.get_loc(date) - 1
            if prev_idx >= 0:
                if df.iloc[prev_idx]['Bias'] < TRIGGER and bias >= TRIGGER:
                    cur['start'] = date
            
            if bias < RESET:
                cur['end'] = date
                events.append(cur)
                in_zone = False
    
    if in_zone:
        cur['end'] = "ACTIVE"
        events.append(cur)
        
    for i, e in enumerate(events):
        print(f"{i+1}: {e['start'].date()} | {e['peak_date'].date()} | {e['peak_bias']:.2f}% | {(e['peak_date']-e['start']).days}天")

find_all_events()
