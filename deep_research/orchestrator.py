"""
orchestrator.py
"""
from typing import List, TypedDict, Dict
from langgraph.graph import StateGraph, END
import json
import re
from termcolor import cprint

# --- IMPORTS ---
# We keep OpenRouter for Executor/Reporter, but add Gemini Tool for Planner
from research_agent.clients import call_openrouter
from research_agent.gemini_cli_tool import ask_gemini_cli_tool# <--- NEW IMPORT
from research_agent.new_config import PLANNER_MODEL_ID, ENSEMBLE_MODELS
from research_agent.tools import tavily_search
from research_agent.financial_tools import get_company_fundamentals, get_historical_performance
from research_agent.ensemble import ensemble_query
from research_agent.skills import load_skill, SKILL_LIBRARY

# --- CONFIGURATION ---
EXECUTOR_MODEL_ID = "meta-llama/llama-3.3-70b-instruct" 

# --- STATE DEFINITION ---
class ResearchState(TypedDict):
    task: str
    companies: List[str]
    background_research: str
    plan: List[str]
    current_step_index: int
    step_results: Dict[str, str]
    final_report: str

# --- PROMPTS ---

PLANNER_PROMPT = """You are a Principal Financial Research Architect conducting DEEP RESEARCH MODE.

You are building a FINANCIAL DEEP RESEARCH AGENT that replicates advanced capabilities:
- Execute extensive research loops (5-10+ distinct actions for complex queries)
- Synthesize information from diverse financial sources
- Demonstrate research intelligence by adapting queries based on findings

BACKGROUND RESEARCH COMPLETED:
{background}

USER QUERY: "{task}"

YOUR RESEARCH PLANNING PHILOSOPHY:
1. INITIAL EXPLORATION: Start broad
2. ITERATIVE DEEPENING: Each finding informs the next query
3. SOURCE DIVERSIFICATION: Web search, Financial APIs, Professional Skills

AVAILABLE TOOLS:
- analyze_sec_filing_structure, assess_competitive_forces, evaluate_capital_allocation, perform_ratio_analysis
- get_company_fundamentals(ticker), get_historical_performance(tickers, period)
- tavily_search(query), ensemble_query(query)

OUTPUT FORMAT:
Return ONLY a valid JSON array of sequential steps strings. Do not add markdown blocks like ```json.
Example:
["analyze_sec_filing_structure TCS.NS", "get_company_fundamentals TCS.NS", "assess_competitive_forces TCS", "Synthesize report"]
"""

EXECUTOR_PROMPT = """You are a Senior Financial Analyst executing ONE STEP of a deep research plan.

CURRENT STEP: {step}
CONTEXT FROM PREVIOUS STEPS: {context}

OUTPUT INSTRUCTIONS:
If a specific tool is required, output EXACTLY: TOOL: <tool_name> ARGS: <json_args>
If analysis/reasoning is required, output: TOOL: ensemble_query ARGS: {{"query": "your analytical question"}}
If synthesis is required, just write the synthesis text directly.

Tools available: tavily_search, get_company_fundamentals, get_historical_performance, load_skill, ensemble_query.
"""

# --- HELPER: Extract Company Tickers ---
def extract_companies(task: str) -> List[str]:
    patterns = [r"TCS", r"Infosys", r"INFY", r"Wipro", r"HCL Tech", r"Tech Mahindra", r"Gold"]
    companies = []
    for pattern in patterns:
        if re.search(pattern, task, re.IGNORECASE):
            if "TCS" in pattern: companies.append("TCS.NS")
            elif "Infosys" in pattern or "INFY" in pattern: companies.append("INFY.NS")
            elif "Wipro" in pattern: companies.append("WIPRO.NS")
            elif "Gold" in pattern: companies.append("COMMODITY: GOLD")
    return list(set(companies))

# --- NODES ---

