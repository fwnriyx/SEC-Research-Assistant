import streamlit as st
from data.report import get_cik, fetch_10k_text, parse_10k, extract_section, get_latest_filing_url, build_prompt
from data.financials import get_financials, get_price_metrics,  display_revenue
from google import genai
import yfinance as yf
import os
from dotenv import load_dotenv
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

load_dotenv()

# api_key = os.getenv("AISTUDIO_KEY")
# api_key = st.secrets["api_key"]
# st.write("Google key exists:", bool(st.secrets.get("api_key", None)))
try:
    api_key = st.secrets["api_key"]
except Exception:
    api_key = os.getenv("AISTUDIO_KEY")


st.set_page_config(page_title="Stock Research Assistant", layout="wide")
st.title("Stock Research Assistant")
st.caption("Pulls live financials + SEC 10-K analysis for (mainly) any US stock")

ticker = st.text_input("Enter a ticker", placeholder="e.g. AAPL, MSFT, NVDA").upper()
search = st.button("Research")

if search and ticker:

    # ── Financials ──────────────────────────────────────
    with st.spinner("Fetching financials..."):
        fin = get_financials(ticker)

    st.subheader(f"{fin['name']} — {fin['sector']}")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Market Cap", f"${fin['market_cap']:,.0f}")
    col2.metric("P/E Ratio", fin['pe_ratio'])
    col3.metric("PEG Ratio", fin['peg_ratio'])
    col4.metric("Revenue Growth", f"{fin['revenue_growth'] * 100:.1f}%")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Gross Margin", f"{fin['gross_margins'] * 100:.1f}%")
    col6.metric("Free Cash Flow", f"${fin['fcf']:,.0f}")
    col7.metric("Debt / Equity", fin['debt_to_equity'])
    col8.metric("Return on Equity", f"{fin['roic'] * 100:.1f}%")
    pm = get_price_metrics(ticker)

    st.subheader("Risk Metrics (1 Year)")
    col9, col10, col11, col12 = st.columns(4)
    col9.metric("Sharpe Ratio", pm["sharpe_ratio"])
    col10.metric("Volatility", f"{pm['volatility']}%")
    col11.metric("Max Drawdown", f"{pm['max_drawdown']}%")
    col12.metric("1Y Return", f"{pm['ytd_return']}%")

    st.divider()

    # ── Price Chart ─────────────────────────────────────
    with st.spinner("Loading price chart..."):
        hist = yf.Ticker(ticker).history(period="1y")

    st.subheader("1 Year Price History")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Close"))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig, width = 'stretch', key = "Yearly Price Change")
        # I was on python 3.9 so I used .line_chart but I swapped to 3.12 for streamlit
        # dont ask me why i was using 3.9 im retro like that
    #st.line_chart(hist["Close"])
    

    st.divider()
    
    st.subheader(f'{fin['name']} - Revenue')
    rev = display_revenue(ticker)
    if rev is None or rev.empty:
        st.warning("No revenue data available for this ticker")
    else:
        fig = px.line(
            rev,
            x="Date",
            y="Revenue (B)",
            markers=True,
            title="Revenue Trend"
    )

        st.plotly_chart(fig, width = 'stretch', key = "revenue_chart")
    st.divider()
    # 10-K Summary
    st.subheader("📝 10-K AI Summary")

    with st.spinner("Fetching and analysing 10-K (this takes ~ 1 min)..."):
        cik = get_cik(ticker)

        if not cik:
            st.error("Ticker not found in SEC database")
            st.stop()

        # USE THIS BLOCK OF CODE IF URE ONLY LOOKING FOR 10Ks
        # url = get_latest_10k_url(cik)

        # if not url:
        #     st.error("No 10-K filing found for this company")
        #     st.stop()

        
        url, form_type = get_latest_filing_url(cik)

        if not url:
            st.error("No SEC filing found for this ticker.")
            st.stop()

        st.caption(f"📄 Analysing: {form_type} filing")
        raw = fetch_10k_text(url)
        clean = parse_10k(raw)

        risk_factors = extract_section(clean, "Item 1A", "Item 1B")
        mda = extract_section(clean, "Item 7", "Item 8")
        financials_text = extract_section(clean, "Item 8", "Item 9")

        client = genai.Client(api_key = api_key)
        prompt = build_prompt(risk_factors, mda, financials_text, form_type, fin, pm)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

    # st.markdown(response.text)
    summary = response.text.replace("$", "\\$")
    st.markdown(summary)
