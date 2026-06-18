A Python-based project that automates fundamental stock research by collecting data from SEC filings, extracting key information, and generating concise company summaries. 

The goal of this project is to reduce the time spent manually reading annual reports while still providing enough information for an investor or analyst to understand a company's financial position and business performance.

## Features

* **SEC EDGAR Integration**: Retrieve 10-K filings directly using a stock ticker.
* **Automated Parsing**: Extract critical sections (MD&A, Risk Factors) from annual reports.
* **Metrics Collection**: Gather core financial data for structural analysis.
* **AI-Powered Summaries**: Generate concise insights using LLMs.
* **Consolidated Reports**: Produce a unified research document for any selected stock.
* **Streamlit Web Interface**: Optional interactive dashboard for user queries.

## Tech Stack

* **Language**: Python
* **Data Processing**: Pandas, Requests
* **Data Sources**: SEC EDGAR API
* **AI Engine**: Anthropic API
* **Frontend**: Streamlit

## Project Structure

```text
project/
│
├── data/                 # Raw filings and extracted data
├── reports/              # Generated research reports
├── src/
│   ├── edgar.py          # SEC filing retrieval
│   ├── parser.py         # 10-K section extraction
│   ├── metrics.py        # Financial metrics collection
│   ├── summarizer.py     # LLM summaries
│   └── report.py         # Final report generation
│
├── app.py                # Streamlit interface
└── requirements.txt
```

## Development Roadmap

### Phase 1 — SEC Filing Retrieval
Build a module that retrieves 10-K filings from the SEC EDGAR database using a stock ticker.
* **Skills**: API requests, JSON parsing, Data retrieval.

### Phase 2 — Filing Parsing
Extract useful sections from the filing for deeper textual analysis.
* **Target Sections**: Business Overview, Risk Factors, Management Discussion and Analysis (MD&A).
* **Skills**: Text processing, File handling, Data cleaning.

### Phase 3 — Financial Metrics Collection
Collect key financial metrics and store them in a structured format for later analysis.
* **Target Metrics**: Revenue, Net Income, EPS, Free Cash Flow.
* **Skills**: Requests, Pandas, Financial data processing.

### Phase 4 — AI Summarisation
Use an LLM to generate concise summaries of filing sections and financial performance.
* **Skills**: Prompt engineering, API integration, Output evaluation.

### Phase 5 — Research Report Generation
Combine filing insights, financial metrics, and AI summaries into a single, clean report.
* **Skills**: Project architecture, Data pipelines, Report generation.

### Phase 6 — Streamlit Front End
Create a simple interface where users can enter a ticker and generate a report dynamically.
* **Skills**: Streamlit, User interfaces, Deployment basics.

## Why I Built This

I wanted a project that combined investing, financial analysis, and machine learning. Reading annual reports is crucial for understanding a company, but it can be incredibly time-consuming. This project aims to automate repetitive parts of the research process while keeping the underlying data transparent and accessible.

## Future Improvements

* Multi-year trend analysis.
* Earnings call transcript integration.
* Valuation metrics (DCF, P/E, EV/EBITDA).
* Portfolio screening features.
* Historical report comparisons.
