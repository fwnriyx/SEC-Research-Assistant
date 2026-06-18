import yfinance as yf

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

if __name__ == "__main__":
    print(get_financials("AAPL"))
