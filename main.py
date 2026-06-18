from data.report import get_cik, get_latest_10k_url, fetch_10k_text, parse_10k, extract_section
from data.financials import get_financials
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("AISTUDIO_KEY")

def run(ticker):
    print(f"\n📊 Researching {ticker}...\n")

    # financials
    fin = get_financials(ticker)
    print("=" * 50)
    print(f"🏢 {fin['name']} | {fin['sector']}")
    print("=" * 50)
    print(f"Market Cap:       ${fin['market_cap']:,.0f}")
    print(f"P/E Ratio:        {fin['pe_ratio']}")
    print(f"PEG Ratio:        {fin['peg_ratio']}")
    print(f"Revenue Growth:   {fin['revenue_growth'] * 100:.1f}%")
    print(f"Gross Margin:     {fin['gross_margins'] * 100:.1f}%")
    print(f"Free Cash Flow:   ${fin['fcf']:,.0f}")
    print(f"Debt/Equity:      {fin['debt_to_equity']}")
    print(f"Return on Equity: {fin['roic'] * 100:.1f}%")
    print(f"Dividend Yield:   {fin['dividend_yield'] * 100:.2f}%" if fin['dividend_yield'] else "Dividend Yield:   N/A")

    # 10-K
    print("\n⏳ Fetching 10-K...\n")
    cik = get_cik(ticker)
    url = get_latest_10k_url(cik)
    raw = fetch_10k_text(url)
    clean = parse_10k(raw)

    risk_factors = extract_section(clean, "Item 1A", "Item 1B")
    mda = extract_section(clean, "Item 7", "Item 8")
    financials = extract_section(clean, "Item 8", "Item 9")

    # LLM summary
    print("🤖 Analysing with AI...\n")
    client = genai.Client(api_key=api_key)
    prompt = f"""
    You are a financial analyst. Analyse these sections from a 10-K filing and give a concise research summary.

    RISK FACTORS:
    {risk_factors}

    MD&A:
    {mda}

    FINANCIAL STATEMENTS:
    {financials}

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

    print("=" * 50)
    print("📝 10-K AI SUMMARY")
    print("=" * 50)
    print(response.text)

run("AAPL")