def research_background_node(state: ResearchState):
    cprint("\n[DEBUG] === BACKGROUND RESEARCH NODE STARTED ===", "cyan")
    task = state["task"]
    companies = extract_companies(task)
    
    background_results = []
    
    # STEP 0: ANALYZE QUERY (Using GEMINI CLI TOOL)
    print(f"\n   🎯 STEP 0: Query Analysis & Core Entity Research")
    try:
        analysis_prompt = f"""
        Analyze this financial query: "{task}"
        Extract:
        1. Core Entity (company, sector, market)
        2. Focus Areas
        3. Suggested Generic Search Query
        
        Return ONLY valid JSON: {{ "core_entity": "...", "focus_areas": [], "generic_search": "..." }}
        """
        
        cprint("[DEBUG] Analyzing query via Gemini CLI Tool...", "cyan")
        
        # --- CHANGED: USE GEMINI CLI TOOL ---
        # invoke() expects a dictionary with the argument name 'query'
        analysis_response = ask_gemini_cli_tool.invoke({"query": analysis_prompt})
        
        cleaned_analysis = analysis_response.replace("```json", "").replace("```", "").strip()
        analysis = json.loads(cleaned_analysis)
        
        core_entity = analysis.get("core_entity", task)
        generic_search = analysis.get("generic_search", task)
        
        print(f"      \u2713 Core Entity: {core_entity}")
        print(f"      [0] Generic Search: {generic_search[:60]}...")
        
        generic_result = tavily_search.invoke({"query": generic_search})
        background_results.append(f"## CORE ENTITY RESEARCH: {core_entity}\n\n{generic_result[:1000]}...")
        
    except Exception as e:
        cprint(f"[DEBUG] Analysis failed ({e}), using fallback search.", "yellow")
        basic_search = tavily_search.invoke({"query": task})
        background_results.append(f"## BASIC SEARCH\n\n{basic_search[:1000]}...")

    # Continue with targeted searches
    if companies:
        for company in companies[:2]:
            try:
                print(f"      Researching {company}...")
                news = tavily_search.invoke({"query": f"{company} latest news financial analysis"})
                background_results.append(f"## {company} NEWS\n{news[:600]}...")
            except: pass

    background = "\n\n".join(background_results) if background_results else "No background info."
    return {"companies": companies, "background_research": background}


def planner_node(state: ResearchState):
    cprint("\n[DEBUG] === PLANNER NODE STARTED ===", "blue")
    task = state["task"]
    background = state.get("background_research", "")
    
    # Truncate background if massive
    if len(background) > 20000: 
        background = background[:20000] + "...(truncated)"

    prompt = PLANNER_PROMPT.format(task=task, background=background)
    
    cprint(f"[DEBUG] Generating Plan via Gemini CLI Tool...", "blue")

    max_retries = 3
    plan = []
    
    for attempt in range(max_retries):
        try:
            # --- CHANGED: USE GEMINI CLI TOOL ---
            response = ask_gemini_cli_tool.invoke({"query": prompt})
            
            # Clean Markdown wrappers often returned by LLMs
            cleaned = response.replace("```json", "").replace("```", "").strip()
            
            # Extract JSON array if surrounded by text
            start_idx = cleaned.find('[')
            end_idx = cleaned.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                cleaned = cleaned[start_idx:end_idx]

            plan = json.loads(cleaned)
            cprint(f"[DEBUG] Successfully parsed plan with {len(plan)} steps", "blue")
            break
        except Exception as e:
            cprint(f"[DEBUG] Plan parse error (attempt {attempt+1}): {str(e)}", "yellow")
            if attempt == max_retries - 1:
                print("[ERROR] Fallback to simple plan.")
                plan = [f"Research {task} thoroughly", "Synthesize findings"]

    print(f"📋 PLAN GENERATED: {len(plan)} steps.")
    for i, step in enumerate(plan):
        print(f"   {i + 1}. {step}")

    return {"plan": plan, "current_step_index": 0, "step_results": {}}

def approval_node(state: ResearchState):
    return {"plan": state["plan"]}

