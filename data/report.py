import requests
from bs4 import BeautifulSoup

'''
In this file Im fetching the central index key from public SEC records to see  

'''

def get_cik(ticker):
    # cik = central index key. its basically fancy phrase for ticker.
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "forschoolwork.exe@gmail.com"} # SEC requires this
    res = requests.get(url, headers=headers).json()
    # print(res.text[:2000])
    for entry in res.values():
        if entry["ticker"].upper() == ticker.upper():
            return str(entry["cik_str"]).zfill(10) # pads to 10 digits
    
    return None

def get_latest_10k_url(cik):
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

def fetch_10k_text(url):
    headers = {"User-Agent": "yourname@email.com"}
    res = requests.get(url, headers=headers)
    return res.text

def parse_10k(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # remove script, style, and hidden elements
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    # remove hidden divs (where the XBRL metadata lives)
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



cik = get_cik("AAPL")
print(get_latest_10k_url(cik))

url = get_latest_10k_url(cik)
raw = fetch_10k_text(url)
clean = parse_10k(raw)
# print(raw[:2000])
# print(clean[:3000])

# extract all the sections needed using first and last words 
risk_factors = extract_section(clean, "Item 1A.", "Item 1B.")
mda = extract_section(clean, "Item 7", "Item 8")
financials = extract_section(clean, "Item 8", "Item 9")

print("Risk Factors:", len(risk_factors), "chars")
print("MD&A:", len(mda), "chars")
print("Financials:", len(financials), "chars")
# print(risk_factors[:3000])

print(risk_factors[-3000:])