import yfinance as yf
import pandas as pd

# 週期對應表 (信號月份 -> 投資人反應月份)
# 邏輯：月份 M 的信號在 M+1 月底發布，M+2 月初反應
target_dates = [
    {"signal": "2024.04", "action_month": "2024-06-01", "peak": 24416},
    {"signal": "2020.12", "action_month": "2021-02-01", "peak": 18619},
    {"signal": "2009.11", "action_month": "2010-01-01", "peak": 9220},
    {"signal": "2007.09", "action_month": "2007-11-01", "peak": 9859},
    {"signal": "2003.12", "action_month": "2004-02-01", "peak": 7135},
    {"signal": "2000.01", "action_month": "2000-03-01", "peak": 10393},
    {"signal": "1994.06", "action_month": "1994-08-01", "peak": 7228},
]

results = []
for item in target_dates:
    start_search = item["action_month"]
    end_search = (pd.to_datetime(start_search) + pd.Timedelta(days=20)).strftime("%Y-%m-%d")
    try:
        df = yf.download("^TWII", start=start_search, end=end_search)
        if not df.empty:
            actual_date = df.index[0]
            close_val = df['Close'].iloc[0]
            if isinstance(close_val, pd.Series): close_val = close_val.iloc[0]
            
            results.append({
                "signal": item["signal"],
                "action_date": actual_date.strftime("%Y/%m/%d"),
                "start_idx": round(float(close_val), 0),
                "peak_idx": item["peak"],
                "new_gain": round((item["peak"] / float(close_val) - 1) * 100, 1)
            })
        else:
            print(f"No data for {start_search}")
    except Exception as e:
        print(f"Error for {start_search}: {e}")

print(pd.DataFrame(results))
