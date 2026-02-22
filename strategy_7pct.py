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
def analyze_7pct_strategy(df, trigger_pct=7.0):
    if len(df) == 0:
        return pd.DataFrame()

    # 指揮官指定的台股戰役清單 (Hardcoded Manual List)
    # 格式: (起跌日/波段前高, 最低落底日)
    MANUAL_EVENTS = [
        # 千禧年網路泡沫
        ('2000-02-18', '2000-03-16'),
        ('2000-04-06', '2000-10-19'),
        ('2000-11-08', '2000-12-28'),
        ('2001-02-16', '2001-07-24'),
        ('2001-08-17', '2001-09-26'),
        ('2001-12-13', '2001-12-21'),
        # 非典 SARS 與後續盤整
        ('2002-04-22', '2002-10-11'),
        ('2003-01-24', '2003-04-28'),
        ('2004-03-05', '2004-08-05'),
        ('2006-05-09', '2006-07-17'),
        # 金融海嘯
        ('2007-07-26', '2007-08-17'),
        ('2007-10-30', '2008-01-23'),
        ('2008-05-20', '2008-10-28'),
        ('2008-11-05', '2008-11-21'),
        # 歐債、中型回檔與中美貿易戰
        ('2010-01-19', '2010-05-25'),
        ('2011-02-08', '2011-12-19'),
        ('2012-03-02', '2012-06-04'),
        ('2014-07-15', '2014-10-16'),
        ('2015-04-28', '2015-08-24'),
        ('2015-11-05', '2016-01-18'),
        ('2018-01-23', '2019-01-04'),
        # 新冠肺炎 COVID-19
        ('2020-01-03', '2020-03-19'),
        ('2021-04-29', '2021-05-17'),
        ('2021-07-15', '2021-10-05'),
        # 近期長官確定的實戰波段
        ('2022-12-01', '2022-12-29'),
        ('2023-07-31', '2023-10-31'),
        ('2024-04-10', '2024-04-19'),
        ('2024-07-11', '2024-08-05'),
        ('2025-01-07', '2025-04-09'), # (註: 指揮官1/11實際上是指1/07的起跌高點23943，所以用01-07對齊)
    ]

    events = []
    df_index = df.index.normalize()
    
    for (p_date, b_date) in MANUAL_EVENTS:
        p_date = pd.to_datetime(p_date)
        b_date = pd.to_datetime(b_date)
        
        # 配對最近的交易日
        if p_date not in df_index:
            nearest = df_index[df_index <= p_date]
            if not nearest.empty: p_date = nearest[-1]
            else: continue
            
        if b_date not in df_index:
            nearest = df_index[df_index <= b_date]
            if not nearest.empty: b_date = nearest[-1]
            else: continue
            
        peak_price = df.loc[p_date]['High']
        if isinstance(peak_price, pd.Series): peak_price = peak_price.max()
        bottom_price = df.loc[b_date]['Low']
        if isinstance(bottom_price, pd.Series): bottom_price = bottom_price.min()
        
        # 嚴格依照手工指定的高低點算出破壞力
        max_drawdown = (peak_price - bottom_price) / peak_price * 100
        
        # 抓出觸發 -7% 的那一天
        segment_pb = df.loc[p_date:b_date]
        trigger_sub = segment_pb[segment_pb['Close'] <= peak_price * (1 - trigger_pct/100.0)]
        trigger_date = trigger_sub.index[0] if not trigger_sub.empty else b_date
        trigger_price = df.loc[trigger_date]['Close']
        if isinstance(trigger_price, pd.Series): trigger_price = trigger_price.min()
        
        residual_drawdown = (trigger_price - bottom_price) / trigger_price * 100
        
        # 尋找解套或反彈結案 (從見底之後開始找)
        future_df = df.loc[b_date:]
        
        # 1. 完全收復: 未來某日的高點大於等於起跌前高
        rec_sub = future_df[future_df['High'] >= peak_price]
        
        if not rec_sub.empty:
            rec_date = rec_sub.index[0]
            status = '已解套'
            recovery_status = '完全收復前高'
            rec_price = df.loc[rec_date]['High']
            if isinstance(rec_price, pd.Series): rec_price = rec_price.max()
            days_to_rec = (rec_date - p_date).days
        else:
            # 2. 如果沒有完全收復，那有沒有反彈超過 15% 結案？
            bounce_sub = future_df[future_df['Close'] >= bottom_price * 1.15]
            if not bounce_sub.empty:
                rec_date = bounce_sub.index[0]
                status = '已解套'
                recovery_status = '空頭終結(反彈15%)'
                rec_price = df.loc[rec_date]['Close']
                if isinstance(rec_price, pd.Series): rec_price = rec_price.max()
                days_to_rec = (rec_date - p_date).days
            else:
                # 3. 都在套牢中
                rec_date = future_df.index[-1]
                status = '進行中'
                recovery_status = '套牢中'
                rec_price = df.loc[rec_date]['Close']
                if isinstance(rec_price, pd.Series): rec_price = rec_price.max()
                days_to_rec = (rec_date - p_date).days
                
        # 根據長官定義: 日期皆由起跌前高起算
        days_to_bottom = (b_date - p_date).days
        
        events.append({
            '觸發日期': trigger_date.strftime('%Y-%m-%d'),
            '前高日期': p_date.strftime('%Y-%m-%d'),
            '前高價格': peak_price,
            '觸發價格': trigger_price,
            '破底最低價': bottom_price,
            '破底日期': b_date.strftime('%Y-%m-%d'),
            '解套日期': rec_date.strftime('%Y-%m-%d') if status == '已解套' else '進行中',
            '解套點位': rec_price,
            '最大跌幅(%)': round(max_drawdown, 2),
            '剩餘跌幅(%)': round(residual_drawdown, 2),
            '破底花費天數': days_to_bottom,
            '解套花費天數': days_to_rec,
            '狀態': status,
            '解套形式': recovery_status
        })

    # 將事件按日期排序回傳
    result_df = pd.DataFrame(events)
    if not result_df.empty:
        result_df = result_df.sort_values(by='前高日期', ascending=True).reset_index(drop=True)
    return result_df

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
