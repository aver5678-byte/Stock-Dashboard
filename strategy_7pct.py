import pandas as pd
import numpy as np

def analyze_7pct_strategy(df, trigger_pct=7.0):
    """
    Analyze the 7% drawdown entry strategy.
    
    Args:
        df: DataFrame containing 'High', 'Low', 'Close' columns and DatetimeIndex.
        trigger_pct: Percentage drop to trigger entry (e.g., 7.0 for 7%).
        
    Returns:
        pd.DataFrame: A DataFrame of all triggered events and their follow-up metrics.
    """
    if len(df) == 0:
        return pd.DataFrame()
        
    events = []
    
    in_drawdown = False
    current_high = df['High'].iloc[0]
    current_high_date = df.index[0]
    
    trigger_date = None
    trigger_price = None
    
    lowest_since_trigger = None
    lowest_date = None
    
    for date, row in df.iterrows():
        high = row['High']
        low = row['Low']
        close = row['Close']
        
        if not in_drawdown:
            # Update rolling high
            if high >= current_high:
                current_high = high
                current_high_date = date
                
            # Check for trigger
            drawdown = (current_high - close) / current_high * 100
            if drawdown >= trigger_pct:
                in_drawdown = True
                trigger_date = date
                trigger_price = close
                lowest_since_trigger = low
                lowest_date = date
        else:
            # We are in a drawdown
            if low < lowest_since_trigger:
                lowest_since_trigger = low
                lowest_date = date
                
            # Check for recovery (解套：只要漲回當初觸發買進的價格，即算本波段解套結案)
            if high >= trigger_price:
                # Event concluded
                max_drawdown = (current_high - lowest_since_trigger) / current_high * 100
                residual_drawdown = (trigger_price - lowest_since_trigger) / trigger_price * 100
                
                days_to_bottom = (lowest_date - trigger_date).days
                days_to_recovery = (date - trigger_date).days
                
                events.append({
                    '觸發日期': trigger_date.strftime('%Y-%m-%d'),
                    '前高日期': current_high_date.strftime('%Y-%m-%d'),
                    '前高價格': current_high,
                    '觸發價格': trigger_price,
                    '破底最低價': lowest_since_trigger,
                    '破底日期': lowest_date.strftime('%Y-%m-%d'),
                    '解套日期': date.strftime('%Y-%m-%d'),
                    '最大跌幅(%)': round(max_drawdown, 2),
                    '剩餘跌幅(%)': round(residual_drawdown, 2),
                    '破底花費天數': days_to_bottom,
                    '解套花費天數': days_to_recovery,
                    '狀態': '已解套'
                })
                
                # Reset for next event
                in_drawdown = False
                current_high = high
                current_high_date = date
                
    # Handle ongoing event
    if in_drawdown:
        max_drawdown = (current_high - lowest_since_trigger) / current_high * 100
        residual_drawdown = (trigger_price - lowest_since_trigger) / trigger_price * 100
        days_to_bottom = (lowest_date - trigger_date).days
        
        last_date = df.index[-1]
        days_ongoing = (last_date - trigger_date).days
        
        events.append({
            '觸發日期': trigger_date.strftime('%Y-%m-%d'),
            '前高日期': current_high_date.strftime('%Y-%m-%d'),
            '前高價格': current_high,
            '觸發價格': trigger_price,
            '破底最低價': lowest_since_trigger,
            '破底日期': lowest_date.strftime('%Y-%m-%d'),
            '解套日期': '進行中',
            '最大跌幅(%)': round(max_drawdown, 2),
            '剩餘跌幅(%)': round(residual_drawdown, 2),
            '破底花費天數': days_to_bottom,
            '解套花費天數': days_ongoing,
            '狀態': '進行中'
        })
        
    return pd.DataFrame(events)

def calculate_7pct_statistics(events_df):
    """
    Calculate summary statistics and probability distribution for the residual drawdowns.
    """
    if events_df.empty:
        return {}, pd.DataFrame()
        
    recovered_events = events_df[events_df['狀態'] == '已解套']
    
    # Summary Metrics
    avg_residual_dd = 0
    avg_days_to_bottom = 0
    avg_days_to_recovery = 0
    prob_dd_gt_10 = 0
    prob_dd_gt_20 = 0
    
    if len(recovered_events) > 0:
        avg_residual_dd = recovered_events['剩餘跌幅(%)'].mean()
        avg_days_to_bottom = recovered_events['破底花費天數'].mean()
        avg_days_to_recovery = recovered_events['解套花費天數'].mean()
        prob_dd_gt_10 = len(recovered_events[recovered_events['剩餘跌幅(%)'] > 10]) / len(recovered_events) * 100
        prob_dd_gt_20 = len(recovered_events[recovered_events['剩餘跌幅(%)'] > 20]) / len(recovered_events) * 100
        
    metrics = {
        'Total Events': len(events_df),
        'Recovered Events': len(recovered_events),
        'Avg Residual Drawdown (%)': round(avg_residual_dd, 2),
        'Avg Days to Bottom': round(avg_days_to_bottom, 1),
        'Avg Days to Recovery': round(avg_days_to_recovery, 1),
        'Prob Residual DD > 10%': round(prob_dd_gt_10, 2),
        'Prob Residual DD > 20%': round(prob_dd_gt_20, 2)
    }
    
    # Distribution of Residual Drawdowns
    perfs = events_df['剩餘跌幅(%)'].copy()
    
    # Bins for residual drawdown
    # Use finer granularity for smaller ranges
    bins = [0, 2, 4, 6, 8, 10, 15, 20, 30, 1000]
    labels = ['0%~2%', '2%~4%', '4%~6%', '6%~8%', '8%~10%', '10%~15%', '15%~20%', '20%~30%', '>30%']
    
    counts = pd.cut(perfs, bins=bins, labels=labels, right=False).value_counts().sort_index()
    
    dist_results = []
    n_total = len(events_df)
    
    for label, count in counts.items():
        if count == 0:
            continue
            
        prob = count / n_total * 100 if n_total > 0 else 0
        dist_results.append({
            'Range': label,
            'Count': count,
            'Probability (%)': round(prob, 2)
        })
        
    distribution_df = pd.DataFrame(dist_results)
    
    return metrics, distribution_df
