import pandas as pd
import numpy as np

def analyze_waves(df, reversal_percent=10.0):
    """
    Identify upward and downward waves in the price history.
    A trend reverses when the price moves against the trend by at least `reversal_percent`%.
    
    Args:
        df: DataFrame containing 'High', 'Low', 'Close' columns and DatetimeIndex.
        reversal_percent: The percentage required to confirm a reversal (e.g. 10.0 for 10%).
        
    Returns:
        List of dictionaries containing wave information.
    """
    waves = []
    
    if len(df) == 0:
        return waves
        
    state = 0 # 1 for uptrend, -1 for downtrend
    
    current_extreme_price = df['Close'].iloc[0]
    current_extreme_date = df.index[0]
    
    wave_start_date = df.index[0]
    wave_start_price = df['Close'].iloc[0]
    
    for date, row in df.iterrows():
        high = row['High']
        low = row['Low']
        close = row['Close']
        
        # Initial state determination
        if state == 0:
            if high >= current_extreme_price * (1 + reversal_percent / 100.0):
                state = 1
                current_extreme_price = high
                current_extreme_date = date
            elif low <= current_extreme_price * (1 - reversal_percent / 100.0):
                state = -1
                current_extreme_price = low
                current_extreme_date = date
            else:
                # Update extremes while no direction confirmed
                if high > current_extreme_price:
                    current_extreme_price = high
                    current_extreme_date = date
                elif low < current_extreme_price:
                    current_extreme_price = low
                    current_extreme_date = date
            continue
            
        if state == 1:
            # In uptrend, update peak
            if high > current_extreme_price:
                current_extreme_price = high
                current_extreme_date = date
                
            # Check for reversal to downtrend
            if low <= current_extreme_price * (1 - reversal_percent / 100.0):
                wave = {
                    'type': 'up',
                    'start_date': wave_start_date,
                    'end_date': current_extreme_date,
                    'highest_price': current_extreme_price,
                    'lowest_price': wave_start_price,
                    # For uptrend, start is bottom, end is peak
                    'start_price': wave_start_price, 
                    'end_price': current_extreme_price,
                    'ongoing': False
                }
                waves.append(wave)
                
                # Start downtrend
                state = -1
                wave_start_date = current_extreme_date
                wave_start_price = current_extreme_price
                current_extreme_price = low
                current_extreme_date = date
                
        elif state == -1:
            # In downtrend, update trough
            if low < current_extreme_price:
                current_extreme_price = low
                current_extreme_date = date
                
            # Check for reversal to uptrend
            if high >= current_extreme_price * (1 + reversal_percent / 100.0):
                wave = {
                    'type': 'down',
                    'start_date': wave_start_date,
                    'end_date': current_extreme_date,
                    'highest_price': wave_start_price,
                    'lowest_price': current_extreme_price,
                    # For downtrend, start is peak, end is bottom
                    'start_price': wave_start_price,
                    'end_price': current_extreme_price,
                    'ongoing': False
                }
                waves.append(wave)
                
                # Start uptrend
                state = 1
                wave_start_date = current_extreme_date
                wave_start_price = current_extreme_price
                current_extreme_price = high
                current_extreme_date = date

    # Add the final incomplete wave if needed
    if state != 0 and wave_start_date != current_extreme_date:
         wave = {
             'type': 'up' if state == 1 else 'down',
             'start_date': wave_start_date,
             'end_date': current_extreme_date,
             'highest_price': current_extreme_price if state == 1 else wave_start_price,
             'lowest_price': wave_start_price if state == 1 else current_extreme_price,
             'start_price': wave_start_price,
             'end_price': current_extreme_price,
             'ongoing': True
         }
         waves.append(wave)

    return waves
