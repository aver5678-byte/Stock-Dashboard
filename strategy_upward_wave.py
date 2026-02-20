import pandas as pd
import numpy as np

def get_upward_waves(events_df, df):
    if events_df.empty:
        return pd.DataFrame(), pd.DataFrame(), {}
    
    up_waves = []
    
    for i in range(len(events_df)):
        event = events_df.iloc[i]
        start_date = event['破底日期']
        start_price = event['破底最低價']
        
        if i < len(events_df) - 1:
            next_event = events_df.iloc[i+1]
            end_date = next_event['前高日期']
            end_price = next_event['前高價格']
            status = '已完結'
        else:
            if event['狀態'] == '進行中':
                continue
            else:
                rec_date = event['解套日期']
                try:
                    recent_df = df.loc[rec_date:]
                    if not recent_df.empty:
                        max_idx = recent_df['High'].idxmax()
                        end_date = max_idx.strftime('%Y-%m-%d')
                        end_price = recent_df.loc[max_idx, 'High']
                    else:
                        end_date = df.index[-1].strftime('%Y-%m-%d')
                        end_price = df['High'].iloc[-1]
                except:
                    end_date = df.index[-1].strftime('%Y-%m-%d')
                    end_price = df['High'].iloc[-1]
                status = '進行中'
        
        if start_price > 0:
            gain_pct = (end_price - start_price) / start_price * 100
            try:
                days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
            except:
                days = 0
                
            up_waves.append({
                '起漲日期 (前波破底)': start_date,
                '最高日期 (下波前高)': end_date,
                '起漲價格': round(float(start_price), 2),
                '最高價格': round(float(end_price), 2),
                '漲幅(%)': round(float(gain_pct), 2),
                '花費天數': int(days),
                '狀態': status
            })
            
    up_df = pd.DataFrame(up_waves)
    
    if up_df.empty:
        return up_df, pd.DataFrame(), {}
        
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 10000]
    labels = ['0% ~ 10%', '10% ~ 20%', '20% ~ 30%', '30% ~ 40%', '40% ~ 50%', '50% ~ 60%', '60% ~ 70%', '70% 以上']
    
    finished_waves = up_df[up_df['狀態'] == '已完結']
    if finished_waves.empty:
        finished_waves = up_df
        
    counts = pd.cut(finished_waves['漲幅(%)'], bins=bins, labels=labels, right=False).value_counts().sort_index()
    
    dist_results = []
    total = len(finished_waves)
    for label, count in counts.items():
        prob = (count / total * 100) if total > 0 else 0
        dist_results.append({
            '區間': label,
            '次數': count,
            '機率(%)': round(float(prob), 2)
        })
    dist_df = pd.DataFrame(dist_results)
    
    metrics = {
        '總完整波段數': total,
        '平均漲幅(%)': round(float(finished_waves['漲幅(%)'].mean()), 2) if total > 0 else 0,
        '平均花費天數': round(float(finished_waves['花費天數'].mean()), 1) if total > 0 else 0,
        '漲幅超過 20% 機率': round(float(len(finished_waves[finished_waves['漲幅(%)'] >= 20]) / total * 100), 2) if total > 0 else 0
    }
        
    return up_df, dist_df, metrics
