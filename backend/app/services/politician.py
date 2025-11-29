import requests
import io
import re
from typing import List, Dict
from pypdf import PdfReader
from app.models.schemas import PoliticianTrade

# Hardcoded list of recent PDF URLs for "Whales" to ensure demo works reliably
# In a full production app, we would scrape the search results page periodically.
# These are real 2024 filings for Pelosi, Crenshaw, etc.
DEMO_PDF_URLS = [
    {
        "politician": "Nancy Pelosi",
        "party": "D",
        "url": "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2024/20024542.pdf", # PANW Calls
        "date": "2024-02-21"
    },
    {
        "politician": "Dan Crenshaw",
        "party": "R",
        "url": "https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/2023/20024186.pdf", # Example (older but valid format)
        "date": "2023-12-29"
    }
]

# Cache parsed trades to avoid re-downloading PDFs on every request
_TRADE_CACHE: Dict[str, List[PoliticianTrade]] = {}

def parse_pdf_trades(pdf_content: bytes, politician_info: Dict) -> List[PoliticianTrade]:
    """
    Parse the text content of a House Disclosure PDF to extract trades.
    This is a heuristic parser based on the standard form layout.
    """
    trades = []
    try:
        reader = PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text()
            
        # Debug: Print text to see what we're working with
        # print(text)
        
        # Regex to find lines that look like trades.
        # Structure often involves: [Ticker] ... [Date] ... [Amount]
        # This is tricky because the text extraction might not preserve table layout perfectly.
        # We'll look for known tickers or patterns.
        
        # Simple heuristic: Look for lines containing "$" and "Purchase" or "Sale"
        # and try to extract a ticker symbol in parentheses e.g. (AAPL)
        
        lines = text.split('\n')
        for line in lines:
            # Look for Ticker pattern: (SYMBOL)
            ticker_match = re.search(r'\(([A-Z]+)\)', line)
            if ticker_match:
                ticker = ticker_match.group(1)
                
                # Determine type
                type_ = "Purchase" if " P " in line or "Purchase" in line else "Sale"
                if " S " in line or "Sale" in line:
                    type_ = "Sale"
                    
                # Extract Amount (rough heuristic looking for $ ranges)
                amount_match = re.search(r'\$[\d,]+ - \$[\d,]+', line)
                amount = amount_match.group(0) if amount_match else "Unknown"
                
                trade = PoliticianTrade(
                    politician=politician_info['politician'],
                    party=politician_info['party'],
                    date=politician_info['date'], # Using filing date as proxy if transaction date parse fails
                    type=type_,
                    amount=amount,
                    ticker=ticker
                )
                trades.append(trade)
                
    except Exception as e:
        print(f"Error parsing PDF for {politician_info['politician']}: {e}")
        
    return trades

def get_politician_trades(symbol: str) -> List[PoliticianTrade]:
    """
    Get politician trades for a specific symbol.
    """
    global _TRADE_CACHE
    
    # If cache is empty, populate it
    if not _TRADE_CACHE:
        print("Hydrating politician trade cache...")
        all_trades = []
        for item in DEMO_PDF_URLS:
            try:
                print(f"Fetching PDF for {item['politician']}...")
                response = requests.get(item['url'], timeout=10)
                if response.status_code == 200:
                    trades = parse_pdf_trades(response.content, item)
                    all_trades.extend(trades)
            except Exception as e:
                print(f"Failed to fetch/parse PDF for {item['politician']}: {e}")
        
        # Group by ticker
        for trade in all_trades:
            if trade.ticker not in _TRADE_CACHE:
                _TRADE_CACHE[trade.ticker] = []
            _TRADE_CACHE[trade.ticker].append(trade)
            
    return _TRADE_CACHE.get(symbol, [])
