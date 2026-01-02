#!/bin/bash
# Quick verification script for Gemini CLI tool in Gradio

echo "🔍 Checking Gradio App Status..."
echo "================================"

# Check if Gradio is running
if lsof -ti:7860 > /dev/null 2>&1; then
    echo "✅ Gradio app is running on port 7860"
    PID=$(lsof -ti:7860)
    echo "   Process ID: $PID"
else
    echo "❌ Gradio app is NOT running"
    exit 1
fi

# Check if tool file exists
if [ -f "research_agent/gemini_cli_tool.py" ]; then
    echo "✅ Tool file exists: research_agent/gemini_cli_tool.py"
else
    echo "❌ Tool file missing"
    exit 1
fi

# Check if __init__.py has the import
if grep -q "ask_gemini_cli_tool" research_agent/__init__.py; then
    echo "✅ Tool is exported in research_agent/__init__.py"
else
    echo "❌ Tool NOT exported in __init__.py"
    exit 1
fi

# Check if agent.py has the tool
if grep -q "ask_gemini_cli_tool" agent.py; then
    echo "✅ Tool is added to agent.py toolkit"
else
    echo "❌ Tool NOT in agent.py toolkit"
    exit 1
fi

echo ""
echo "📋 Summary:"
echo "================================"
echo "The Gemini CLI tool code is properly integrated."
echo ""
echo "⚠️  IMPORTANT: The running Gradio app (PID: $PID) was started"
echo "   BEFORE the tool was added. It needs to be restarted to"
echo "   pick up the new tool."
echo ""
echo "To restart Gradio app:"
echo "  1. Kill current process: kill $PID"
echo "  2. Start new instance: python3 gradio_app.py"
echo ""
