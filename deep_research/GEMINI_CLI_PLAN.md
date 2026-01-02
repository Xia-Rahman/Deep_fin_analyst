# Implementation Plan - Gemini CLI Integration

## User Objective
Install and integrate the **Gemini CLI** to be used for planning, reflection, and inference within the LangChain agent, replacing direct API calls.

## Constraints & System State
- **OS**: macOS
- **System Tools**: `npm` and `node` are currently NOT found in PATH. `brew` status to be verified.
- **Requirement**: Use `subprocess` to call the CLI (Standard LangChain Tool pattern).

## Proposed Solution
Since the official `@google/gemini-cli` is a Node.js package and Node is missing, we will pursue a two-tier strategy:

### Strategy A: Official Installation (Preferred)
1. Check for Homebrew (`brew`) availability.
2. If available, install `node` -> `npm` -> `@google/gemini-cli`.
3. Authenticate and verify.

### Strategy B: Python-Based Bridge (Fallback)
If Strategy A fails (no permission/tools), we will perfect the "Bridge CLI" (`gemini_cli.py`) which acts exactly like the official CLI but uses the pre-installed Python environment.
1. Fix model configuration in `gemini_cli.py` to resolve 404 errors.
2. Ensure it is executable as `gemini`.
3. Verify it accepts `-p` flags and arguments just like the official tool.

## Implementation Steps

1. **System Tools Verification**
   - Check `brew --version`.
   - Attempt Node installation if possible.

2. **CLI Installation / Configuration**
   - **Scenario A (Node Available):** Run `npm install -g @google/gemini-cli`.
   - **Scenario B (Python Bridge):** 
     - Update `gemini_cli.py` to handle arguments robustly.
     - Fix `genai.Client` model targeting (likely `gemini-1.5-flash` or `gemini-pro`).
     - Create shell alias/script for global access.

3. **LangChain Tool Integration**
   - Modify `research_agent/clients.py` to implement the `ask_gemini_cli` tool using `subprocess`.
   - Ensure it captures `stdout`/`stderr` correctly.

4. **Orchestrator Update**
   - Redirect `planner_node`, `executor_node` (tool selection), and `reporter_node` to use `ask_gemini_cli`.

5. **Validation**
   - Run a test query: `gemini -p "Hello world"`.
   - Verify agent flow executes via CLI calls.

## Verification
- Successful execution of `./gemini -p "test"`
- Streamlit/Gradio app successfully generating plans via CLI.
- No "command not found" errors during agent execution.
