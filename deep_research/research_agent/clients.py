import os
import json
import requests
import subprocess
from google import genai
from google.genai import types
from dotenv import load_dotenv
import sys 

from research_agent.config import MODEL_LIMITS, LEVEL_5_MODEL
from research_agent.rate_limiter import GLOBAL_RATE_LIMITER

load_dotenv(override=True)

# --- GOOGLE GENAI CLIENT (Level 5) ---
def call_gemini_deep_think(prompt: str):
    """
    Uses Gemini 3 Pro Preview with High Thinking config.
    """
    # 1. Rate Limit Check
    limit = MODEL_LIMITS.get(LEVEL_5_MODEL, MODEL_LIMITS["default"])
    GLOBAL_RATE_LIMITER.wait_for_slot(LEVEL_5_MODEL, limit)
    
    print("🧠 INVOKING GEMINI 3 PRO PREVIEW (DEEP THINKING)...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY not found in environment variables."

    import time
    
    # REVERTING TO USER CODE SNIPPET EXACTLY
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-3-pro-preview" 
    
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    
    # Enable Google Search tool + Thinking
    tools = [
        types.Tool(google_search=types.GoogleSearch()),
    ]
    
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(include_thoughts=True),
        tools=tools,
        response_modalities=["TEXT"],
    )

    full_response = []
    
    # Retry loop for 429 errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print("\n--- GEMINI THINKING PROCESS ---")
            full_response = []
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config,
            ):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    full_response.append(chunk.text)
            
            # If we get here success
            print("\n--- END THINKING ---\n")
            return "".join(full_response)

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = 15 * (attempt + 1)
                print(f"\n⚠️ Gemini Rate Limit Hit (Attempt {attempt+1}/{max_retries}). Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                return f"Gemini Error: {str(e)}"
    
    return "Error: Gemini Rate Limit Exceeded after retries."

# --- OPENROUTER CLIENT (Levels 1-4) ---
def call_openrouter(prompt: str, model_id: str):
    """
    Generic wrapper for OpenRouter models.
    """
    # 1. Rate Limit Check
    limit = MODEL_LIMITS.get(model_id, MODEL_LIMITS["default"])
    GLOBAL_RATE_LIMITER.wait_for_slot(model_id, limit)
    
    print(f"⚡ INVOKING OPENROUTER: {model_id}")
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return "Error: OPENROUTER_API_KEY not found in environment variables."

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://localhost:3000", 
            },
            data=json.dumps({
                "model": model_id,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"OpenRouter Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"OpenRouter Connection Error: {str(e)}"

from research_agent.rate_limiter import GLOBAL_RATE_LIMITER

load_dotenv(override=True)

# --- GEMINI CLI WRAPPER ---
def ask_gemini_cli(prompt: str) -> str:
    """
    Sends a prompt to the Gemini CLI.
    Tries 'gemini' command first, falls back to local 'gemini_cli.py'.
    """
    GLOBAL_RATE_LIMITER.wait_for_slot("gemini", 15)
    
    print("🤖 INVOKING GEMINI CLI...")
    
    # 1. Try Global Command
    try:
        result = subprocess.run(
            ["gemini", "-p", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        # 2. Fallback: Try local script in project root
        try:
            # Find the script relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script_path = os.path.join(base_dir, "gemini_cli.py")
            
            if os.path.exists(script_path):
                # Run with current python executable
                result = subprocess.run(
                    [sys.executable, script_path, "-p", prompt],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            else:
                return "Error: Could not find gemini command or gemini_cli.py"
                
        except Exception as e:
            return f"Gemini CLI Fallback Error: {str(e)}"
    except Exception as e:
        return f"Gemini CLI Error: {str(e)}"

# Alias for backward compatibility with orchestrator
call_gemini = ask_gemini_cli

# --- OTHER CLIENTS (Preserved for compatibility) ---
# (OpenRouter and other client functions remain unchanged)
def call_openrouter(prompt: str, model_id: str):
    # ... existing implementation ...
    from research_agent.config import MODEL_LIMITS
    limit = MODEL_LIMITS.get(model_id, 10)
    GLOBAL_RATE_LIMITER.wait_for_slot(model_id, limit)
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key: return "Error: No API key."
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Connection Error: {e}"