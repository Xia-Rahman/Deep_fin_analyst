
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

# Adjust import path to ensuring research_agent can be imported
import sys
import os
os.environ['TAVILY_API_KEY'] = 'test_key' # Mock key to prevent Import Error
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research_agent.financial_tools import (
    calculate_cagr,
    get_company_fundamentals,
    get_historical_performance
)

class TestFinancialTools(unittest.TestCase):

    def test_calculate_cagr(self):
        # Test basic calculation: 100 -> 200 in 1 year = 100%
        self.assertAlmostEqual(calculate_cagr(100, 200, 1), 1.0)
        
        # Test basic calculation: 100 -> 121 in 2 years = 10%
        self.assertAlmostEqual(calculate_cagr(100, 121, 2), 0.1)
        
        # Test zero start value
        self.assertEqual(calculate_cagr(0, 100, 5), 0)
        
        # Test zero periods
        self.assertEqual(calculate_cagr(100, 200, 0), 0)

    @patch('research_agent.financial_tools.yf.Ticker')
    def test_get_company_fundamentals_success(self, mock_ticker):
        # Setup mock data using a dictionary for info
        mock_stock = MagicMock()
        mock_stock.info = {
            'marketCap': 1000000,
            'enterpriseValue': 1200000,
            'trailingPE': 25.5,
            'forwardPE': 20.0,
            'pegRatio': 1.5,
            'priceToBook': 5.0,
            'grossMargins': 0.45,
            'operatingMargins': 0.25,
            'profitMargins': 0.15,
            'returnOnEquity': 0.20,
            'returnOnAssets': 0.10,
            'revenueGrowth': 0.05,
            'earningsGrowth': 0.08,
            'totalCash': 500000,
            'totalDebt': 200000,
            'currentRatio': 2.5
        }
        mock_ticker.return_value = mock_stock

        # LangChain tools must be called via invoke with a dict
        result = get_company_fundamentals.invoke({"ticker": "TEST"})
        
        # Verify Key Metrics are present in the output
        self.assertIn("1,000,000", result) # Market Cap
        self.assertIn("25.50", result)     # Trailing PE
        self.assertIn("45.00%", result)    # Gross Margin
        self.assertIn("TEST", result)     # Ticker in title

    @patch('research_agent.financial_tools.yf.Ticker')
    def test_get_company_fundamentals_missing_data(self, mock_ticker):
        # Setup mock with missing data
        mock_stock = MagicMock()
        mock_stock.info = {} # Empty info
        mock_ticker.return_value = mock_stock
        
        result = get_company_fundamentals.invoke({"ticker": "EMPTY"})
        
        # Should gracefully handle N/A
        self.assertIn("N/A", result)

    @patch('research_agent.financial_tools.yf.download')
    def test_get_historical_performance_multi(self, mock_download):
        # Create a mock DataFrame for multi-ticker
        dates = pd.date_range(start='2020-01-01', periods=2)
        data = {
            'TCS.NS': [100.0, 200.0],
            'INFY.NS': [50.0, 75.0]
        }
        
        # Mocking the return of yf.download
        class MockYFResult:
            def __getitem__(self, item):
                if item == 'Adj Close':
                    return pd.DataFrame(data, index=dates)
                return None
        
        mock_download.return_value = MockYFResult()

        result = get_historical_performance.invoke({"tickers": "TCS.NS INFY.NS", "period": "1y"})
        
        # TCS: 100 -> 200 (100% return)
        self.assertIn("TCS.NS", result)
        self.assertIn("100.00%", result) # Total Return
        
        # INFY: 50 -> 75 (50% return)
        self.assertIn("INFY.NS", result)
        self.assertIn("50.00%", result)

    @patch('research_agent.financial_tools.yf.download')
    def test_get_historical_performance_single(self, mock_download):
        dates = pd.date_range(start='2020-01-01', periods=2)
        prices = [100.0, 110.0]
        
        mock_series = pd.Series(prices, index=dates, name='Adj Close')
        
        class MockYFResult:
            def __getitem__(self, item):
                if item == 'Adj Close':
                    return mock_series
                return None
        
        mock_download.return_value = MockYFResult()
        
        result = get_historical_performance.invoke({"tickers": "AAPL", "period": "1y"})
        
        self.assertIn("AAPL", result)
        self.assertIn("10.00%", result) # 100->110 = 10%

if __name__ == '__main__':
    unittest.main()
