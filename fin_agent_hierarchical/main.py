import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv(".env", override=True)

from src.graph import app
from termcolor import colored

def main():
    print(colored("🚀 Initializing Hierarchical Financial Agent...", "cyan"))
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
        
        inputs = {"query": current_query}

        try:
            # Run the graph
            result = app.invoke(inputs)
            
            final_response = result.get("final_response", "No response generated.")
            
            print(colored("\n✅ Response:", "green", attrs=["bold"]))
            print(final_response)
            
        except Exception as e:
            print(colored(f"\n❌ Error: {e}", "red"))

        if len(sys.argv) > 1:
            break

if __name__ == "__main__":
    main()
