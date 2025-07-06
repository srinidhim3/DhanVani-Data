import requests

def get_symbol_from_name(company_name):
    url = f"https://www.nseindia.com/api/search/autocomplete?q={company_name}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com"
    }

    session = requests.Session()
    session.headers.update(headers)

    # Hit the homepage first to get cookies set
    session.get("https://www.nseindia.com", timeout=5)

    # Now hit the API
    response = session.get(url, timeout=5)
    if response.ok:
        results = response.json()
        for item in results.get("symbols", []):
            symbol_info = item.get("symbol_info", "").lower()
            symbol = item.get("symbol", "")
            if company_name.lower() in symbol_info:
                return symbol
    return None

# Example
print(get_symbol_from_name("CEAT Limited"))  # Should return 'CEATLTD'
