import streamlit as st
import yfinance as yf

INDUSTRY_PEERS = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA"],
    "Energy": ["XOM", "CVX", "NEE", "CEG", "VST"],
    "Financials": ["JPM", "BAC", "GS", "MS", "WFC"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK"],
    "Consumer Cyclical": ["AMZN", "TSLA", "HD", "MCD", "NKE"],
    "Industrials": ["CAT", "DE", "BA", "GE", "HON"],
    "Communication Services": ["GOOGL", "META", "NFLX", "DIS", "T"],
    "Utilities": ["NEE", "DUK", "SO", "D", "AEP"],
    "Real Estate": ["AMT", "PLD", "CCI", "EQIX", "PSA"],
    "Basic Materials": ["LIN", "APD", "ECL", "NEM", "FCX"],
    "Consumer Defensive": ["PG", "KO", "PEP", "WMT", "COST"],
}

@st.cache_data(ttl=3600)
def get_industry_benchmarks(sector):
    peers = INDUSTRY_PEERS.get(sector, [])
    if not peers:
        return None
    
    metrics = []
    for p in peers:
        try:
            info = yf.Ticker(p).info
            metrics.append({
                "pe_ratio": info.get("trailingPE"),
                "revenue_growth": info.get("revenueGrowth"),
                "gross_margins": info.get("grossMargins"),
                "debt_to_equity": info.get("debtToEquity"),
                "roic": info.get("returnOnEquity"),
            })
        except:
            continue
    
    # average across peers, skip Nones
    def avg(key):
        vals = [m[key] for m in metrics if m[key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None
    
    return {
        "pe_ratio": avg("pe_ratio"),
        "revenue_growth": avg("revenue_growth"),
        "gross_margins": avg("gross_margins"),
        "debt_to_equity": avg("debt_to_equity"),
        "roic": avg("roic"),
    }