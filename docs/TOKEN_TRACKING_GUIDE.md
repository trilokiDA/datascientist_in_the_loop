# Token Tracking & Cost Display Guide

## Overview
This implementation adds real-time token usage and cost tracking to the EDA Pipeline application, displaying metrics in the left sidebar.

## Implementation Summary

### Components Created

#### 1. **Token Tracker Service** (`src/utils/token_tracker.py`)
- Singleton service that tracks all LLM API calls
- Captures input tokens, output tokens, and calculates costs
- Provides session-wide accumulation and per-agent breakdown
- Uses Streamlit session state for persistence

**Key Features:**
- Automatic cost calculation for Llama 3.3 70B model
- Per-agent usage breakdown
- Request history tracking
- Formatting utilities for tokens and costs

#### 2. **Base Agent Integration** (`src/agents/base_agent.py`)
- Added `track_chain_response()` method to BaseAgent
- Automatically extracts token usage from LangChain response metadata
- All agents inherit this functionality

**Modified Agents:**
- ProfileAgent
- QualityAgent
- TransformAgent
- VisualizationAgent
- FeatureAgent
- StatAgent
- TimeSeriesAgent

#### 3. **UI Component** (`src/ui/components/token_metrics.py`)
- **Option B: Expandable Detailed View**
- Compact summary showing total cost
- Expandable section with:
  - Input/Output/Total token counts
  - Per-agent breakdown with progress bars
  - Cost breakdown by agent
  - Reset button
  - Request count

#### 4. **Sidebar Integration** (`src/ui/app.py`)
- Token metrics displayed at bottom of sidebar
- Updates automatically after each agent run
- Persists throughout the session

---

## How It Works

### Token Tracking Flow

```
1. User uploads dataset and runs agent
2. Agent creates LLM chain (prompt | self.llm)
3. Chain.invoke() returns response with metadata
4. Agent calls self.track_chain_response(response)
5. TokenTracker extracts usage from response metadata:
   - prompt_tokens (input)
   - completion_tokens (output)
6. TokenTracker updates session state:
   - Cumulative totals
   - Per-agent breakdown
   - Request history
7. UI component reads from session state and displays
```

### Token Usage Extraction

```python
# From LangChain/Groq response metadata
response.response_metadata['token_usage'] = {
    'prompt_tokens': 1234,      # Input tokens
    'completion_tokens': 567,   # Output tokens
    'total_tokens': 1801
}
```

### Cost Calculation

**Llama 3.3 70B Pricing (Groq):**
- Input: $0.59 per 1M tokens
- Output: $0.79 per 1M tokens

**Formula:**
```python
input_cost = (input_tokens * 0.59) / 1_000_000
output_cost = (output_tokens * 0.79) / 1_000_000
total_cost = input_cost + output_cost
```

---

## Usage

### Running the Application

```bash
# Navigate to project directory
cd /path/to/test

# Run Streamlit app
streamlit run src/ui/app.py
```

### Viewing Token Metrics

1. Upload a dataset in the sidebar
2. Run any agent or workflow
3. Scroll to the bottom of the sidebar
4. See the compact cost card: **💰 $0.0045**
5. Click **"📊 View Token Details"** to expand:
   - Input/Output/Total tokens
   - Per-agent breakdown
   - Cost breakdown
   - Reset option

### Resetting Token Tracking

Click the **"🔄 Reset Token Tracking"** button in the expanded view to clear all tracked usage.

---

## Session State Structure

```python
st.session_state.token_usage = {
    'input_tokens': 12345,           # Total input tokens
    'output_tokens': 8901,           # Total output tokens
    'total_tokens': 21246,           # Sum of input + output
    'total_cost': 0.0125,            # Total cost in USD
    'requests': [                    # History of all requests
        {
            'timestamp': '2026-07-30T14:30:00',
            'agent': 'ProfileAgent',
            'model': 'llama-3.3-70b-versatile',
            'input_tokens': 1234,
            'output_tokens': 567,
            'total_tokens': 1801,
            'cost': 0.0012,
            'metadata': {'temperature': 0.1}
        },
        ...
    ],
    'agent_breakdown': {             # Per-agent statistics
        'ProfileAgent': {
            'input_tokens': 1234,
            'output_tokens': 567,
            'total_tokens': 1801,
            'cost': 0.0012,
            'calls': 1
        },
        ...
    }
}
```

---

## Testing

Run the test script to verify the implementation:

```bash
python test_token_tracking.py
```

**Expected Output:**
```
Testing Token Tracking Implementation...
==================================================
✅ TokenTracker imported successfully
✅ Token metrics components imported successfully
✅ BaseAgent imported successfully
✅ TokenTracker has all required methods
✅ TokenTracker initialized successfully
✅ Token tracking works
✅ Token usage tracked correctly: 1500 tokens, $0.001590
✅ Token formatting works: 1,000
✅ Cost formatting works: $0.0016
✅ Agent breakdown works: TestAgent with 1 call(s)
✅ Token tracking reset works
==================================================
🎉 All tests passed! Token tracking is ready to use.
```

