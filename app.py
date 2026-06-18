import streamlit as st
from data.report import get_cik, get_latest_10k_url, fetch_10k_text, parse_10k, extract_section
from data.financials import get_financials
from google import genai
import yfinance as yf

st.set_page_config(page_title="Stock Research Assistant", layout="wide")
st.title("📊 Stock Research Assistant")
st.caption("Pulls live financials + SEC 10-K analysis for any US stock")

ticker = st.text_input("Enter a ticker", placeholder="e.g. AAPL, MSFT, NVDA").upper()
search = st.button("Research")

if search and ticker:

    # ── Financials ──────────────────────────────────────
    with st.spinner("Fetching financials..."):
        fin = get_financials(ticker)

    st.subheader(f"🏢 {fin['name']} — {fin['sector']}")
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

    st.divider()

    # ── Price Chart ─────────────────────────────────────
    with st.spinner("Loading price chart..."):
        hist = yf.Ticker(ticker).history(period="1y")

    st.subheader("📈 1 Year Price History")
    st.line_chart(hist["Close"])

    st.divider()

    # ── 10-K Summary ────────────────────────────────────
    st.subheader("📝 10-K AI Summary")

    with st.spinner("Fetching and analysing 10-K (this takes ~30s)..."):
        cik = get_cik(ticker)
        url = get_latest_10k_url(cik)
        raw = fetch_10k_text(url)
        clean = parse_10k(raw)

        risk_factors = extract_section(clean, "Item 1A", "Item 1B")
        mda = extract_section(clean, "Item 7", "Item 8")
        financials_text = extract_section(clean, "Item 8", "Item 9")

        client = genai.Client(api_key="your_key_here")
        prompt = f"""
        You are a financial analyst. Analyse these sections from a 10-K filing.

        RISK FACTORS:
        {risk_factors}

        MD&A:
        {mda}

        FINANCIAL STATEMENTS:
        {financials_text}

        Return a summary covering:
        1. Top 3 risks to be aware of
        2. Revenue and margin trends from MD&A
        3. Cash flow health
        4. Overall investment outlook (1-2 sentences)
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

    st.markdown(response.text)