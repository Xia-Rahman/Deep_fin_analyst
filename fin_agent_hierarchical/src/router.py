from src.clients import call_openrouter

def decide_complexity(query: str) -> int:
    """
    Analyzes the query and returns an integer 1-5.
    Uses a cheap/fast model for this decision.
    """
    router_prompt = f"""
    You are a Compute Resource Allocator. Analyze the user query and assign a Complexity Level (1-5).
    
    DEFINITIONS:
    Level 1: Simple formatting, spelling fix, data extraction.
    Level 2: Routine questions, simple summaries, known facts, "what is X".
    Level 3: Comparative analysis, code generation, intermediate reasoning, "Compare X and Y".
    Level 4: Strategic planning, complex synthesis, multi-step logic.
    Level 5: Deep research, novel discovery, extremely complex financial forecasting, requires "thinking".
    
    QUERY: {query}
    
    Reply ONLY with the single integer number (1, 2, 3, 4, or 5). Do not write anything else.
    """
    
    # Use a fast model for routing (e.g., Llama 3 8B or Mistral)
    result = call_openrouter(router_prompt, "meta-llama/llama-3.2-3b-instruct:free")
    
    try:
        if "Error" in result:
            print(f"Router Error: {result}")
            return 3 # Default to intermediate

        level = int(result.strip())
        # Clamp between 1 and 5
        return max(1, min(5, level))
    except:
        return 3 # Default to intermediate if parsing fails
