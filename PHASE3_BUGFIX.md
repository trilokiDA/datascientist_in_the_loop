# Phase 3 Bug Fix: LangChain Prompt Template Error

## Issue
When running Phase 3 UI (`streamlit run src/ui/app_v3.py`), the application crashed with a KeyError from LangChain's ChatPromptTemplate:

```
KeyError: 'Input to ChatPromptTemplate is missing variables {\'\\n    "reasoning"\'}.  Expected: [\'\\n    "reasoning"\'] Received: []
```

## Root Cause
In the Phase 3 agent files (`viz_agent.py`, `stat_agent.py`, `feature_agent.py`), the system prompt contained JSON examples with unescaped curly braces:

```python
system_message = """You must respond in JSON format with these fields:
{
    "reasoning": "...",
    "impact": "...",
    ...
}
"""
```

LangChain's `ChatPromptTemplate` interprets `{...}` as template variables. Since these weren't actual variables, it threw an error.

## Solution
Escaped all curly braces in JSON examples by doubling them (`{{` and `}}`):

```python
system_message = """You must respond in JSON format with these fields:
{{
    "reasoning": "...",
    "impact": "...",
    ...
}}
"""
```

## Files Fixed
1. ✅ `src/agents/viz_agent.py` - Line 400-405
2. ✅ `src/agents/stat_agent.py` - Line 450-455
3. ✅ `src/agents/feature_agent.py` - Line 427-432

## Files Already Correct (Phase 2)
- ✅ `src/agents/quality_agent.py` - Already had escaped braces
- ✅ `src/agents/transform_agent.py` - Already had escaped braces
- ✅ `src/agents/profile_agent.py` - Already had escaped braces

## Verification
All Phase 3 agents now import and instantiate successfully:
```bash
python -c "from src.agents.viz_agent import VisualizationAgent; agent = VisualizationAgent(); print('Success')"
```

## Next Steps
You can now run the Phase 3 UI without errors:
```bash
streamlit run src/ui/app_v3.py
```

The "Run Complete Analysis" button should work properly with all three Phase 3 agents (Visualization, Statistical, and Feature Engineering).
