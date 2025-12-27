import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env", override=True)

# DeepAgents and LangChain imports - NOT USED FOR ROUTING EXECUTION directly in this hybrid mode
# We are manually orchestrating execution based on router decision now.

# Import our modular Financial components
from research_agent.router import decide_complexity
from research_agent.clients import call_gemini_deep_think, call_openrouter
from research_agent.config import *
from termcolor import colored

def main():
    print(colored("🚀 Initializing Hierarchical Financial Agent (in deep_research)...", "cyan"))
    print(colored("   - Level 1-4: OpenRouter (Llama/Mistral/Claude)", "blue"))
    print(colored("   - Level 5:   Google Gemini (Deep Think)", "green"))
    
    # Check for CLI arguments or run interactive mode
    if len(sys.argv) > 1:
        queries = [" ".join(sys.argv[1:])]
    else:
        print("\n💡 Enter a query to route through the hierarchy (or 'q' to quit).")
        queries = []

    while True:
        if not queries:
            try:
                user_input = input(colored("\n💰 Query: ", "yellow"))
                if user_input.lower() in ['q', 'exit', 'quit']: break
                if not user_input.strip(): continue
                current_query = user_input
            except KeyboardInterrupt:
                break
        else:
            current_query = queries.pop(0)

        print(colored(f"\n🔎 Processing: '{current_query}'", "white", attrs=["bold"]))
        
        # 1. ROUTE
        print(colored(f"🤔 ROUTER: Analyzing complexity...", "magenta"))
        level = decide_complexity(current_query)
        print(colored(f"🎯 ROUTER DECISION: Level {level}", "magenta", attrs=["bold"]))

        # 2. EXECUTE
        final_response = ""
        try:
            if level == 5:
                print(colored(f"🧠 Routing to Level 5 (Gemini Deep Think)...", "green"))
                final_response = call_gemini_deep_think(current_query)
            elif level == 4:
                print(colored(f"⚡ Routing to Level 4 ({LEVEL_4_MODEL})...", "blue"))
                final_response = call_openrouter(current_query, LEVEL_4_MODEL)
            elif level == 3:
                print(colored(f"⚡ Routing to Level 3 ({LEVEL_3_MODEL})...", "blue"))
                final_response = call_openrouter(current_query, LEVEL_3_MODEL)
            elif level == 2:
                print(colored(f"⚡ Routing to Level 2 ({LEVEL_2_MODEL})...", "blue"))
                final_response = call_openrouter(current_query, LEVEL_2_MODEL)
            else: # Level 1
                print(colored(f"⚡ Routing to Level 1 ({LEVEL_1_MODEL})...", "blue"))
                final_response = call_openrouter(current_query, LEVEL_1_MODEL)
            
            print(colored("\n✅ Response:", "green", attrs=["bold"]))
            print(final_response)
            
        except Exception as e:
            print(colored(f"\n❌ Error: {str(e)}", "red"))

        if len(sys.argv) > 1:
            break

if __name__ == "__main__":
    main()
