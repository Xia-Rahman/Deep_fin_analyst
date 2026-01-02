
import json
from research_agent.clients import call_openrouter
from research_agent.new_config import ENSEMBLE_MODELS, PLANNER_MODEL_ID

def ensemble_query(query: str, context: str = "") -> str:
    """
    Executes a query using 3 different models and uses a meta-model to select the best answer.
    
    Args:
        query: The question or task to execute
        context: Any relevant context from previous steps
        
    Returns:
        The synthesized/selected best answer
    """
    print(f"\n🔄 ENSEMBLE: Running query through {len(ENSEMBLE_MODELS)} models...")
    
    # Prepare the prompt for each model
    prompt = f"""Context: {context}

Task: {query}

Provide a clear, accurate answer."""
    
    # Collect responses from all models
    responses = []
    for i, model_id in enumerate(ENSEMBLE_MODELS):
        print(f"   Model {i+1}/{len(ENSEMBLE_MODELS)}: {model_id}")
        try:
            response = call_openrouter(prompt, model_id)
            responses.append({
                "model": model_id,
                "response": response
            })
        except Exception as e:
            responses.append({
                "model": model_id,
                "response": f"Error: {str(e)}"
            })
    
    # Use Meta-Model (405B) to select/synthesize the best answer
    print(f"\n🧠 META-MODEL ({PLANNER_MODEL_ID}): Synthesizing ensemble results...")
    
    meta_prompt = f"""You are a Meta-Judge AI evaluating multiple model responses to select or synthesize the best answer.

Original Query: {query}

Model Responses:
{json.dumps(responses, indent=2)}

INSTRUCTIONS:
1. Compare the responses for accuracy, completeness, and relevance.
2. If one response is clearly superior, select it.
3. If multiple responses have complementary strengths, synthesize them into a unified answer.
4. Return ONLY the final answer (not meta-commentary about the models).

Final Answer:"""
    
    final_answer = call_openrouter(meta_prompt, PLANNER_MODEL_ID)
    
    print(f"✅ ENSEMBLE COMPLETE")
    return final_answer
