# Progress Tracker Enhancement

## Overview

The Progress Tracker is a comprehensive UI component that provides real-time visual feedback during workflow execution in the EDA Pipeline. It addresses the critical UX issue where users had no visibility into multi-agent workflows that could take several minutes to complete.

## Features

### 1. **Visual Workflow Stepper**
- Real-time status updates for each agent
- Color-coded status indicators:
  - ⏳ **Pending** (Gray) - Not started
  - 🔄 **Running** (Blue) - Currently executing
  - ✅ **Completed** (Green) - Successfully finished
  - ❌ **Failed** (Red) - Error occurred
  - ⏭️ **Skipped** (Dark Gray) - Bypassed

### 2. **Progress Metrics**
- **Completion Percentage**: Visual progress bar showing overall completion
- **Step Counter**: "3/6 steps completed"
- **Time Tracking**: Duration for each completed step
- **ETA Calculation**: Estimated time remaining based on average step duration

### 3. **Two Display Modes**

#### Full View (`.render()`)
- Vertical step-by-step breakdown
- Detailed descriptions for active steps
- Error messages for failed steps
- Substep details (expandable)
- Individual step timings

#### Compact View (`.render_compact()`)
- Horizontal progress bar
- Icon-based step indicators
- Minimal space usage
- Perfect for persistent display

### 4. **Real-time Updates**
- Live status updates as agents execute
- Smooth animations for active steps
- Automatic progress bar updates
- No page refresh required

## Architecture

### Core Components

```
src/ui/components/
├── __init__.py
└── progress_tracker.py
    ├── WorkflowStep         # Individual step data model
    ├── WorkflowProgressTracker  # Main tracker orchestrator
    ├── AGENT_STEPS          # Pre-defined agent configurations
    └── create_workflow_tracker()  # Factory function
```

### Data Model

**WorkflowStep**
```python
class WorkflowStep:
    id: str                  # Unique identifier (e.g., "profile")
    name: str                # Display name (e.g., "Profile Dataset")
    description: str         # Step description
    icon: str                # Emoji icon
    status: Literal[...]     # Current status
    start_time: datetime     # When step started
    end_time: datetime       # When step completed/failed
    error_message: str       # Error details if failed
    substeps: List[str]      # Optional sub-operations
```

**WorkflowProgressTracker**
```python
class WorkflowProgressTracker:
    workflow_name: str           # Name of workflow
    steps: List[WorkflowStep]    # All steps in sequence
    start_time: datetime         # Workflow start
    
    # Computed properties
    @property current_step       # Currently running step
    @property completed_count    # Number of completed steps
    @property progress_percentage # 0-100%
    @property estimated_time_remaining  # "~2m 30s"
```

## Integration

### 1. Import Components

```python
from src.ui.components import (
    create_workflow_tracker,
    WorkflowProgressTracker,
    PROGRESS_TRACKER_CSS,
    AGENT_STEPS
)
```

### 2. Initialize Session State

```python
if "workflow_tracker" not in st.session_state:
    st.session_state.workflow_tracker = None
```

### 3. Create Tracker

```python
# For pre-defined workflows
tracker = create_workflow_tracker("complete_analysis")

# Or build custom workflow
from src.ui.components import WorkflowStep
steps = [
    AGENT_STEPS["profile"],
    AGENT_STEPS["quality"],
    AGENT_STEPS["visualization"]
]
tracker = WorkflowProgressTracker("Custom Workflow", steps)
```

### 4. Execute Workflow with Progress

```python
# Create progress container
progress_container = st.empty()

# Store tracker in session state
st.session_state.workflow_tracker = tracker

for step_id, agent_name, agent in agent_configs:
    step = next((s for s in tracker.steps if s.id == step_id), None)
    
    # Start step
    step.start()
    with progress_container.container():
        tracker.render()
    
    try:
        # Run agent
        result = agent.analyze(dataset)
        
        # Complete step
        step.complete()
        
    except Exception as e:
        # Handle failure
        step.fail(str(e))
        break
    
    # Update display
    with progress_container.container():
        tracker.render()
```

### 5. Display in UI

```python
# In main() function
if st.session_state.workflow_tracker:
    st.session_state.workflow_tracker.render_compact()
```

## Pre-defined Workflows

The system comes with 4 pre-configured workflows:

### 1. **Quick Analysis**
- Profile → Quality → Visualization
- Est. time: ~2-3 minutes
- Use case: Fast dataset overview

### 2. **Complete Analysis**
- Profile → Quality → Visualization → Feature → Stat → Transform
- Est. time: ~5-8 minutes
- Use case: Full EDA pipeline

### 3. **Deep Dive**
- Profile → Quality → Visualization → Feature → Stat
- Est. time: ~4-6 minutes
- Use case: Comprehensive analysis without transformations

### 4. **ML Preparation**
- Profile → Quality → Feature → Transform
- Est. time: ~3-5 minutes
- Use case: Preparing dataset for machine learning

## Usage Examples

### Example 1: Run Complete Analysis

