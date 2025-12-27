from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.router import decide_complexity
from src.clients import call_gemini_deep_think, call_openrouter
from src.config import *

# --- NODES ---

def router_node(state: AgentState):
    print(f"🤔 ROUTER: Analyzing complexity for: '{state['query']}'")
    level = decide_complexity(state['query'])
    print(f"🎯 ROUTER DECISION: Level {level}")
    return {"complexity_level": level}

def execution_node(state: AgentState):
    level = state['complexity_level']
    query = state['query']
    response = ""
    
    if level == 5:
        # Use Google GenAI SDK (Gemini Thinking)
        response = call_gemini_deep_think(query)
    elif level == 4:
        response = call_openrouter(query, LEVEL_4_MODEL)
    elif level == 3:
        response = call_openrouter(query, LEVEL_3_MODEL)
    elif level == 2:
        response = call_openrouter(query, LEVEL_2_MODEL)
    else: # Level 1
        response = call_openrouter(query, LEVEL_1_MODEL)
    
    return {"final_response": response}

# --- GRAPH DEFINITION ---

workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("execution", execution_node)

workflow.set_entry_point("router")
workflow.add_edge("router", "execution")
workflow.add_edge("execution", END)

app = workflow.compile()
