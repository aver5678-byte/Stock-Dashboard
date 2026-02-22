import yfinance as yf
import pandas as pd

df = yf.download('^TWII', start='2000-01-01', end='2021-12-31')
df.columns = df.columns.get_level_values(0)

peaks = []
in_dd = False
peak_val = df['High'].iloc[0]
peak_date = df.index[0]
lowest_val = peak_val
lowest_date = peak_date

events = []
for date, row in df.iterrows():
    high, low, close = row['High'], row['Low'], row['Close']
    if not in_dd:
        if high >= peak_val:
            peak_val = high
            peak_date = date
        if (peak_val - close) / peak_val >= 0.07:
            in_dd = True
            lowest_val = low
            lowest_date = date
    else:
        if low <= lowest_val:
            lowest_val = low
            lowest_date = date
        # If recovers absolute high OR 15% bounce from absolute bottom
        if high >= peak_val or (close - lowest_val)/lowest_val >= 0.15:
            # We save the event
            events.append({
                'p': peak_date.strftime('%Y-%m-%d'),
                'b': lowest_date.strftime('%Y-%m-%d'),
                'pv': peak_val,
                'bv': lowest_val,
                'dd': (peak_val - lowest_val) / peak_val * 100
            })
            in_dd = False
            peak_val = high
            peak_date = date

df_ev = pd.DataFrame(events)
print("=== 2000-2021 TAIWAN WEIGHTED INDEX RECORD ===")
for _, r in df_ev.iterrows():
    if r['dd'] >= 7.0:
        print(f"📅 {r['p']} ➔ {r['b']}  {int(r['pv']):,}➔{int(r['bv']):,}  -{r['dd']:.1f}%")
