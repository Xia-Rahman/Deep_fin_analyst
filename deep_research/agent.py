
"""Financial Research Agent - Standalone script."""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env", override=True)

from langchain_openai import ChatOpenAI
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
from research_agent.gemini_cli_tool import ask_gemini_cli_tool

# Configuration
max_concurrent_research_units = 3
max_researcher_iterations = 5 
current_date = datetime.now().strftime("%Y-%m-%d")

# --- MODEL SETUP ---

# PLANNER / ORCHESTRATOR / WRITER: Llama 3.1 405B (The "Brain")
planner_model = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="meta-llama/llama-3.1-405b-instruct",
    temperature=0.0,
    max_tokens=2000, # Validation/Report needs space
)

# EXECUTOR / SUB-AGENT: Llama 3.3 70B (The "Worker")
executor_model = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="meta-llama/llama-3.3-70b-instruct",
    temperature=0.0,
    max_tokens=2000,
)

# --- PROMPT ENHANCEMENT FOR VALIDATION ---
VALIDATION_INSTRUCTION = """
\n
CRITICAL STEP: FACT VALIDATION & REPORT SYNTHESIS
Before creating the final report, you MUST:
1. Review all data collected by sub-agents.
2. Cross-reference specific numbers (revenue, margins, CAGR) if multiple sources exist.
3. Explicitly state "Verified" next to high-confidence data in the final report.
4. Flag any inconsistencies.

The Final Report must be high-quality, professional markdown, suitable for an investment memo.
"""

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
    + VALIDATION_INSTRUCTION
)

# Define the Toolset 
financial_tools = [
    tavily_search, 
    think_tool,
    get_company_fundamentals,
    get_historical_performance,
    ask_gemini_cli_tool  # NEW: Gemini CLI for secondary inference
]

# Create the Financial Analyst Sub-agent
# We try to pass the executor model here. 
# If deepagents package doesn't support 'model' key, it might ignore it or error.
# Given I cannot see the package, this is a best-effort consistent with other LangChain agent structures.
research_sub_agent = {
    "name": "financial-analyst",
    "description": "Delegate financial research tasks (Data Fetching, Market Search).",
    "system_prompt": FINANCIAL_RESEARCHER_INSTRUCTIONS.format(date=current_date),
    "tools": financial_tools,
    "model": executor_model, # Attempt to assign specific model
}

# Create the Deep Agent (Planner)
agent = create_deep_agent(
    model=planner_model,        # 405B for Planning and Synthesis
    tools=financial_tools,      # Orchestrator tools
    system_prompt=INSTRUCTIONS,
    subagents=[research_sub_agent],
)
