"""
Test script to verify the orchestrator workflow step by step
"""

from dotenv import load_dotenv
load_dotenv(".env", override=True)

from orchestrator import research_background_node, planner_node, executor_node, reporter_node, orchestrator_check

def test_orchestrator_manually():
    """Test the orchestrator workflow step by step"""
    
    # Initial state
    state = {
        "task": "Analyze TCS financial performance",
        "companies": [],
        "background_research": "",
        "plan": [],
        "current_step_index": 0,
        "step_results": {},
        "final_report": ""
    }
    
    print("="*80)
    print("TESTING ORCHESTRATOR WORKFLOW")
    print("="*80)
    
    # Step 1: Background Research
    print("\n[1/5] Running Background Research...")
    bg_result = research_background_node(state)
    state.update(bg_result)
    print(f"✓ Background gathered: {len(state['background_research'])} chars")
    
    # Step 2: Planning
    print("\n[2/5] Running Planner...")
    plan_result = planner_node(state)
    state.update(plan_result)
    print(f"✓ Plan generated: {len(state['plan'])} steps")
    for i, step in enumerate(state['plan']):
        print(f"   {i+1}. {step}")
    
    # Step 3: Simulate approval (skip approval_node for testing)
    print("\n[3/5] Simulating plan approval...")
    state['current_step_index'] = 0
    
    # Step 4: Execute steps
    print("\n[4/5] Executing steps...")
    while state['current_step_index'] < len(state['plan']):
        step_num = state['current_step_index'] + 1
        print(f"\n   Executing step {step_num}/{len(state['plan'])}...")
        
        try:
            exec_result = executor_node(state)
            state.update(exec_result)
            print(f"   ✓ Step {step_num} complete")
        except Exception as e:
            print(f"   ✗ Step {step_num} failed: {e}")
            break
    
    print(f"\n✓ Execution complete. Step results: {len(state['step_results'])} items")
    
    # Step 5: Reporter
    print("\n[5/5] Running Reporter...")
    try:
        report_result = reporter_node(state)
        state.update(report_result)
        print(f"✓ Report generated: {len(state['final_report'])} chars")
        
        # Display report
        print("\n" + "="*80)
        print("FINAL REPORT")
        print("="*80)
        print(state['final_report'][:500])
        print("...")
        
    except Exception as e:
        print(f"✗ Reporter failed: {e}")
        import traceback
        traceback.print_exc()
    
    return state

if __name__ == "__main__":
    final_state = test_orchestrator_manually()
    
    # Save to file
    if final_state.get('final_report'):
        with open('test_report.md', 'w') as f:
            f.write(final_state['final_report'])
        print("\n✓ Report saved to test_report.md")
