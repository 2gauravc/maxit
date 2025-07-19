import requests 
from agents.core_utils import set_sec_client, ensure_list
from edgar import *

## Get ticker given company name 
def get_ticker_given_name(company_name: str):
    """
    Searches for equity ticker symbols that match a given company name using Yahoo Finance's search API.
    Args:
        company_name (str): The name of the company to search for (e.g., "Apple").
    Returns:
        List[dict]: A list of dictionaries, each with:
            - 'name': The company's short name (str)
            - 'symbol': The stock ticker symbol (str)
    """
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    params = {"q": company_name}

    try:
        res = requests.get(url, params=params, headers=headers)
        res.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)

        if "application/json" in res.headers.get("Content-Type", ""):
            data = res.json()
            #print(data)
            results = [
                {
                    "name": q["shortname"],
                    "symbol": q["symbol"],
                    "exchange": q["exchange"]
                }
                for q in data.get("quotes", []) 
                if q.get("quoteType") == "EQUITY"
            ]
            return {
            "success": True,
            "result": results,
            "error": None
            }

        else:
            raise ValueError(f"Unexpected content type: {res.headers.get('Content-Type')}")

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"HTTP error: {e}", "result": None}
    except ValueError as e:
        return {"success": False, "error": f"Invalid response: {e}", "result": None}


# Get the CIK 
def get_cik (name: str) -> str:
    """
    Fetches the CIK (Central Index Key) given the entity name.

    Args:
        name (str): The name of the entity (e.g., "Micron Technology").
    
    Returns:
        str: The CIK number of the entity (e.g. 'CIK0001730168').
    """
    set_sec_client()
    
    ticker = get_ticker_given_name(name)[0]['symbol']
    c = Company(ticker)    
    cik_raw = c.cik
    print(f"cik_raw={cik_raw} ({type(cik_raw)})")
    cik_formatted = f"CIK{int(cik_raw):010d}"
    return cik_formatted

def get_latest_filings(ticker: str, form_type: Optional[str] = None, n: int = 5, as_text: bool = True) -> str:
    """
    Fetches the latest filings for a given ticker using SEC-API.
    If form_type is specified, filters by that form (e.g., '10-K', '8-K').

    Args:
        ticker (str): The stock ticker (e.g., "AAPL").
        form_type (Optional[str]): The form type to filter (e.g., "10-K", "10-Q", "8-K"). If None, returns all types.
        n (int): Number of filings to retrieve. Defaults to 5.
        as_text (bool): for string output, use True. Defaults to False which gives a Filing object 
    
    Returns:
        str: A newline-separated string of the latest filings.
    """
    set_sec_client()

    c = Company(ticker)
    
    if form_type:
        filings = c.get_filings(form=form_type).latest(n)
    else:
        filings = c.get_filings().latest(n)
    
    filings = ensure_list(filings)
    if as_text:
        return "\n".join(str(f) for f in filings)
    else: 
        return filings
