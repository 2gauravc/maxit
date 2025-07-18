from agents.data_wrappers import gather_peer_data
from agents.core_utils import format_peer_comparison_prompt
from langchain_openai import ChatOpenAI
from edgar import *

def run_peer_comparison(tickers: List[str]) -> str:
    """
    Executes a flexible peer comparison across multiple companies using LLM reasoning.

    This function performs the following steps:
    1. Retrieves financial and market data for each ticker using underlying tools.
    2. Structures the data into a unified prompt format.
    3. Passes the prompt to an LLM to generate a qualitative comparison based on:
       - Revenue
       - Cost Structure
       - Profitability
       - Leverage
       - Stock Price and Valuation

    Parameters:
        tickers (List[str]): A list of company ticker symbols to compare.

    Returns:
        str: A natural language comparison generated by the LLM.
    """

    data = gather_peer_data(tickers)
    prompt = format_peer_comparison_prompt(data)
    llm = ChatOpenAI(model="gpt-4o")
    response = llm.invoke(prompt)  # plug in your LLM interface
    return response



