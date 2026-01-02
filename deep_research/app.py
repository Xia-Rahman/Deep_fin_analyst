
import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import time
from termcolor import cprint

# Load environment
load_dotenv(".env", override=True)

# Import orchestrator
from orchestrator import orchestrator_app

# ============================================================================
# BLOOMBERG TERMINAL AESTHETIC - CSS STYLING
# ============================================================================

def apply_bloomberg_theme():
    """Apply Bloomberg Terminal inspired dark theme with orange accents."""
    st.markdown("""
    <style>
    /* Global Background - Bloomberg Black */
    .stApp {
        background-color: #000000;
        color: #FF8200;
        font-family: 'Courier New', monospace;
    }
    
    /* Main Content Area */
    .main {
        background-color: #000000;
    }
    
    /* Headers - Bloomberg Orange */
    h1, h2, h3 {
        color: #FF8200 !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 2px solid #FF8200;
        padding-bottom: 10px;
    }
    
    /* Text Areas and Inputs - Terminal Style */
    .stTextInput input, .stTextArea textarea {
        background-color: #0A0A0A !important;
        color: #00FF00 !important;
        border: 1px solid #FF8200 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 14px !important;
    }
    
    /* Buttons - Bloomberg Style */
    .stButton button {
        background-color: #FF8200 !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-family: 'Courier New', monospace !important;
        border: none !important;
        padding: 10px 20px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s !important;
    }
    
    .stButton button:hover {
        background-color: #FFA500 !important;
        box-shadow: 0 0 10px #FF8200 !important;
    }
    
    /* Status Boxes */
    .status-box {
        background-color: #0A0A0A;
        border: 1px solid #FF8200;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
    }
    
    /* Info Boxes - Green Terminal Text */
    .info-text {
        color: #00FF00;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.6;
    }
    
    /* Warning/Error Text - Red */
    .error-text {
        color: #FF0000;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    
    /* Sidebar - Dark */
    [data-testid="stSidebar"] {
        background-color: #0A0A0A !important;
        border-right: 2px solid #FF8200 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #FF8200 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #0A0A0A !important;
        color: #FF8200 !important;
        border: 1px solid #FF8200 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* Code blocks */
    code {
        background-color: #0A0A0A !important;
        color: #00FF00 !important;
        border: 1px solid #FF8200 !important;
        padding: 2px 5px !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #CCCCCC !important;
    }
    
    /* Divider */
    hr {
        border-color: #FF8200 !important;
    }
    
    /* Metric boxes */
    [data-testid="stMetricValue"] {
        color: #00FF00 !important;
        font-family: 'Courier New', monospace !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #FF8200 !important;
        font-family: 'Courier New', monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    cprint("\n[DEBUG] Initializing session state...", "cyan")
    if 'research_plan' not in st.session_state:
        st.session_state.research_plan = []
        cprint("[DEBUG] - research_plan initialized", "cyan")
    if 'plan_approved' not in st.session_state:
        st.session_state.plan_approved = False
        cprint("[DEBUG] - plan_approved initialized", "cyan")
    if 'research_in_progress' not in st.session_state:
        st.session_state.research_in_progress = False
        cprint("[DEBUG] - research_in_progress initialized", "cyan")
    if 'final_report' not in st.session_state:
        st.session_state.final_report = ""
        cprint("[DEBUG] - final_report initialized", "cyan")
    if 'background_research' not in st.session_state:
        st.session_state.background_research = ""
        cprint("[DEBUG] - background_research initialized", "cyan")
    if 'step_results' not in st.session_state:
        st.session_state.step_results = {}
        cprint("[DEBUG] - step_results initialized", "cyan")
    # New: execution state tracking
    if 'executing_plan' not in st.session_state:
        st.session_state.executing_plan = False
        cprint("[DEBUG] - executing_plan initialized", "cyan")
    if 'execution_step' not in st.session_state:
        st.session_state.execution_step = 0
        cprint("[DEBUG] - execution_step initialized", "cyan")
    if 'execution_state' not in st.session_state:
        st.session_state.execution_state = {}
        cprint("[DEBUG] - execution_state initialized", "cyan")
    cprint(f"[DEBUG] Session state keys: {list(st.session_state.keys())}", "cyan")

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Apply theme
    apply_bloomberg_theme()
    
    # Initialize state
    init_session_state()
    
    # Terminal-style header
    st.markdown("""
    <div style='text-align: center; padding: 20px; border: 2px solid #FF8200; margin-bottom: 30px;'>
    <h1>⚡ DEEP FINANCIAL ANALYST TERMINAL ⚡</h1>
    <p style='color: #00FF00; font-family: Courier New; font-size: 12px;'>
    POWERED BY: LLAMA 405B (PLANNER) | ENSEMBLE MODELS (EXECUTOR) | PROGRESSIVE SKILL DISCLOSURE
    </p>
    <p style='color: #CCCCCC; font-family: Courier New; font-size: 11px;'>
    [SYSTEM READY] | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST
    </p>
    </div>
    """.replace("{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 
    unsafe_allow_html=True)
    
    # Sidebar - System Info
    with st.sidebar:
        st.markdown("### 📊 SYSTEM STATUS")
        st.markdown(f"**TIME**: {datetime.now().strftime('%H:%M:%S')}")
        st.markdown(f"**DATE**: {datetime.now().strftime('%Y-%m-%d')}")
        st.divider()
        
        st.markdown("### 🛠️ CAPABILITIES")
        st.markdown("""
        ```
        [✓] PLANNER: Meta-Llama 405B
        [✓] EXECUTORS: 3-Model Ensemble
        [✓] SKILLS: 12 Professional Skills
        [✓] INDIA: SEBI/NSE/BSE Integration
        [✓] SECTORS: IT Services, Pharma
        [✓] TOOLS: Financial APIs + Web
        ```
        """)
        
        st.divider()
        st.markdown("### 📚 AVAILABLE SKILLS")
        with st.expander("GLOBAL SKILLS"):
            st.markdown("""
            - SEC Filing Intelligence
            - Competitive Positioning
            - Capital Allocation
            - Ratio Diagnostics
            - Valuation Modeling
            - Peer Group Construction
            - ESG Integration
            """)
        
        with st.expander("INDIA SKILLS"):
            st.markdown("""
            - SEBI Regulatory Intelligence
            - Promoter Holdings Analysis
            - Related Party Transactions
            - IT Sector Analysis
            - Pharma Sector Analysis
            """)
    
    # Main Input Area
    st.markdown("### 🔍 RESEARCH QUERY")
    query = st.text_area(
        "Enter your financial research query:",
        height=100,
        placeholder="Example: Analyze the profit margins and growth of TCS and Infosys over the last 5 years",
        help="Enter any financial research query. The system will analyze complexity and create a deep research plan."
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        execute_btn = st.button("⚡ EXECUTE RESEARCH", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑️ CLEAR", use_container_width=True)
    with col3:
        st.markdown(f"<p style='color: #00FF00; font-size: 11px;'>STATUS: {'READY' if not st.session_state.research_in_progress else 'PROCESSING...'}</p>", unsafe_allow_html=True)
    
    if clear_btn:
        cprint("\n[DEBUG] CLEAR button pressed - resetting all state", "yellow")
        st.session_state.research_plan = []
        st.session_state.plan_approved = False
        st.session_state.final_report = ""
        st.session_state.background_research = ""
        st.session_state.step_results = {}
        st.session_state.executing_plan = False
        st.session_state.execution_step = 0
        st.session_state.execution_state = {}
        st.session_state.research_in_progress = False
        cprint("[DEBUG] All state cleared, rerunning app", "yellow")
        st.rerun()
    
    # Execute Research
    if execute_btn and query.strip():
        cprint(f"\n[DEBUG] EXECUTE button pressed with query: {query[:100]}...", "green")
        st.session_state.research_in_progress = True
        cprint("[DEBUG] Research status set to IN PROGRESS", "green")
        
        # Status display
        st.markdown("---")
        st.markdown("### 📡 RESEARCH STATUS")
        
        status_container = st.container()
        
        with status_container:
            # Phase 1: Background Research
            st.markdown("<p class='info-text'>🔍 PHASE 1: Background Research...</p>", unsafe_allow_html=True)
            progress_bar = st.progress(0)
            
            try:
                # Create initial state
                cprint("\n[DEBUG] Creating initial orchestrator state", "magenta")
                initial_state = {
                    "task": query,
                    "companies": [],
                    "background_research": "",
                    "plan": [],
                    "current_step_index": 0,
                    "step_results": {},
                    "final_report": ""
                }
                cprint(f"[DEBUG] Initial state: {initial_state}", "magenta")
                
                # Import node functions
                from orchestrator import research_background_node, planner_node
                
                # Run background research
                progress_bar.progress(20)
                state = initial_state.copy()
                cprint("\n[DEBUG] Calling research_background_node...", "blue")
                bg_result = research_background_node(state)
                cprint(f"[DEBUG] Background research returned keys: {bg_result.keys()}", "blue")
                state.update(bg_result)
                st.session_state.background_research = state.get("background_research", "")
                cprint(f"[DEBUG] Background research length: {len(st.session_state.background_research)} chars", "blue")
                
                st.markdown("<p class='info-text'>✓ Background research complete</p>", unsafe_allow_html=True)
                
                # Phase 2: Planning
                st.markdown("<p class='info-text'>🧠 PHASE 2: Planning...</p>", unsafe_allow_html=True)
                progress_bar.progress(40)
                
                cprint("\n[DEBUG] Calling planner_node...", "blue")
                plan_result = planner_node(state)
                cprint(f"[DEBUG] Planner returned keys: {plan_result.keys()}", "blue")
                state.update(plan_result)
                st.session_state.research_plan = state.get("plan", [])
                cprint(f"[DEBUG] Plan has {len(st.session_state.research_plan)} steps:", "blue")
                for i, step in enumerate(st.session_state.research_plan):
                    cprint(f"[DEBUG]   Step {i+1}: {step}", "blue")
                
                progress_bar.progress(60)
                st.markdown("<p class='info-text'>✓ Plan generated</p>", unsafe_allow_html=True)
                
                # Display background research if available
                if st.session_state.background_research:
                    with st.expander("📄 View Background Research"):
                        st.markdown(st.session_state.background_research)
                
                # Display Plan
                st.markdown("---")
                st.markdown("### 📋 RESEARCH PLAN")
                st.markdown("<div class='status-box'>", unsafe_allow_html=True)
                
                for i, step in enumerate(st.session_state.research_plan):
                    st.markdown(f"<p class='info-text'>{i+1}. {step}</p>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Approval Interface
                st.markdown("### ⚙️ PLAN APPROVAL REQUIRED")
                st.markdown("<p class='info-text'>Choose an action below:</p>", unsafe_allow_html=True)
                
                col_a, col_b, col_c = st.columns([1, 1, 1])
                
                with col_a:
                    if st.button("✅ APPROVE & EXECUTE", use_container_width=True, key="approve_execute"):
                        # Start execution mode
                        cprint("\n[DEBUG] APPROVE & EXECUTE button pressed!", "green")
                        cprint(f"[DEBUG] About to execute {len(st.session_state.research_plan)} steps", "green")
                        
                        # Initialize execution state
                        st.session_state.executing_plan = True
                        st.session_state.execution_step = 0
                        st.session_state.execution_state = {
                            "task": query,
                            "companies": state.get("companies", []),
                            "background_research": st.session_state.background_research,
                            "plan": st.session_state.research_plan,
                            "current_step_index": 0,
                            "step_results": {},
                            "final_report": ""
                        }
                        cprint("[DEBUG] Execution mode activated, triggering rerun", "green")
                        st.rerun()
                
                with col_b:
                    if st.button("📝 EDIT PLAN", use_container_width=True, key="edit_plan"):
                        cprint("\n[DEBUG] EDIT PLAN button pressed", "yellow")
                        st.session_state.edit_mode = True
                        st.rerun()
                
                with col_c:
                    if st.button("❌ CANCEL", use_container_width=True, key="cancel_research"):
                        cprint("\n[DEBUG] CANCEL button pressed", "red")
                        st.session_state.research_plan = []
                        st.session_state.research_in_progress = False
                        st.session_state.executing_plan = False
                        st.session_state.execution_step = 0
                        st.session_state.execution_state = {}
                        st.warning("Research canceled")
                        st.rerun()
                
                # Edit mode
                if hasattr(st.session_state, 'edit_mode') and st.session_state.edit_mode:
                    st.markdown("---")
                    st.markdown("### 📝 EDIT RESEARCH PLAN")
                    
                    edited_plan_text = st.text_area(
                        "Edit plan (one step per line):",
                        value="\n".join(st.session_state.research_plan),
                        height=300,
                        key="plan_editor"
                    )
                    
                    col_save, col_cancel_edit = st.columns([1, 1])
                    
                    with col_save:
                        if st.button("💾 SAVE EDITS", use_container_width=True):
                            st.session_state.research_plan = [
                                s.strip() for s in edited_plan_text.split("\n") if s.strip()
                            ]
                            st.session_state.edit_mode = False
                            st.success("Plan updated!")
                            st.rerun()
                    
                    with col_cancel_edit:
                        if st.button("⏪ CANCEL EDIT", use_container_width=True):
                            st.session_state.edit_mode = False
                            st.rerun()
                
            except Exception as e:
                cprint(f"\n[ERROR] Main research flow failed: {str(e)}", "red")
                cprint(f"[ERROR] Exception type: {type(e).__name__}", "red")
                import traceback
                cprint(f"[ERROR] Traceback:\n{traceback.format_exc()}", "red")
                st.error(f"❌ Error: {str(e)}")
                st.exception(e)
                st.session_state.research_in_progress = False
                progress_bar.progress(0)
    
    # ============================================================================
    # PROGRESSIVE EXECUTION - Runs automatically when in execution mode
    # ============================================================================
    if st.session_state.executing_plan:
        cprint(f"\n[DEBUG] Progressive execution active - Step {st.session_state.execution_step}", "cyan")
        
        total_steps = len(st.session_state.research_plan)
        exec_state = st.session_state.execution_state
        
        # Display execution status
        st.markdown("---")
        st.markdown("### 🚀 EXECUTING RESEARCH PLAN")
        
        progress_container = st.container()
        with progress_container:
            # Show progress
            current_step = st.session_state.execution_step
            progress_pct = int((current_step / (total_steps + 1)) * 100)  # +1 for report generation
            st.progress(progress_pct)
            
            if current_step < total_steps:
                # Execute current step
                step_num = current_step + 1
                st.markdown(f"<p class='info-text'>⚙️ Executing step {step_num}/{total_steps}: {st.session_state.research_plan[current_step][:80]}...</p>", unsafe_allow_html=True)
                
                try:
                    from orchestrator import executor_node
                    
                    cprint(f"\n[DEBUG] === EXECUTING STEP {step_num}/{total_steps} ===", "yellow")
                    cprint(f"[DEBUG] Step description: {exec_state['plan'][current_step]}", "yellow")
                    cprint(f"[DEBUG] Current state keys: {exec_state.keys()}", "yellow")
                    
                    # Execute the step
                    exec_result = executor_node(exec_state)
                    cprint(f"[DEBUG] Executor returned keys: {exec_result.keys()}", "yellow")
                    
                    # Update state
                    exec_state.update(exec_result)
                    st.session_state.execution_state = exec_state
                    
                    # Move to next step
                    st.session_state.execution_step += 1
                    cprint(f"[DEBUG] Step {step_num} complete. Moving to step {st.session_state.execution_step + 1}", "yellow")
                    
                    # Trigger next step
                    time.sleep(0.5)  # Brief pause for UI update
                    st.rerun()
                    
                except Exception as step_error:
                    cprint(f"\n[ERROR] Step {step_num} failed: {str(step_error)}", "red")
                    import traceback
                    cprint(f"[ERROR] Traceback:\n{traceback.format_exc()}", "red")
                    st.error(f"❌ Step {step_num} failed: {str(step_error)}")
                    st.exception(step_error)
                    
                    # Stop execution
                    st.session_state.executing_plan = False
                    st.session_state.research_in_progress = False
                    
            elif current_step == total_steps:
                # All steps done, generate final report
                st.markdown("<p class='info-text'>📝 Synthesizing final report...</p>", unsafe_allow_html=True)
                
                try:
                    from orchestrator import reporter_node
                    
                    cprint("\n[DEBUG] All steps executed, synthesizing final report...", "magenta")
                    report_result = reporter_node(exec_state)
                    cprint(f"[DEBUG] Reporter returned keys: {report_result.keys()}", "magenta")
                    
                    # Save results
                    exec_state.update(report_result)
                    st.session_state.final_report = exec_state.get("final_report", "")
                    st.session_state.step_results = exec_state.get("step_results", {})
                    
                    cprint(f"[DEBUG] Final report length: {len(st.session_state.final_report)} chars", "magenta")
                    cprint(f"[DEBUG] Step results count: {len(st.session_state.step_results)}", "magenta")
                    
                    # Complete execution
                    st.session_state.executing_plan = False
                    st.session_state.research_in_progress = False
                    st.session_state.execution_step += 1
                    
                    st.success("✅ Research complete!")
                    cprint("\n[DEBUG] === RESEARCH COMPLETE ===", "green")
                    
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as report_error:
                    cprint(f"\n[ERROR] Report generation failed: {str(report_error)}", "red")
                    import traceback
                    cprint(f"[ERROR] Traceback:\n{traceback.format_exc()}", "red")
                    st.error(f"❌ Report generation failed: {str(report_error)}")
                    st.exception(report_error)
                    
                    # Stop execution
                    st.session_state.executing_plan = False
                    st.session_state.research_in_progress = False
    
    
    # Display Final Report
    if st.session_state.final_report:
        st.markdown("---")
        st.markdown("### 📊 FINAL RESEARCH REPORT")
        
        # Show completion status
        st.markdown("<p class='info-text'>✅ Research completed successfully</p>", unsafe_allow_html=True)
        
        # Main report
        st.markdown("<div class='status-box'>", unsafe_allow_html=True)
        st.markdown(st.session_state.final_report)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Show step results in expandable section
        if st.session_state.step_results:
            with st.expander("🔍 View Research Step Details"):
                st.markdown("### Step-by-Step Research Findings")
                for step_name, result in st.session_state.step_results.items():
                    st.markdown(f"**{step_name}**")
                    st.markdown(f"```\n{result[:500]}...\n```")
                    st.markdown("---")
        
        # Download buttons
        col_dl1, col_dl2 = st.columns([1, 1])
        
        with col_dl1:
            st.download_button(
                label="💾 DOWNLOAD REPORT (MD)",
                data=st.session_state.final_report,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col_dl2:
            # Create full research package
            full_package = f"""# Deep Financial Research Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Background Research
{st.session_state.background_research}

## Research Plan
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(st.session_state.research_plan)])}

## Final Report
{st.session_state.final_report}

## Detailed Step Results
"""
            for step_name, result in st.session_state.step_results.items():
                full_package += f"\n### {step_name}\n{result}\n\n"
            
            st.download_button(
                label="📦 DOWNLOAD FULL PACKAGE",
                data=full_package,
                file_name=f"research_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )

    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 10px; color: #666666; font-size: 10px;'>
    DEEP FINANCIAL ANALYST TERMINAL v1.0 | POWERED BY LANGCHAIN + LANGGRAPH | © 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
