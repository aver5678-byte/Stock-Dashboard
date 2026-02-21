import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def log_visit(page_name):
    if 'visit_logs' in st.session_state:
        user = st.session_state.get('user_email') or "訪客 (未登入)"
        import datetime
        st.session_state['visit_logs'].append({
            '時間': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            '使用者': user,
            '瀏覽模組': page_name
        })

@st.cache_data(ttl=3600)
def fetch_portfolio_data(tickers, start_date, end_date):
    if not tickers:
        return pd.DataFrame()
    df = yf.download(tickers, start=start_date, end=end_date)
    
    # Handle single ticker edge case
    if len(tickers) == 1:
        close_df = df[['Close']]
        close_df.columns = tickers
        return close_df
    else:
        # yfinance multi-index column handle
        # Level 0 is usually 'Price' ('Close', 'Open', etc) and Level 1 is Ticker
        # Sometimes Level 0 is 'Close' and Level 1 is Ticker
        try:
            if 'Close' in df.columns.levels[0]:
                return df['Close']
            else:
                return df.xs('Close', level=0, axis=1)
        except Exception as e:
            # Fallback
            close_cols = [c for c in df.columns if 'Close' in str(c) or c[0] == 'Close']
            df_filtered = df[close_cols]
            df_filtered.columns = [c[1] if isinstance(c, tuple) else c for c in df_filtered.columns]
            return df_filtered

