import yfinance as yf
import pandas as pd

periods = [
    {"start": "2024-04-01", "peak_date": "2024-07-11", "peak_val": 24416},
    {"start": "2020-12-01", "peak_date": "2022-01-05", "peak_val": 18619},
    {"start": "2009-11-01", "peak_date": "2011-01-28", "peak_val": 9220},
    {"start": "2007-09-01", "peak_date": "2007-10-30", "peak_val": 9859},
    {"start": "2003-12-01", "peak_date": "2004-03-05", "peak_val": 7135},
    {"start": "2000-01-01", "peak_date": "2000-02-18", "peak_val": 10393},
    {"start": "1997-06-01", "peak_date": "1997-08-27", "peak_val": 10256}, # Added a missing one if needed
    {"start": "1994-06-01", "peak_date": "1994-10-03", "peak_val": 7228},
]

# Note: ^TWII might not have very old data in yfinance, let's check.
# If not ^TWII, I will search for them.
data_list = []
for p in periods:
    try:
        df = yf.download("^TWII", start=p["start"], end=pd.to_datetime(p["start"]) + pd.Timedelta(days=10))
        if not df.empty:
            start_val = df['Close'].iloc[0]
            if isinstance(start_val, pd.Series): start_val = start_val.iloc[0]
            data_list.append({
                "period_start": p["start"],
                "start_index": round(float(start_val), 0),
                "peak_date": p["peak_date"],
                "peak_index": p["peak_val"],
                "gain": round(p["peak_val"] - float(start_val), 0),
                "pct": round((p["peak_val"] / float(start_val) - 1) * 100, 2)
            })
        else:
            print(f"No data for {p['start']}")
    except Exception as e:
        print(f"Error for {p['start']}: {e}")

print(pd.DataFrame(data_list))
