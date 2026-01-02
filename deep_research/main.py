
import sys
import time
from dotenv import load_dotenv
from termcolor import colored

# Load ENVs
load_dotenv(".env", override=True)

# Import New Orchestrator
from orchestrator import orchestrator_app

def main():
    print(colored("🚀 Starting ENSEMBLE Financial Agent (Multi-Model + Meta-Judge)", "cyan", attrs=["bold"]))
    print(colored("   🔍 Background Research: Web Search (Tavily)", "magenta"))
    print(colored("   🧠 Planner: Llama 3.1 405B (Planning + Meta-Judge)", "green"))
    print(colored("   🔄 Executors: 3-Model Ensemble (Llama 70B + Qwen 72B + Mixtral 8x22B)", "blue"))
    print(colored("   ✍️  Writer: Llama 3.1 405B (Final Synthesis)", "green"))
    
    if len(sys.argv) > 1:
        queries = [" ".join(sys.argv[1:])]
    else:
        print("\n💡 Enter a complex financial research query.")
        queries = []

    while True:
        if not queries:
            try:
                user_input = input(colored("\n💰 Query (q to exit): ", "yellow"))
                if user_input.lower() in ['q', 'exit', 'quit']: break
                if not user_input.strip(): continue
                current_query = user_input
            except KeyboardInterrupt:
                break
        else:
            current_query = queries.pop(0)

        print(colored(f"\n🔎 STARTING RESEARCH: '{current_query}'", "white", attrs=["bold"]))
        
        try:
            # Prepare Initial State
            initial_state = {
                "task": current_query,
                "companies": [],
                "background_research": "",
                "plan": [],
                "current_step_index": 0,
                "step_results": {},
                "final_report": ""
            }
            
            # Run Graph
            final_state = orchestrator_app.invoke(initial_state)
            
            print(colored("\n✅ FINAL REPORT GENERATED:", "green", attrs=["bold"]))
            print("-" * 80)
            print(final_state.get("final_report", "No report generated."))
            print("-" * 80)
            
            # Save to file
            with open("final_report.md", "w") as f:
                f.write(f"# Research Report\n\n")
                f.write(f"**Query**: {current_query}\n\n")
                f.write(f"## Background Research\n\n{final_state.get('background_research', 'N/A')}\n\n")
                f.write(f"## Final Analysis\n\n{final_state.get('final_report', '')}\n")
            print(colored(f"\n📄 Saved to 'final_report.md'", "cyan"))

        except Exception as e:
            print(colored(f"\n❌ Error during execution: {e}", "red"))
            import traceback
            traceback.print_exc()

        if len(sys.argv) > 1:
            break

if __name__ == "__main__":
    main()