def calculate_portfolio_metrics(cumulative_returns, start_balance):
    # cumulative_returns is a Series of portfolio growth factors (starting at 1.0)
    final_balance = cumulative_returns.iloc[-1] * start_balance
    
    # CAGR
    days = (cumulative_returns.index[-1] - cumulative_returns.index[0]).days
    years = days / 365.25
    if years > 0:
        cagr = ( (cumulative_returns.iloc[-1] / cumulative_returns.iloc[0]) ** (1 / years) ) - 1
    else:
        cagr = 0
        
    # Max Drawdown
    rolling_max = cumulative_returns.cummax()
    drawdown = (cumulative_returns - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    # Annual Returns (simple approximation using year-end values)
    yearly_vals = cumulative_returns.resample('Y').last()
    yearly_returns = yearly_vals.pct_change().dropna()
    best_year = yearly_returns.max() if not yearly_returns.empty else 0
    worst_year = yearly_returns.min() if not yearly_returns.empty else 0
    
    return {
        "最終資產餘額": round(final_balance, 2),
        "年化報酬率 (CAGR)": round(cagr * 100, 2),
        "最大回檔 (Max Drawdown)": round(max_drawdown * 100, 2),
        "最佳年度報酬": round(best_year * 100, 2),
        "最差年度報酬": round(worst_year * 100, 2)
    }

def page_portfolio_visualizer():
    log_visit("資產配置回測 (Portfolio)")
    st.title("💼 資產配置回測 (Portfolio Visualizer 繁中版)")
    st.write("模擬國外知名網站 **Portfolio Visualizer** 的核心功能！快速回測多重資產組合的歷史績效、年化報酬率 (CAGR) 與最大回檔 (Max Drawdown)。")
    
    with st.sidebar.expander("⚙️ 回測參數設定", expanded=True):
        start_year = st.number_input("起始年份 (Start Year)", min_value=1990, max_value=2030, value=2010)
        start_date = f"{start_year}-01-01"
        end_date = None # current date
        
        initial_amount = st.number_input("初始投入金額 ( Initial Amount $ )", min_value=100, value=10000, step=1000)
        rebalance = st.selectbox("再平衡頻率 (Rebalance)", ["不進行再平衡 (Buy and Hold)", "每年再平衡 (Annually)"])
        
    st.subheader("📊 投資組合分配 (Asset Allocation)")
    st.write("請輸入資產代碼 (如 `SPY`, `QQQ`, `TLT`, `2330.TW`) 與對應比例，總和必須為 100%。")
    
    cols = st.columns(5)
    tickers = []
    weights = []
    
    default_assets = [("SPY", 60), ("TLT", 40), ("", 0), ("", 0), ("", 0)]
    
    for i in range(5):
        with cols[i]:
            t = st.text_input(f"資產 {i+1}", value=default_assets[i][0], key=f"t_{i}")
            w = st.number_input(f"比例 (%)", min_value=0, max_value=100, value=default_assets[i][1], key=f"w_{i}")
            if t.strip() and w > 0:
                tickers.append(t.strip().upper())
                weights.append(w / 100.0)
                
    if sum(weights) != 1.0:
        st.error(f"⚠️ 權重總和必須剛好為 100%！目前為：{sum(weights)*100}%")
        st.stop()
        
    if st.button("🚀 開始回測 (Run Optimization)", type="primary"):
        with st.spinner("正在下載歷史數據並計算，請稍候..."):
            # Fetch Data
            benchmark_ticker = "^GSPC" # S&P 500
            all_tickers = list(set(tickers + [benchmark_ticker]))
            
            df = fetch_portfolio_data(all_tickers, start_date, end_date)
            
            if df.empty:
                st.error("找不到資料，請確認代碼正確。")
                st.stop()
                
            # Drop NaN rows where all are NaN, forward fill rest
            df = df.ffill().dropna(how='all')
            
            # Align start date to the earliest common date for all portfolio tickers
            port_df = df[tickers].dropna()
            if port_df.empty:
                 st.error("因某些代碼上市時間不足，無法找到共同交易時間段，請更換代碼或延後起始年份。")
                 st.stop()
                 
            # Extract Benchmark with same dates
            bench_df = df[[benchmark_ticker]].reindex(port_df.index).ffill()
            
            # Calculate daily returns
            daily_returns = port_df.pct_change().dropna()
            bench_returns = bench_df.pct_change().dropna().iloc[:, 0]
            
            # Portfolio Growth Calculation
            portfolio_growth = pd.Series(index=daily_returns.index, dtype=float)
            
            if "Annually" in rebalance:
                # Annual Rebalancing
                current_weights = np.array(weights)
                current_value = 1.0
                
                # We need to know when a year changes
                years = daily_returns.index.year
                
                vals = []
                for idx, dt in enumerate(daily_returns.index):
                    if idx > 0 and years[idx] != years[idx-1]:
                        # Rebalance at start of new year
                        current_weights = np.array(weights)
                        
                    # Apply daily return
                    ret = daily_returns.iloc[idx].values
                    # Growth of each individual piece
                    growth = 1 + ret
                    
                    # Update value
                    daily_port_return = np.sum(current_weights * ret)
                    current_value *= (1 + daily_port_return)
                    vals.append(current_value)
                    
                    # Drift the weights
                    current_weights = current_weights * growth
                    current_weights = current_weights / np.sum(current_weights)
                    
                portfolio_growth = pd.Series(vals, index=daily_returns.index)
            else:
                # Buy and Hold (No Rebalancing)
                # Just buy initial weights and let them drift
                cumulative_asset_returns = (1 + daily_returns).cumprod()
                portfolio_growth = (cumulative_asset_returns * weights).sum(axis=1)
                
            # Benchmark Growth Calculation
            bench_growth = (1 + bench_returns).cumprod()
            
            # Normalize to start at 1.0 for day 0
            portfolio_growth.loc[port_df.index[0]] = 1.0
            bench_growth.loc[port_df.index[0]] = 1.0
            portfolio_growth = portfolio_growth.sort_index()
            bench_growth = bench_growth.sort_index()
            
            # Metrics
            port_metrics = calculate_portfolio_metrics(portfolio_growth, initial_amount)
            bench_metrics = calculate_portfolio_metrics(bench_growth, initial_amount)
            
            st.markdown("---")
            st.subheader("📈 績效總覽 (Performance Summary)")
            
            # Display Metrics
            m_cols = st.columns(5)
            m_cols[0].metric("最新資產總值", f"${port_metrics['最終資產餘額']:,.0f}")
            m_cols[1].metric("年化報酬 (CAGR)", f"{port_metrics['年化報酬率 (CAGR)']}%")
            m_cols[2].metric("最大回檔 (Max DD)", f"{port_metrics['最大回檔 (Max Drawdown)']}%")
            m_cols[3].metric("最佳年度", f"{port_metrics['最佳年度報酬']}%")
            m_cols[4].metric("最差年度", f"{port_metrics['最差年度報酬']}%")
            
            # Plotly Chart
            fig = go.Figure()
            
            # Portfolio
            fig.add_trace(go.Scatter(
                x=portfolio_growth.index, 
                y=portfolio_growth * initial_amount,
                mode='lines', 
                name='您的投資組合 (Portfolio)',
                line=dict(color='white', width=2)
            ))
            
            # Benchmark
            fig.add_trace(go.Scatter(
                x=bench_growth.index, 
                y=bench_growth * initial_amount,
                mode='lines', 
                name='基準指數 (S&P 500)',
                line=dict(color='#888888', width=1.5, dash='dot')
            ))
            
            fig.update_layout(
                title="資產成長曲線 (Portfolio Growth)",
                yaxis_title="資產淨值 ($)",
                template="plotly_dark",
                height=500,
                hovermode="x unified",
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Drawdown Curve
            st.subheader("📉 洗盤回檔曲線 (Drawdowns)")
            port_dd = (portfolio_growth / portfolio_growth.cummax()) - 1
            bench_dd = (bench_growth / bench_growth.cummax()) - 1
            
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(x=port_dd.index, y=port_dd * 100, mode='lines', fill='tozeroy', name='組合回檔', line=dict(color='#ff0000')))
            fig_dd.update_layout(
                yaxis_title="回檔幅度 (%)",
                template="plotly_dark",
                height=300,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig_dd, use_container_width=True)
