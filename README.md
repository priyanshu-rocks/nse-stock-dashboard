# NSE Stock Market Dashboard 📈

A real-time NSE stock market dashboard built with Python, Streamlit and Plotly.

## Stocks Tracked
- Samvardhana Motherson
- PNB (Punjab National Bank)
- Tata Steel
- Hindalco Industries
- HCL Technologies
- TCS (Tata Consultancy Services)
- Tata Motors
- Adani Enterprises

## Features
- Live NSE stock prices
- Candlestick and Line charts
- Moving Averages (MA20, MA50)
- Volume analysis
- Period returns (1W, 1M, 3M, 6M, 1Y)
- Recent price data table
- Auto-refresh every 5 minutes

## Setup

### 1. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the dashboard
```bash
streamlit run app.py
```

The dashboard will open automatically at http://localhost:8501

## Technologies Used
- Python
- Streamlit
- Plotly
- yfinance
- Pandas
