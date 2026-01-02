# Debug Enhancements & Query Analysis Feature

## Overview
This document describes the debug logging system and the new query analysis feature added to the Deep Financial Analyst application.

## 1. Comprehensive Debug Logging

### Files Enhanced:
- **`app.py`**: Streamlit UI with full workflow tracking
- **`orchestrator.py`**: Research orchestrator with node-level visibility

### Debug Features Added:

#### In `app.py`:
```python
- Session state initialization tracking
- Button click detection (EXECUTE, CLEAR, APPROVE, EDIT, CANCEL)
- Phase progression (Background → Planning → Execution → Reporting)
- Data flow monitoring (lengths, step counts, results)
- Error handling with full tracebacks
```

#### In `orchestrator.py`:
```python
- Node entry/exit markers for all nodes:
  * research_background_node
  * planner_node
  * executor_node
  * reporter_node
- State inspection at each node
- Tool execution tracking
- API call logging (OpenRouter, Tavily)
- Step progression monitoring
```

### Color-Coded Output:
- 🔵 **Blue**: Planner node activities
- 🟣 **Magenta**: Executor node activities
- 🟢 **Green**: Reporter node activities
- 🟡 **Yellow**: Warnings and fallbacks
- 🔴 **Red**: Errors and exceptions
- 🔷 **Cyan**: Background research activities

## 2. Query Analysis & Core Entity Research

### New Feature: Intelligent Query Pre-Processing

Before diving into detailed research, the system now:

1. **Analyzes the Query** using Llama 405B to extract:
   - Core entity or topic
   - Key focus areas
   - Suggested generic search query

2. **Performs Broad Search** on the core entity first
   - Provides foundational context
   - Helps the planner understand the domain
   - Improves subsequent targeted searches

### Implementation:

```python
# STEP 0 in research_background_node():
1. LLM-based query analysis
   └─> Extracts: core_entity, focus_areas, generic_search

2. Generic web search on core entity
   └─> Gathers: 1000 chars of foundational context

3. Proceeds with targeted searches
   └─> Company-specific, sector, regulatory, etc.
```

### Example Flow:

**Query**: "Compare TCS and Infosys profit margins and growth"

**Step 0 Output**:
```
🎯 STEP 0: Query Analysis & Core Entity Research
  ✓ Core Entity: TCS and Infosys
  ✓ Focus Areas: profit margins, revenue growth, comparison
  [0] Generic Search: TCS Infosys comparison Indian IT sector...
```

**Then continues with**:
- Company-specific searches (TCS, Infosys)
- Sector analysis (Indian IT)
- Market context (India NSE/BSE)
- Regulatory intelligence

## 3. Testing Instructions

### Running the App:
```bash
cd /Users/xiya/deep_fin_analyst/Deep_fin_analyst/deep_research
streamlit run app.py
```

### Monitoring Debug Output:
The terminal will display color-coded debug information showing:
- Every node transition
- API calls and responses
- Tool executions
- State changes
- Errors with full context

### Test Queries:
1. **Company Comparison**: "Compare TCS and Infosys profit margins and growth"
2. **Sector Analysis**: "Analyze the Indian pharma sector"
3. **Single Company**: "Evaluate Reliance Industries capital allocation"
4. **Market Context**: "India banking sector NPA trends"

## 4. Benefits

### For Debugging:
- ✅ Complete visibility into workflow execution
- ✅ Easy identification of bottlenecks
- ✅ Clear error context with tracebacks
- ✅ State inspection at each step

### For Research Quality:
- ✅ Better initial context from generic search
- ✅ More targeted subsequent queries
- ✅ Reduced irrelevant information
- ✅ Improved planner decision-making

## 5. Configuration

### Model Used for Analysis:
- **Query Analysis**: PLANNER_MODEL_ID (Llama 405B)
- **Generic Search**: Tavily Search API

### Customization:
Edit the analysis prompt in `orchestrator.py` at line ~154 to adjust:
- Analysis depth
- JSON structure
- Focus area extraction logic

## 6. Troubleshooting

### If Core Entity Analysis Fails:
- System falls back to using the original query
- Performs basic search instead
- Continues with normal workflow

### If Generic Search Fails:
- Error is logged but not fatal
- System proceeds with targeted searches
- Background results may be less comprehensive

## 7. Next Steps

Potential enhancements:
1. **Caching**: Store core entity analysis to avoid re-analysis
2. **Streaming**: Show analysis results in real-time in UI
3. **Refinement**: Allow user to edit core entity before search
4. **History**: Track which entities have been researched
