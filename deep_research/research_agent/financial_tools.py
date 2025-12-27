"""Financial Tools.

This module provides programmatic access to financial data and calculations,
ensuring mathematical accuracy separate from LLM reasoning.
"""

import yfinance as yf
from langchain_core.tools import tool

def calculate_cagr(start_value, end_value, periods):
    """Programmatic CAGR calculation to ensure math accuracy."""
    if start_value == 0 or periods == 0:
        return 0
    return (end_value / start_value) ** (1 / periods) - 1

@tool(parse_docstring=True)
def get_company_fundamentals(ticker: str) -> str:
    """Fetch core fundamental data and calculated metrics for a specific company.

    Use this tool to get accurate numbers for revenue, margins, and ratios.
    Do NOT hallucinate financial figures. 
    For Indian companies, append .NS (NSE) or .BO (BSE).
    
    Args:
        ticker: The stock ticker symbol (e.g., INFY.NS, TCS.NS, AAPL, PFE).

    Returns:
        Markdown formatted financial summary including Valuation, Margins, Growth, and Balance Sheet.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Helper to safely get data
        def get_val(key, fmt="{:.2f}"):
            val = info.get(key)
            if val is None: return "N/A"
            if isinstance(val, (int, float)):
                return fmt.format(val)
            return val

        # Construct the financial card
        report = f"""## Financial Fundamentals: {ticker}
        
### Valuation & Size
- **Market Cap:** {get_val('marketCap', '{:,.0f}')}
- **Enterprise Value:** {get_val('enterpriseValue', '{:,.0f}')}
- **Trailing P/E:** {get_val('trailingPE')}
- **Forward P/E:** {get_val('forwardPE')}
- **PEG Ratio:** {get_val('pegRatio')}
- **Price/Book:** {get_val('priceToBook')}

### Profitability & Returns
- **Gross Margin:** {get_val('grossMargins', '{:.2%}')}
- **Operating Margin:** {get_val('operatingMargins', '{:.2%}')}
- **Net Margin:** {get_val('profitMargins', '{:.2%}')}
- **ROE:** {get_val('returnOnEquity', '{:.2%}')}
- **ROA:** {get_val('returnOnAssets', '{:.2%}')}

### Growth & Strength
- **Revenue Growth (YoY):** {get_val('revenueGrowth', '{:.2%}')}
- **Earnings Growth (YoY):** {get_val('earningsGrowth', '{:.2%}')}
- **Total Cash:** {get_val('totalCash', '{:,.0f}')}
- **Total Debt:** {get_val('totalDebt', '{:,.0f}')}
- **Current Ratio:** {get_val('currentRatio')}
"""
        return report
    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"

@tool(parse_docstring=True)
def get_historical_performance(tickers: str, period: str = "5y") -> str:
    """Fetch historical stock performance and calculate CAGR for multiple companies.
    
    Args:
        tickers: Space-separated list of tickers (e.g., "TCS.NS INFY.NS WIPRO.NS")
        period: Time period (1y, 3y, 5y, 10y, ytd)

    Returns:
        Comparative performance table with calculated CAGRs.
    """
    try:
        ticker_list = tickers.split()
        data = yf.download(ticker_list, period=period)['Adj Close']
        
        results = []
        for ticker in ticker_list:
            # Handle single vs multi ticker return structure
            series = data[ticker] if len(ticker_list) > 1 else data
            
            # Get clean start/end
            series = series.dropna()
            if series.empty:
                results.append(f"| {ticker} | No Data | No Data | N/A | N/A |")
                continue

            start_price = series.iloc[0]
            end_price = series.iloc[-1]
            
            # Approximate years based on period string
            years = 1
            if 'y' in period and period != 'ytd':
                years = int(period.replace('y', ''))
            
            cagr = calculate_cagr(start_price, end_price, years)
            total_return = (end_price - start_price) / start_price
            
            results.append(f"| {ticker} | {start_price:.2f} | {end_price:.2f} | {total_return:.2%} | {cagr:.2%} |")
            
        table = f"""## Comparative Performance ({period})
| Ticker | Start Price | End Price | Total Return | CAGR |
|--------|-------------|-----------|--------------|------|
{chr(10).join(results)}
"""
        return table
    except Exception as e:
        return f"Error calculating performance: {str(e)}"
