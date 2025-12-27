"""Financial Research Agent - Standalone script."""

from datetime import datetime
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents import create_deep_agent

# 1. Import Modified Prompts
from research_agent.prompts import (
    FINANCIAL_RESEARCHER_INSTRUCTIONS,
    FINANCIAL_WORKFLOW_INSTRUCTIONS,
    SUBAGENT_DELEGATION_INSTRUCTIONS,
)

# 2. Import Tools (Native + Financial)
from research_agent.tools import tavily_search, think_tool
from research_agent.financial_tools import get_company_fundamentals, get_historical_performance

# Configuration
max_concurrent_research_units = 3
max_researcher_iterations = 5  # Financial research needs depth

current_date = datetime.now().strftime("%Y-%m-%d")

# Combine instructions
INSTRUCTIONS = (
    FINANCIAL_WORKFLOW_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + SUBAGENT_DELEGATION_INSTRUCTIONS.format(
        max_concurrent_research_units=max_concurrent_research_units,
        max_researcher_iterations=max_researcher_iterations,
    )
)

# Define the Toolset (Sub-agents need direct access to financial data)
financial_tools = [
    tavily_search, 
    think_tool,
    get_company_fundamentals,
    get_historical_performance
]

# Create the Financial Analyst Sub-agent
research_sub_agent = {
    "name": "financial-analyst",
    "description": "Delegate financial research tasks. Can analyze stocks, sectors, and financial metrics.",
    "system_prompt": FINANCIAL_RESEARCHER_INSTRUCTIONS.format(date=current_date),
    "tools": financial_tools,
}

# Model Selection (Gemini 3 Pro recommended for handling long Annual Reports)
model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", temperature=0.0)
# Alternative: model = init_chat_model(model="anthropic:claude-sonnet-4-5-20250929", temperature=0.0)

# Create the Deep Agent
agent = create_deep_agent(
    model=model,
    tools=financial_tools,  # Orchestrator also gets tools to verify
    system_prompt=INSTRUCTIONS,
    subagents=[research_sub_agent],
)
