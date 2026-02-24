import yfinance as yf
import pandas as pd
import datetime

def get_regime(df, start_date):
    prev_52w = df.loc[:start_date].iloc[:-1].tail(52)
    if prev_52w.empty:
        return "未知", 0
    roll_max = prev_52w['High'].cummax()
    max_dd = ((prev_52w['Low'] - roll_max) / roll_max).min() * 100
    if max_dd < -20:
        return "類型 A (低基期反彈)", max_dd
    else:
        return "類型 B (高位末升段)", max_dd

def backtest(df):
    results = []
    in_danger = False
    start_date = None
    trigger_price = None
    trigger_bias = None
    trigger_warning_price = None
    max_price = 0
    max_date = None
    regime = None
    max_dd = 0
    
    TRIGGER_LEVEL = 20.0
    RESET_LEVEL = 15.0
    
    for date, row in df.iterrows():
        bias = row['Bias']
        close_p = row['Close']
        if pd.isna(bias):
            continue
            
        if not in_danger:
            if bias >= TRIGGER_LEVEL:
                in_danger = True
                start_date = date
                trigger_price = close_p
                trigger_bias = bias
                trigger_warning_price = row['SMA40'] * (1 + TRIGGER_LEVEL/100)
                max_price = close_p
                max_date = date
                regime, max_dd = get_regime(df, date)
        else:
            curr_high = row['High']
            if curr_high > max_price:
                max_price = curr_high
                max_date = date
            if bias > trigger_bias:
                trigger_bias = bias
                
            # 結束判定：跌破 15% (視為此度熱度結案)
            if bias < RESET_LEVEL:
                in_danger = False
                end_date = date
                drop_price = close_p
                max_surge = (max_price - trigger_price) / trigger_price * 100 if trigger_price and trigger_price != 0 else 0
                total_drop = (drop_price - max_price) / max_price * 100 if max_price and max_price != 0 else 0
                weeks = int((end_date - start_date).days) if start_date and end_date else 0
                results.append({
                    '觸發日期': start_date.strftime('%Y-%m-%d'),
                    '波段最高日期': max_date.strftime('%Y-%m-%d'),
                    '回歸0%日期': end_date.strftime('%Y-%m-%d'),
                })
    return results

ticker = "^TWII"
df_long = yf.download(ticker, start="2010-01-01", end="2021-12-31", interval="1d", progress=False)
if isinstance(df_long.columns, pd.MultiIndex):
    df_long.columns = df_long.columns.get_level_values(0)
logic = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}
df = df_long.resample('W-MON', label='left', closed='left').apply(logic)
df = df.dropna(subset=['Close'])
df['SMA40'] = df['Close'].rolling(window=40).mean()
df['Bias'] = (df['Close'] - df['SMA40']) / df['SMA40'] * 100

res = backtest(df)
for r in res:
    if "2021" in r['觸發日期']:
        print(r)