def executor_node(state: ResearchState):
    # Executor remains on Llama 3.3 70B (OpenRouter) for tool handling
    step_idx = state["current_step_index"]
    plan = state["plan"]
    
    if step_idx >= len(plan):
        return {"step_results": state["step_results"], "current_step_index": step_idx}

    task = plan[step_idx]
    cprint(f"\n[DEBUG] === EXECUTING STEP {step_idx + 1}/{len(plan)}: {task} ===", "magenta")
    
    context_str = "\n".join([f"Step '{k}': {v[:300]}..." for k, v in state["step_results"].items()])

    is_analysis = any(k in task.lower() for k in ["compare", "analyze", "evaluate", "synthesize"])
    result_text = ""
    
    try:
        if is_analysis and "ensemble" in task.lower():
            cprint("[DEBUG] Routing to Ensemble Engine...", "magenta")
            result_text = ensemble_query(task, context_str)
        else:
            tool_prompt = f"""
            {EXECUTOR_PROMPT.format(step=task, context=context_str)}
            Based on the task, select the best tool. Respond ONLY with: TOOL: <name> ARGS: <json>
            """
            
            # Using OpenRouter for Executor (Tools)
            cprint(f"[DEBUG] Selecting tool via {EXECUTOR_MODEL_ID}...", "magenta")
            response = call_openrouter(tool_prompt, EXECUTOR_MODEL_ID)
            
            if "TOOL:" in response:
                parts = response.split("TOOL:")[1].split("ARGS:")
                tool_name = parts[0].strip()
                args_str = parts[1].strip()
                try:
                    args = json.loads(args_str)
                    cprint(f"[DEBUG] Tool Call: {tool_name} {args}", "yellow")
                    
                    if tool_name == "tavily_search":
                        tool_output = tavily_search.invoke(args)
                    elif tool_name == "get_company_fundamentals":
                        tool_output = get_company_fundamentals.invoke(args)
                    elif tool_name == "get_historical_performance":
                        tool_output = get_historical_performance.invoke(args)
                    elif tool_name == "ensemble_query":
                        tool_output = ensemble_query(args.get("query", task), context_str)
                    elif tool_name == "load_skill":
                        tool_output = load_skill.invoke(args)
                    else:
                        tool_output = f"Unknown tool: {tool_name}"
                        
                    result_text = f"Tool Output:\n{tool_output}"
                except Exception as e:
                    result_text = f"Tool Execution Failed: {str(e)}"
            else:
                result_text = response

    except Exception as e:
        result_text = f"Step Failed: {str(e)}"

    return {
        "step_results": {**state["step_results"], task: result_text},
        "current_step_index": step_idx + 1
    }

def orchestrator_check(state: ResearchState):
    if state["current_step_index"] < len(state["plan"]):
        return "continue"
    return "finalize"

def reporter_node(state: ResearchState):
    # Reporter remains on OpenRouter (Llama 405B) for high quality writing
    cprint("\n[DEBUG] === REPORTER NODE STARTED ===", "green")
    
    print(f"\n✍️ WRITER ({PLANNER_MODEL_ID}): Synthesizing Final Report...")
    
    context_str = "\n".join([f"## Finding from '{k}'\n{v}" for k,v in state["step_results"].items()])
    
    final_prompt = f"""
    You are the Chief Financial Editor.
    Compile the research notes into a comprehensive, professional financial report in Markdown.
    
    Original Task: {state["task"]}
    
    RESEARCH NOTES:
    {context_str}
    
    Final Report (Use Headers, Tables, Bullet Points):
    """
    
    report = call_openrouter(final_prompt, PLANNER_MODEL_ID)
    return {"final_report": report}

# --- GRAPH ---
builder = StateGraph(ResearchState)
builder.add_node("background_research", research_background_node)
builder.add_node("planner", planner_node)
builder.add_node("approval", approval_node)
builder.add_node("executor", executor_node)
builder.add_node("reporter", reporter_node)

builder.set_entry_point("background_research")
builder.add_edge("background_research", "planner")
builder.add_edge("planner", "approval")
builder.add_edge("approval", "executor")
builder.add_conditional_edges("executor", orchestrator_check, {
    "continue": "executor",
    "finalize": "reporter"
})
builder.add_edge("reporter", END)

orchestrator_app = builder.compile()