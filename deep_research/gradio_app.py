
import gradio as gr
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv(".env", override=True)

# Import orchestrator nodes
from orchestrator import (
    research_background_node, 
    planner_node, 
    executor_node, 
    reporter_node
)

# ============================================================================
# CSS STYLING (Bloomberg Terminal Theme)
# ============================================================================
BLOOMBERG_CSS = """
/* Global Background - Bloomberg Black */
body, .gradio-container {
    background-color: #000000 !important;
    color: #FF8200 !important;
    font-family: 'Courier New', monospace !important;
}

/* Headers - Bloomberg Orange */
h1, h2, h3, h4, span {
    color: #FF8200 !important;
    font-family: 'Courier New', monospace !important;
    text-transform: uppercase;
    font-weight: bold;
}

/* Inputs and Text Areas */
textarea, input {
    background-color: #0A0A0A !important;
    color: #00FF00 !important;
    border: 1px solid #FF8200 !important;
    font-family: 'Courier New', monospace !important;
}

/* Buttons - Bloomberg Style */
button.primary {
    background-color: #FF8200 !important;
    color: #000000 !important;
    font-weight: bold !important;
    border: none !important;
    text-transform: uppercase !important;
    padding: 10px 20px !important;
}
button:hover {
    background-color: #FFA500 !important;
    box-shadow: 0 0 10px #FF8200 !important;
}

/* Status/Output Boxes */
.output-box {
    background-color: #0A0A0A;
    border: 1px solid #FF8200;
    padding: 15px;
    margin: 10px 0;
    color: #00FF00;
}

/* Dataframes */
table {
    border: 1px solid #FF8200 !important;
    background-color: #0A0A0A !important;
    color: #00FF00 !important;
}
"""

# ============================================================================
# APP LOGIC
# ============================================================================

def init_state():
    return {
        "task": "",
        "companies": [],
        "background_research": "",
        "plan": [],
        "current_step_index": 0,
        "step_results": {},
        "final_report": "",
        "logs": []
    }