---

## UI Screenshots (Conceptual)

### Sidebar - Compact View
```
┌─────────────────────────────┐
│  💰 $0.0125                 │
│  Session Cost               │
└─────────────────────────────┘
     [📊 View Token Details ▼]
```

### Sidebar - Expanded View
```
┌─────────────────────────────┐
│  💰 $0.0125                 │
│  Session Cost               │
└─────────────────────────────┘

📊 View Token Details ▲

### 📈 Overall Usage
┌───────────┬───────────┬──────────┐
│ 📥 Input  │ 📤 Output │ 🔢 Total │
│   12,345  │    8,901  │  21,246  │
└───────────┴───────────┴──────────┘

### 🤖 Agent Breakdown

ProfileAgent
████████░░░░░░ 45.2%
12,345 tokens          $0.0056
3 calls

QualityAgent
██████░░░░░░░░ 32.8%
8,901 tokens           $0.0041
2 calls

### 💸 Cost Breakdown
ProfileAgent          $0.0056
QualityAgent          $0.0041

[🔄 Reset Token Tracking]  📊 8 total API calls
```

---

## Code Examples

### Adding Token Tracking to a New Agent

If you create a new agent, the tracking is already inherited from `BaseAgent`. Just ensure you call `self.track_chain_response()` after invoking the LLM:

```python
class MyNewAgent(BaseAgent):
    def analyze(self, dataset_handle, context=None):
        # Create prompt
        prompt = self.create_structured_prompt(system_message, user_message)
        chain = prompt | self.llm
        
        # Invoke LLM
        response = chain.invoke({})
        
        # Track token usage (IMPORTANT!)
        self.track_chain_response(response)
        
        # Parse and return results
        ...
```

### Manual Token Tracking (if needed)

```python
from src.utils.token_tracker import TokenTracker

# Track a custom LLM call
TokenTracker.track_usage(
    agent_name="CustomAgent",
    model_name="llama-3.3-70b-versatile",
    input_tokens=1000,
    output_tokens=500,
    metadata={'temperature': 0.1}
)

# Get current usage
usage = TokenTracker.get_usage()
print(f"Total cost: ${usage['total_cost']:.4f}")

# Get agent breakdown
breakdown = TokenTracker.get_agent_breakdown()
for agent in breakdown:
    print(f"{agent['agent']}: {agent['total_tokens']} tokens")
```

---

## Customization

### Changing Model Pricing

Edit `src/utils/token_tracker.py`:

```python
PRICING = {
    'llama-3.3-70b-versatile': {
        'input': 0.59,   # $ per 1M input tokens
        'output': 0.79   # $ per 1M output tokens
    },
    # Add more models here
    'your-model-name': {
        'input': 1.00,
        'output': 2.00
    }
}
```

### Changing UI Colors

Edit `src/ui/components/token_metrics.py`:

```python
# In display_token_metrics(), modify the gradient:
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

# Color thresholds for badges:
if total_cost < 0.01:
    color = "#28a745"  # Green
elif total_cost < 0.05:
    color = "#ffc107"  # Yellow
else:
    color = "#dc3545"  # Red
```

---

## Troubleshooting

### Tokens Not Showing
1. Ensure agents are calling `self.track_chain_response(response)`
2. Check that response has `response_metadata['token_usage']`
3. Verify Groq API returns token usage in metadata

### Cost Incorrect
1. Verify model name matches pricing table
2. Check Groq pricing hasn't changed
3. Ensure calculation uses correct units (per 1M tokens)

### UI Not Updating
1. Token metrics update after each agent run
2. If stuck, try refreshing the page
3. Check browser console for errors

### Reset Not Working
1. Ensure Streamlit session state is accessible
2. Try `st.rerun()` after reset
3. Check for errors in browser console

---

## Future Enhancements

Potential improvements:
1. **Export token metrics** with HTML reports
2. **Budget alerts** when cost exceeds threshold
3. **Token usage charts** over time
4. **Model comparison** tracking
5. **Per-dataset cost history**
6. **Estimated cost preview** before running agents
7. **Token usage optimization suggestions**

---

## Summary

✅ **4 Steps Completed:**
1. ✅ Created token tracking service (`token_tracker.py`)
2. ✅ Modified BaseAgent and all 7 agents to track tokens
3. ✅ Created expandable token metrics UI component (Option B)
4. ✅ Integrated into sidebar in `app.py`

**Result:** Users can now see real-time token usage and costs for all LLM calls in the left sidebar!

---

## Support

For issues or questions:
- Check `test_token_tracking.py` output
- Review agent implementations in `src/agents/`
- Inspect session state in Streamlit debugger
- Verify Groq API responses include token metadata
