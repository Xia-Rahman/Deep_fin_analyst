import subprocess
import json
from langchain.tools import tool

@tool
def ask_gemini_cli_tool(query: str) -> str:
    print(f"\n[DEBUG] Sending query to Gemini: {query[:50]}...")
    
    command = ["gemini", "-p", query, "--output-format", "json"]
    
    try:
        # Capture BOTH stdout and stderr
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True
        )
        
        # DEBUG: Check if there was an error in the CLI itself
        if result.returncode != 0:
            print(f"[ERROR] CLI Code {result.returncode}")
            print(f"[ERROR] Stderr: {result.stderr}")
            return f"Error executing Gemini CLI: {result.stderr}"

        # DEBUG: unexpected empty output
        if not result.stdout.strip():
            print(f"[ERROR] CLI returned empty stdout. Stderr was: {result.stderr}")
            return "Error: Gemini CLI returned no output."

        # Parse the JSON
        try:
            data = json.loads(result.stdout)
            
            # EXTRACT the content. 
            # Based on your logs, the valid answer is in data['response']
            if isinstance(data, dict) and 'response' in data:
                return data['response']
            return str(data)
            
        except json.JSONDecodeError:
            # Fallback for when CLI prints raw text instead of JSON
            return result.stdout

    except Exception as e:
        return f"System Error: {str(e)}"