```python
def run_complete_analysis():
    tracker = create_workflow_tracker("complete_analysis")
    st.session_state.workflow_tracker = tracker
    
    progress_container = st.empty()
    
    agent_configs = [
        ("profile", ProfileAgent()),
        ("quality", QualityAgent()),
        # ... more agents
    ]
    
    for step_id, agent in agent_configs:
        step = next(s for s in tracker.steps if s.id == step_id)
        step.start()
        
        with progress_container.container():
            tracker.render()
        
        result = agent.analyze(dataset)
        step.complete()
    
    st.success("✅ Analysis complete!")
```

### Example 2: Single Agent Execution

```python
def run_single_agent(agent_name: str):
    step = AGENT_STEPS["profile"]
    tracker = WorkflowProgressTracker(f"Running {agent_name}", [step])
    
    step.start()
    tracker.render_compact()
    
    result = agent.analyze(dataset)
    step.complete()
    
    st.success(f"Completed in {step.duration:.1f}s")
```

### Example 3: Error Handling

```python
try:
    step.start()
    result = agent.analyze(dataset)
    step.complete()
except Exception as e:
    step.fail(str(e))
    st.error(f"Agent failed: {str(e)}")
    # Continue or stop workflow based on criticality
```

## Customization

### Adding New Steps

```python
from src.ui.components import WorkflowStep

custom_step = WorkflowStep(
    id="custom_validation",
    name="Custom Validation",
    description="Performing domain-specific validation checks",
    icon="🔍"
)

# Add to workflow
steps = [AGENT_STEPS["profile"], custom_step]
tracker = WorkflowProgressTracker("Custom Workflow", steps)
```

### Styling

The progress tracker uses inline styles and custom CSS defined in `PROGRESS_TRACKER_CSS`. Key style classes:

- `.step-container` - Individual step wrapper
- `.progress-badge` - Status badges
- `.badge-completed` / `.badge-running` / etc. - Status-specific colors

### Animations

Active steps have a pulse animation defined in CSS:

```css
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

## Benefits

### User Experience
- **Transparency**: Users know exactly what's happening
- **Trust**: Builds confidence in the system
- **Patience**: Reduces perceived wait time with clear progress
- **Error Awareness**: Immediate feedback on failures

### Developer Experience
- **Easy Integration**: Drop-in component with minimal code
- **Flexible**: Works with any workflow structure
- **Reusable**: Same component for all agent executions
- **Debuggable**: Clear visibility into execution flow

### Performance Impact
- **Minimal**: Lightweight rendering with Streamlit containers
- **Non-blocking**: Progress updates don't slow down agent execution
- **Efficient**: Only rerenders progress section, not entire page

## Future Enhancements

### Planned Features
1. **Pause/Resume**: Allow users to pause long-running workflows
2. **Step Dependencies**: Visual indicators showing which steps depend on others
3. **Parallel Execution**: Show multiple agents running simultaneously
4. **History Tracking**: Save progress history for audit trail
5. **Export Progress**: Download progress report as JSON/PDF
6. **Custom Callbacks**: Hook into step lifecycle events
7. **Notifications**: Browser notifications for workflow completion

### Integration with Other Features
- **Phase 2 Enhancement**: Quality issue visualization during quality step
- **Phase 3 Enhancement**: Show before/after preview during transform step
- **Phase 4 Enhancement**: Export progress report alongside analysis report

## Technical Notes

### Session State Management
- Tracker stored in `st.session_state.workflow_tracker`
- Persists across reruns within same session
- Reset between different workflow executions

### Time Tracking
- Uses `datetime.now()` for precise timing
- Duration calculated as `(end_time - start_time).total_seconds()`
- ETA based on average of completed steps

### Error Handling
- Failed steps don't crash entire workflow
- Error messages captured in step object
- Workflow continues or stops based on implementation choice

## Testing

### Manual Testing Checklist
- [ ] Start complete analysis workflow
- [ ] Verify all steps show correct status
- [ ] Check timing accuracy
- [ ] Test error handling (inject failure)
- [ ] Test single agent execution
- [ ] Verify compact view rendering
- [ ] Test with different workflow types
- [ ] Check ETA calculation accuracy

### Edge Cases Handled
- Empty workflow (0 steps)
- Single step workflow
- All steps failed
- Steps completed in < 1 second
- Very long-running steps (> 1 hour)

## Migration Guide

### Upgrading Existing Code

**Before:**
```python
with st.spinner("Running analysis..."):
    for agent in agents:
        result = agent.analyze(dataset)
```

**After:**
```python
tracker = create_workflow_tracker("complete_analysis")
progress_container = st.empty()

for step_id, agent in zip(step_ids, agents):
    step = next(s for s in tracker.steps if s.id == step_id)
    step.start()
    
    with progress_container.container():
        tracker.render()
    
    result = agent.analyze(dataset)
    step.complete()
```

## Credits

- **Design Pattern**: Stepper UI pattern from Material Design
- **Inspiration**: GitHub Actions workflow visualization
- **Built with**: Streamlit, Python 3.10+

## Support

For issues or questions:
1. Check this documentation
2. Review `src/ui/components/progress_tracker.py` source code
3. See example usage in `src/ui/app_v3.py`
4. Raise issue in project repository

---

**Status**: ✅ Implemented in Phase 1 Enhancement  
**Version**: 1.0  
**Last Updated**: 2026-07-17
