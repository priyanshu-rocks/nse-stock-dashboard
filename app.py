import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NSE Stock Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #0A0E1A; }
    .stApp { background-color: #0A0E1A; }

    .metric-card {
        background: linear-gradient(135deg, #111827, #1a2236);
        border: 1px solid #1e2d45;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-label {
        font-size: 12px;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #F9FAFB;
    }
    .metric-change-up { color: #10B981; font-size: 14px; font-weight: 500; }
    .metric-change-down { color: #EF4444; font-size: 14px; font-weight: 500; }

    .stock-header {
        background: linear-gradient(135deg, #111827, #1a2236);
        border: 1px solid #1e2d45;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
    }
    .stock-name { font-size: 28px; font-weight: 700; color: #F9FAFB; margin: 0; }
    .stock-symbol { font-size: 14px; color: #6B7280; margin: 4px 0 0; }
    .stock-price { font-size: 42px; font-weight: 700; color: #F9FAFB; margin: 12px 0 0; }

    .sidebar-title {
        font-size: 20px;
        font-weight: 700;
        color: #F9FAFB;
        margin-bottom: 4px;
    }
    .sidebar-sub {
        font-size: 12px;
        color: #6B7280;
        margin-bottom: 20px;
    }

    div[data-testid="stSelectbox"] label { color: #9CA3AF; font-size: 13px; }
    div[data-testid="stRadio"] label { color: #9CA3AF; font-size: 13px; }

    .footer {
        text-align: center;
        color: #374151;
        font-size: 12px;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #1e2d45;
    }
</style>
""", unsafe_allow_html=True)

# ── Stock list ────────────────────────────────────────────────────────────────
STOCKS = {
    "Samvardhana Motherson": "MOTHERSON.NS",
    "PNB (Punjab National Bank)": "PNB.NS",
    "Tata Steel": "TATASTEEL.NS",
    "Hindalco Industries": "HINDALCO.NS",
    "HCL Technologies": "HCLTECH.NS",
    "TCS (Tata Consultancy)": "TCS.NS",
    "Vedanta": "VEDL.NS",
    "Adani Enterprises": "ADANIENT.NS",
}

PERIODS = {
    "1 Week": "7d",
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-title">📈 NSE Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-sub">Live NSE Stock Tracker</p>', unsafe_allow_html=True)

    selected_name = st.selectbox("Select Stock", list(STOCKS.keys()))
    selected_period_label = st.radio("Time Period", list(PERIODS.keys()), index=2)
    st.markdown("---")
    chart_type = st.radio("Chart Type", ["Candlestick", "Line Chart"], index=0)
    show_volume = st.checkbox("Show Volume", value=True)
    show_ma = st.checkbox("Show Moving Averages", value=True)
    st.markdown("---")
    refresh = st.button("🔄 Refresh Data", use_container_width=True)
    st.markdown('<p style="color:#374151;font-size:11px;margin-top:12px;">Data from Yahoo Finance · NSE</p>', unsafe_allow_html=True)

# ── Fetch data ────────────────────────────────────────────────────────────────
ticker_symbol = STOCKS[selected_name]
period = PERIODS[selected_period_label]

def fetch_data(symbol, period):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period)
    info = ticker.fast_info
    return hist, info

with st.spinner(f"Fetching {selected_name} data..."):
    try:
        hist, info = fetch_data(ticker_symbol, period)
        if refresh:
            st.cache_data.clear()
            hist, info = fetch_data(ticker_symbol, period)
    except Exception as e:
        st.error(f"Could not fetch data: {e}")
        st.stop()

if hist.empty:
    st.error("No data found. Please try again.")
    st.stop()

# ── Compute metrics ───────────────────────────────────────────────────────────
current_price = hist["Close"].iloc[-1]
prev_price = hist["Close"].iloc[-2] if len(hist) > 1 else current_price
change = current_price - prev_price
change_pct = (change / prev_price) * 100
high_52w = hist["High"].max()
low_52w = hist["Low"].min()
avg_volume = hist["Volume"].mean()
period_return = ((current_price - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100

arrow = "▲" if change >= 0 else "▼"
color_class = "metric-change-up" if change >= 0 else "metric-change-down"
line_color = "#10B981" if change >= 0 else "#EF4444"

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stock-header">
    <p class="stock-name">{selected_name}</p>
    <p class="stock-symbol">{ticker_symbol} · NSE · {datetime.now().strftime("%d %b %Y, %I:%M %p")}</p>
    <p class="stock-price">₹{current_price:,.2f}
        <span class="{color_class}" style="font-size:20px; margin-left:12px;">
            {arrow} ₹{abs(change):.2f} ({change_pct:+.2f}%)
        </span>
    </p>
</div>
""", unsafe_allow_html=True)

# ── Metrics row ───────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    (c1, "Period High", f"₹{high_52w:,.2f}", None),
    (c2, "Period Low", f"₹{low_52w:,.2f}", None),
    (c3, "Avg Volume", f"{avg_volume/1e6:.2f}M", None),
    (c4, "Period Return", f"{period_return:+.2f}%", period_return),
    (c5, "Prev Close", f"₹{prev_price:,.2f}", None),
]
for col, label, value, val_num in metrics:
    with col:
        if val_num is not None:
            chg_cls = "metric-change-up" if val_num >= 0 else "metric-change-down"
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="{chg_cls}" style="font-size:22px;font-weight:700;">{value}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Main chart ────────────────────────────────────────────────────────────────
rows = 2 if show_volume else 1
row_heights = [0.7, 0.3] if show_volume else [1.0]

fig = make_subplots(
    rows=rows, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.04,
    row_heights=row_heights
)

if chart_type == "Candlestick":
    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist["Open"],
        high=hist["High"],
        low=hist["Low"],
        close=hist["Close"],
        name="OHLC",
        increasing_line_color="#10B981",
        decreasing_line_color="#EF4444",
        increasing_fillcolor="#10B981",
        decreasing_fillcolor="#EF4444",
    ), row=1, col=1)
else:
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"],
        mode="lines",
        name="Close",
        line=dict(color=line_color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba({'16,185,129' if change >= 0 else '239,68,68'},0.08)",
    ), row=1, col=1)

if show_ma and len(hist) >= 20:
    ma20 = hist["Close"].rolling(20).mean()
    fig.add_trace(go.Scatter(
        x=hist.index, y=ma20,
        mode="lines", name="MA 20",
        line=dict(color="#F59E0B", width=1.5, dash="dot")
    ), row=1, col=1)

if show_ma and len(hist) >= 50:
    ma50 = hist["Close"].rolling(50).mean()
    fig.add_trace(go.Scatter(
        x=hist.index, y=ma50,
        mode="lines", name="MA 50",
        line=dict(color="#8B5CF6", width=1.5, dash="dot")
    ), row=1, col=1)

if show_volume:
    vol_colors = ["#10B981" if c >= o else "#EF4444"
                  for c, o in zip(hist["Close"], hist["Open"])]
    fig.add_trace(go.Bar(
        x=hist.index,
        y=hist["Volume"],
        name="Volume",
        marker_color=vol_colors,
        opacity=0.7,
    ), row=2, col=1)

fig.update_layout(
    paper_bgcolor="#0A0E1A",
    plot_bgcolor="#0A0E1A",
    font=dict(family="Inter", color="#9CA3AF"),
    legend=dict(
        bgcolor="rgba(17,24,39,0.8)",
        bordercolor="#1e2d45",
        borderwidth=1,
        font=dict(size=12)
    ),
    xaxis_rangeslider_visible=False,
    margin=dict(l=0, r=0, t=10, b=0),
    height=520 if show_volume else 420,
    hovermode="x unified",
)
fig.update_xaxes(
    gridcolor="#1e2d45", showgrid=True,
    zeroline=False, showspikes=True,
    spikecolor="#374151", spikethickness=1
)
fig.update_yaxes(
    gridcolor="#1e2d45", showgrid=True,
    zeroline=False, tickprefix="₹"
)
if show_volume:
    fig.update_yaxes(tickprefix="", row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

# ── Price table ───────────────────────────────────────────────────────────────
st.markdown("### 📋 Recent Price Data")
display_df = hist[["Open", "High", "Low", "Close", "Volume"]].tail(10).copy()
display_df = display_df.sort_index(ascending=False)
display_df.index = display_df.index.strftime("%d %b %Y")
display_df.columns = ["Open (₹)", "High (₹)", "Low (₹)", "Close (₹)", "Volume"]
for col in ["Open (₹)", "High (₹)", "Low (₹)", "Close (₹)"]:
    display_df[col] = display_df[col].map(lambda x: f"₹{x:,.2f}")
display_df["Volume"] = display_df["Volume"].map(lambda x: f"{x/1e6:.2f}M")

st.dataframe(display_df, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div class="footer">Built with Python · Streamlit · Plotly · yfinance &nbsp;|&nbsp; Data from Yahoo Finance &nbsp;|&nbsp; NSE India</div>', unsafe_allow_html=True)