def log_message(state, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"
    state["logs"].append(entry)
    return "\n".join(state["logs"])

def start_research_and_plan(query, state):
    """Phase 1: Background Research & Planning"""
    if not query.strip():
        yield state, "Please enter a research query.", gr.update(visible=False), gr.update(visible=False), ""
        return

    # Reset specific fields but keep logs if any
    state["task"] = query
    state["plan"] = []
    state["current_step_index"] = 0
    state["step_results"] = {}
    state["final_report"] = ""
    logs = log_message(state, f"Starting research for: {query}")
    
    yield state, "Status: Running Background Research...", gr.update(visible=False), gr.update(visible=False), logs

    # 1. Background Research
    try:
        log_message(state, "Running background research node...")
        bg_result = research_background_node(state)
        state.update(bg_result)
        logs = log_message(state, f"Background research complete. Length: {len(state['background_research'])} chars")
        yield state, "Status: Planning...", gr.update(visible=False), gr.update(visible=False), logs
    except Exception as e:
        logs = log_message(state, f"Error in background research: {str(e)}")
        yield state, f"Error: {str(e)}", gr.update(visible=False), gr.update(visible=False), logs
        return

    # 2. Planning
    try:
        log_message(state, "Running planner node...")
        item = planner_node(state)
        state.update(item)
        logs = log_message(state, f"Plan generated with {len(state['plan'])} steps.")
        
        # Format plan for display
        plan_text = "\n".join(state["plan"])
        
        yield state, "Status: Plan Generated. Waiting for Approval.", gr.update(visible=True, value=plan_text), gr.update(visible=True), logs
        
    except Exception as e:
        logs = log_message(state, f"Error in planning: {str(e)}")
        yield state, f"Error: {str(e)}", gr.update(visible=False), gr.update(visible=False), logs

def execute_research_plan(state, plan_text):
    """Phase 2: Execution & Reporting"""
    
    # Update plan from text area (in case user edited it)
    state["plan"] = [line.strip() for line in plan_text.split("\n") if line.strip()]
    logs = log_message(state, "Plan approved. Starting execution...")
    
    yield state, "Status: Executing Plan...", gr.update(visible=False), logs, ""

    total_steps = len(state["plan"])
    
    # 3. Execution Loop
    for i in range(total_steps):
        step_idx = i
        state["current_step_index"] = step_idx
        current_step = state["plan"][step_idx]
        
        logs = log_message(state, f"Executing Step {step_idx + 1}/{total_steps}: {current_step}")
        yield state, f"Status: Executing Step {step_idx + 1}/{total_steps}...", gr.update(visible=False), logs, ""
        
        try:
            # Execute step
            item = executor_node(state)
            state.update(item)
            logs = log_message(state, f"Step {step_idx + 1} complete.")
            
        except Exception as e:
            logs = log_message(state, f"Error executing step {step_idx + 1}: {str(e)}")
            yield state, f"Error in Step {step_idx + 1}: {str(e)}", gr.update(visible=False), logs, ""
            return

    # 4. Reporting
    logs = log_message(state, "All steps complete. Synthesizing final report...")
    yield state, "Status: Synthesizing Report...", gr.update(visible=False), logs, ""
    
    try:
        item = reporter_node(state)
        state.update(item)
        logs = log_message(state, "Report generated successfully.")
        
        yield state, "Status: Complete", gr.update(visible=False), logs, state["final_report"]
        
    except Exception as e:
        logs = log_message(state, f"Error generating report: {str(e)}")
        yield state, f"Error in reporting: {str(e)}", gr.update(visible=False), logs, ""


def cancel_process(state):
    state = init_state()
    return state, "Status: Canceled", gr.update(visible=False), gr.update(visible=False), "", ""

# ============================================================================
# UI LAYOUT
# ============================================================================

with gr.Blocks(theme=gr.themes.Monochrome(), css=BLOOMBERG_CSS, title="Deep Financial Analyst") as demo:
    
    state = gr.State(value=init_state())
    
    gr.Markdown("# ⚡ DEEP FINANCIAL ANALYST TERMINAL ⚡")
    gr.Markdown("POWERED BY: GRADIO | LLAMA 405B (PLANNER) | ENSEMBLE MODELS (EXECUTOR)")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📊 SYSTEM STATUS")
            gr.Markdown(f"**DATE**: {datetime.now().strftime('%Y-%m-%d')}")
            gr.Markdown("""
            **CAPABILITIES**
            [✓] PLANNER: Meta-Llama 405B
            [✓] EXECUTORS: 3-Model Ensemble
            [✓] TOOLS: Financial APIs + Web
            """)
            
        with gr.Column(scale=3):
            query_input = gr.Textbox(
                label="RESEARCH QUERY", 
                placeholder="Enter your financial research query (e.g., Analyze TCS and Infosys...)",
                lines=3
            )
            
            with gr.Row():
                execute_btn = gr.Button("⚡ EXECUTE RESEARCH", variant="primary")
                clear_btn = gr.Button("🗑️ CLEAR/CANCEL")
            
            status_text = gr.Markdown("Status: Ready")
            
            # Plan Approval Section
            with gr.Group(visible=False) as plan_group:
                gr.Markdown("### 📋 RESEARCH PLAN (Edit if needed)")
                plan_editor = gr.TextArea(label="Proposed Plan", lines=10, interactive=True)
                approve_btn = gr.Button("✅ APPROVE & EXECUTE", variant="primary")
            
            # Logs & Output
            logs_box = gr.Textbox(label="SYSTEM LOGS", lines=10, interactive=False, visible=True)
            
            # Final Report
            report_box = gr.Markdown(label="FINAL REPORT", visible=True)

    # Event Handlers
    
    # 1. Generate Plan
    execute_btn.click(
        fn=start_research_and_plan,
        inputs=[query_input, state],
        outputs=[state, status_text, plan_editor, plan_group, logs_box]
    )
    
    # 2. Approve & Execute
    approve_btn.click(
        fn=execute_research_plan,
        inputs=[state, plan_editor],
        outputs=[state, status_text, plan_group, logs_box, report_box]
    )
    
    # 3. Clear/Cancel
    clear_btn.click(
        fn=cancel_process,
        inputs=[state],
        outputs=[state, status_text, plan_editor, plan_group, logs_box, report_box]
    )

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, share=False)
