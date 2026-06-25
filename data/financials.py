import yfinance as yf
import streamlit as st
import numpy as np
import pandas as pd

@st.cache_data(ttl=3600)
def get_financials(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    return {
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "peg_ratio": info.get("pegRatio"),
        "revenue_growth": info.get("revenueGrowth"),
        "gross_margins": info.get("grossMargins"),
        "fcf": info.get("freeCashflow"),
        "debt_to_equity": info.get("debtToEquity"),
        "roic": info.get("returnOnEquity"),  # proxy for now
        "dividend_yield": info.get("dividendYield"),
    }

@st.cache_data(ttl=3600)
def get_price_metrics(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")["Close"]
    
    daily_returns = hist.pct_change().dropna()

    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
    volatility = daily_returns.std() * np.sqrt(252) * 100
    max_drawdown = ((hist / hist.cummax()) - 1).min() * 100
    ytd_return = ((hist.iloc[-1] / hist.iloc[0]) - 1) * 100
    
    return {
        "sharpe_ratio": round(sharpe, 2),
        "volatility": round(volatility, 2),
        "max_drawdown": round(max_drawdown, 2),
        "ytd_return": round(ytd_return, 2),
    }

@st.cache_data(ttl=3600)
def display_revenue(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials

    if "Total Revenue" not in financials.index:
        return None

    revenue = stock.financials.loc["Total Revenue"]

    df = revenue.copy()
    df.index = pd.to_datetime(df.index)

    df = df.sort_index()

    df = pd.DataFrame({
        "Date": pd.to_datetime(revenue.index),
        "Revenue (B)": revenue.values / 1e9
    })
    return df
    
    
    
if __name__ == "__main__":
    print(get_financials("AAPL"))

