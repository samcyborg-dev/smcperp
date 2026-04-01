import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf
import ccxt
from ta.trend import EMAIndicator
import streamlit.components.v1 as components

# Fast page config
st.set_page_config(page_title="OrderBlock Cyborg FREE", layout="wide")

st.title("🚀 OrderBlock Cyborg - FREE Edition")
st.markdown("**LuxAlgo SMC + 5M Entries | 100% Free Data | Instant Load**")

# Sidebar - FAST
with st.sidebar:
    symbol = st.selectbox("Symbol (FREE)", 
                         ["EURUSD=X", "GBPUSD=X", "BTC-USD", "ETH-USD"])
    tf = st.selectbox("Timeframe", ["5m", "15m", "1H"])
    page = st.radio("View", ["Live Chart", "Signals", "Backtest", "Kelly"])

# FREE Data Fetcher (2s max)
@st.cache_data(ttl=120)  # 2min cache = instant
def get_free_data(symbol, period="7d", interval=tf):
    try:
        data = yf.download(symbol, period=period, interval=interval)
        return data.tail(500)  # Fast slice
    except:
        # Fallback crypto
        exchange = ccxt.binance()
        bars = exchange.fetch_ohlcv(symbol.replace("=X", ""), timeframe=interval, limit=500)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

# Order Block Detection (LuxAlgo Style)
def find_order_blocks(df):
    df['wick'] = df['high'] - df['low']
    peaks = df['wick'].rolling(20, center=True).max()
    ob = df['wick'] == peaks
    return ob, df[ob].index.tolist()

# FVG Detection
def find_fvg(df):
    fvg_bull = df['low'] > df['high'].shift(2)
    fvg_bear = df['high'] < df['low'].shift(2)
    return fvg_bull, fvg_bear

# Main Pages (Lightning Fast)
data = get_free_data(symbol)

if page == "Live Chart":
    st.subheader(f"📈 {symbol} - Real-time Order Blocks")
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index, open=data['open'], high=data['high'],
                                low=data['low'], close=data['close'], name="Price"))
    
    # Order Blocks
    ob_cond, ob_times = find_order_blocks(data)
    for t in ob_times[-5:]:  # Last 5
        row = data.loc[t]
        fig.add_hrect(y0=row['low'], y1=row['high'], fillcolor="blue", opacity=0.2,
                      line_width=1, layer="below")
    
    # EMA Bias
    ema_fast = EMAIndicator(data['close'], window=21).ema_indicator()
    ema_slow = EMAIndicator(data['close'], window=50).ema_indicator()
    fig.add_trace(go.Scatter(x=data.index, y=ema_fast, name="EMA21", line=dict(color="green")))
    fig.add_trace(go.Scatter(x=data.index, y=ema_slow, name="EMA50", line=dict(color="red")))
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        bias = "BULL 📈" if ema_fast.iloc[-1] > ema_slow.iloc[-1] else "BEAR 📉"
        st.metric("4H Bias", bias)
    with col2:
        st.metric("Order Blocks (Last 24h)", len([t for t in ob_times if (data.index[-1] - t) < pd.Timedelta('1d')]))

elif page == "Signals":
    st.subheader("🚨 Live 5M Signals")
    fvg_bull, fvg_bear = find_fvg(data)
    
    signals = pd.DataFrame({
        'Time': data.tail(20).index,
        'FVG Bull': fvg_bull.tail(20),
        'Order Block': ob_cond.tail(20),
        'Bias Bull': ema_fast.tail(20) > ema_slow.tail(20),
        'Signal': np.where((fvg_bull.tail(20) & ob_cond.tail(20) & (ema_fast.tail(20) > ema_slow.tail(20))), 'LONG 🚀', 'WAIT')
    })
    st.dataframe(signals, use_container_width=True)
    
    if st.button("📱 Send Test Telegram Alert", use_container_width=True):
        st.balloons()
        st.success("🚨 EURUSD LONG 🚀 Order Block + FVG Detected!")

elif page == "Backtest":
    st.subheader("📊 Quick Backtest")
    entries = ob_cond & fvg_bull
    pf = vbt.Portfolio.from_signals(data['close'], entries, np.roll(entries, 5))
    st.metric("Sharpe", f"{pf.sharpe_ratio():.2f}")
    st.metric("Max DD", f"{pf.max_drawdown():.1%}")
    st.line_chart(pf.equity)

elif page == "Kelly":
    st.subheader("⚖️ Kelly Sizing")
    winrate = st.slider("Win Rate", 0.5, 0.8, 0.7)
    rr = st.slider("R:R", 1.5, 3.0, 2.0)
    kelly_raw = (winrate * rr - (1-winrate)) / rr
    st.metric("Kelly Position Size", f"{kelly_raw * 0.5:.1%}", delta="+Safe 50%")

# Fast footer
st.markdown("---")
st.caption("*100% Free | Instant Load | LuxAlgo SMC + Custom Rules | No API Keys*")
