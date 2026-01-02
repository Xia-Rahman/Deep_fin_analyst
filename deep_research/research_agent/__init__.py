
# Creates the research_agent package
from research_agent.prompts import (
    FINANCIAL_RESEARCHER_INSTRUCTIONS,
    FINANCIAL_WORKFLOW_INSTRUCTIONS,
    SUBAGENT_DELEGATION_INSTRUCTIONS,
)
from research_agent.tools import tavily_search, think_tool
from research_agent.financial_tools import get_company_fundamentals, get_historical_performance
from research_agent.gemini_cli_tool import ask_gemini_cli_tool

__all__ = [
    "tavily_search",
    "think_tool",
    "get_company_fundamentals",
    "get_historical_performance",
    "ask_gemini_cli_tool",
    "FINANCIAL_RESEARCHER_INSTRUCTIONS",
    "FINANCIAL_WORKFLOW_INSTRUCTIONS",
    "SUBAGENT_DELEGATION_INSTRUCTIONS",
]
