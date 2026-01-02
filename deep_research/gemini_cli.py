"""
gemini_cli.py
"""
import sys
import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv(".env", override=True)

def call_gemini(prompt_text):
    # Fallback requires API Key since it doesn't use the authenticated global CLI
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "Error: No API key found (Required for local fallback)"

    # --- STABLE MODEL & RETRY LOGIC ---
    model_name = "gemini-1.5-flash" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    max_retries = 5
    base_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 429:
                wait = base_delay * (2 ** attempt)
                print(f"[CLI] Rate Limit (429). Retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            
            response.raise_for_status()
            result = response.json()
            if "candidates" in result:
                return result["candidates"][0]["content"]["parts"][0]["text"].strip()
            return "Error: Empty response"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(base_delay)
                continue
            return f"Error: {str(e)}"
    
    return "Error: Rate Limit Exceeded"

def main():
    args = sys.argv[1:]
    prompt = ""
    if "-p" in args:
        try:
            prompt = args[args.index("-p") + 1]
        except: pass
    elif args:
        prompt = " ".join(args)
    
    if not prompt and not sys.stdin.isatty():
        prompt = sys.stdin.read()
        
    if prompt:
        print(call_gemini(prompt))
    else:
        print("Error: No prompt", file=sys.stderr)

if __name__ == "__main__":
    main()