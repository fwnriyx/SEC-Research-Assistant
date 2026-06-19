import requests
from bs4 import BeautifulSoup
from google import genai

import os
from dotenv import load_dotenv

script_dir = os.path.dirname(__file__)
dotenv_path = os.path.join(script_dir, '..', '.env')

load_dotenv(dotenv_path)

api_key = os.getenv("AISTUDIO_KEY")


'''
In this file Im fetching the central index key from public SEC records and loaded it into Google's GenAI to make analysis.

From SEC, I fetched Risk factors, financials and also Management's Discussion and Analysis. The prompt can be updated, but I fixed it by default for now.
The entire AI part is subject to changes, but I tried to make the AI conclusion as subjective as possible.

'''

# def get_cik(ticker):
#     # cik = central index key. its basically fancy phrase for ticker.
#     url = "https://www.sec.gov/files/company_tickers.json"
#     headers = {"User-Agent": "forschoolwork.exe@gmail.com"} # SEC requires this
#     res = requests.get(url, headers=headers).json()
#     # print(res.text[:2000])
#     for entry in res.values():
#         if entry["ticker"].upper() == ticker.upper():
#             return str(entry["cik_str"]).zfill(10) # pads to 10 digits
    
#     return None

def get_cik(ticker):
    if not ticker:
        return None

    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "forschoolwork.exe@gmail.com"}

    res = requests.get(url, headers=headers).json()

    ticker = ticker.strip().upper()

    for entry in res.values():
        if entry["ticker"].strip().upper() == ticker:
            return str(entry["cik_str"]).zfill(10)

    return None

def get_latest_10k_url(cik):
    # This is for if ure looking for ONLY 10-ks. But foreign companies and companies that recently IPO'd dont have 10-ks
    if cik is None:
        raise ValueError("CIK is None — ticker lookup failed")
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {"User-Agent": "forschoolwork.exe@gmail.com"}
    data = requests.get(url, headers=headers).json()
    
    filings = data["filings"]["recent"]
    
    for i, form in enumerate(filings["form"]):
        if form == "10-K":
            accession = filings["accessionNumber"][i].replace("-", "")
            doc_name = filings["primaryDocument"][i]
            return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{doc_name}"
    
    return None


def get_latest_filing_url(cik):
    #Companies that IPO more recently and foreign companies usually dont have 10-ks. This finds other form types
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {"User-Agent": "forschoolwork.exe@gmail.com"}
    data = requests.get(url, headers=headers).json()
    
    filings = data["filings"]["recent"]
    
    # priority order of form types to try
    priority = ["10-K", "20-F", "10-Q", "S-1"]
    
    found = {}
    for i, form in enumerate(filings["form"]):
        if form in priority and form not in found:
            accession = filings["accessionNumber"][i].replace("-", "")
            doc_name = filings["primaryDocument"][i]
            found[form] = (
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{doc_name}",
                form
            )
        if len(found) == len(priority):
            break
    
    # return highest priority available
    for form_type in priority:
        if form_type in found:
            return found[form_type]  # returns (url, form_type)
    
    return None, None

def fetch_10k_text(url):
    headers = {"User-Agent": "forschoolwork.exe@gmail.com"}
    res = requests.get(url, headers=headers)
    return res.text

def parse_10k(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # remove script, style, and hidden elements cause like why would we use them lol
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    # remove hidden divs (where XBRL metadata comes from. keeps crowding my outputs so ill cya) btw ai helped me w this
    for tag in soup.find_all(style=lambda s: s and "display:none" in s.replace(" ", "")):
        tag.decompose()
    
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def extract_section(text, start_marker, end_marker):
    
    '''
    basically this extracts texts between 2 points. u set the first and last words and it gets all the texts in between
    but because every item is mentioned in the table of contents, u gotta skip the first time its mentioned.
    also later on, its important to start and end every item with the period cause sometimes its mentioned in other items, but its the wrong section
    u feel me? ok
    '''
    
    first = text.find(start_marker)
    second = text.find(start_marker, first + 1)
    end = text.find(end_marker, second)
    
    if second == -1:
        return "Section not found"
    
    return text[second:end].strip()

def summarise_10k(risk_factors, mda, financials, api_key):
    '''
    WARNING NEED TO SWITCH MODELS BY OCT BUT THIS IS THE CHEAPEST ALT SO FAR
    '''
    
    client = genai.Client(api_key = api_key)
    
    prompt = f"""
    You are a financial analyst. Analyse these sections from a 10-K filing and give a concise research summary.

    RISK FACTORS:
    {risk_factors[:30000]}

    MD&A:
    {mda}

    FINANCIAL STATEMENTS:
    {financials[:30000]}

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
    
    return response.text

cik = get_cik("AAPL")
print(get_latest_10k_url(cik))

url = get_latest_10k_url(cik)
raw = fetch_10k_text(url)
clean = parse_10k(raw)
# print(raw[:2000])
# print(clean[:3000])

# extract all the sections needed using first and last words 
risk_factors = extract_section(clean, "Item 1A.", "Item 1B.")
mda = extract_section(clean, "Item 7.", "Item 7A.")
financials = extract_section(clean, "Item 8.", "Item 9.")

print("Risk Factors:", len(risk_factors), "chars")
print("MD&A:", len(mda), "chars")
print("Financials:", len(financials), "chars")
# print(risk_factors[:3000])

# print(risk_factors[-3000:])

if __name__ == "__main__":
    print(summarise_10k(risk_factors, mda, financials, api_key=api_key))

