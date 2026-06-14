# Architecture Documentation

## System Overview

The EDA Pipeline is built on a multi-layer architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                   │
│  - Chat interface                                       │
│  - File upload                                          │
│  - Approval buttons                                     │
│  - Visualization display                                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              LangGraph Orchestration                    │
│  - StateGraph workflow                                  │
│  - Checkpoint persistence (SQLite)                      │
│  - Interrupt nodes for human input                      │
│  - Conditional routing                                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Agent Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ProfileAgent │  │QualityAgent │  │FeatureAgent │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  VizAgent   │  │TransformAgt │  │  StatAgent  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  All agents return: AgentResponse                       │
│    - result: Dict                                       │
│    - reasoning: str (WHY)                               │
│    - impact: str (WHAT impact)                          │
│    - recommendations: List[str]                         │
│    - confidence: float                                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Data Access Layer                          │
│                                                         │
│  DatasetHandle (abstraction)                            │
│         │                                               │
│    ┌────┴────┐                                         │
│    │         │                                         │
│ ┌──▼──┐  ┌──▼──────┐                                  │
│ │Pandas│  │ DuckDB  │                                  │
│ │      │  │         │                                  │
│ │In-mem│  │Sampled  │                                  │
│ └──────┘  └─────────┘                                  │
│ (<500MB)   (>500MB)                                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Persistence Layer                          │
│  - SQLite: LangGraph checkpoints                        │
│  - File system: Datasets, plots, reports                │
│  - State versioning                                     │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. UI Layer (Streamlit)

**Responsibilities:**
- File upload and dataset management
- Chat-based interaction
- Displaying agent responses with explainability
- Human approval gates (buttons)
- Workflow selection
- Progress tracking

**Key Files:**
- `src/ui/app.py`: Main Streamlit application

**Features:**
- Real-time message streaming
- Expandable "Why?" sections for each agent
- Workflow progress indicators
- Interactive approval/rejection buttons

### 2. Orchestration Layer (LangGraph)

**Responsibilities:**
- Workflow state management
- Agent invocation sequencing
- Human-in-the-loop interrupts
- State persistence and resumption
- Conditional routing based on decisions

**Key Files:**
- `src/graph/workflow.py`: StateGraph definition

**State Schema (`EDAState`):**
```python
{
    "dataset_id": str,
    "dataset_path": str,
    "dataset_mode": "in_memory" | "sampled",
    "workflow_type": "quick_profile" | "deep_clean" | "feature_engineering",
    "current_step": str,
    "completed_steps": List[str],
    "pending_approval": bool,
    "approval_context": Dict,
    "profile_results": Dict,
    "quality_results": Dict,
    "feature_results": Dict,
    "reasoning_log": List[ReasoningLog],
    "user_decisions": List[UserDecision],
    "pending_transformations": List[Transformation],
    "applied_transformations": List[Transformation],
    ...
}
```

**Checkpoint Strategy:**
- SQLite-based persistence
- State saved at each node
- Resume from any interrupt point
- Thread-based isolation

### 3. Agent Layer

**Base Architecture:**

All agents inherit from `BaseAgent` and implement:
```python
class BaseAgent(ABC):
    def get_agent_name(self) -> str
    def analyze(self, dataset_handle, context) -> AgentResponse
```

**Implemented Agents:**

#### ProfileAgent
- **Purpose**: Initial dataset profiling
- **Analyzes**: Shape, dtypes, missing values, cardinality
- **Returns**: Basic statistics + issues detected
- **LLM Usage**: Interprets findings, provides recommendations

#### QualityAgent (Phase 2)
- **Purpose**: Data quality assessment
- **Analyzes**: Duplicates, outliers, inconsistencies
- **Returns**: Quality issues + severity levels

#### FeatureAgent (Phase 2)
- **Purpose**: Feature relationships
- **Analyzes**: Correlations, multicollinearity, importance hints
- **Returns**: Feature insights + engineering suggestions

#### VizAgent (Phase 2)
- **Purpose**: Generate visualizations
- **Analyzes**: Distribution, relationships, patterns
- **Returns**: Plot files + interpretation

#### TransformAgent (Phase 2)
- **Purpose**: Data transformations
- **Analyzes**: Required transformations based on prior findings
- **Returns**: Transformation proposals + impact assessment

#### StatAgent (Phase 2)
- **Purpose**: Statistical validation
- **Analyzes**: Hypothesis tests, normality, distributions
- **Returns**: Statistical test results + interpretations

**Agent Communication:**

Agents receive context from previous steps:
```python
context = {
    "profile_results": {...},
    "quality_results": {...},
    "user_feedback": [...]
}
```

### 4. Data Access Layer

**DatasetHandle Abstraction:**

Provides unified interface regardless of backend:
```python
handle = DatasetHandle(path)  # Auto-detects mode

# Unified interface
handle.get_shape()
handle.describe()
handle.get_missing_info()
handle.sample(n)
```

**Backend Selection:**

```python
if file_size < 500MB:
    backend = InMemoryBackend(pandas)
else:
    backend = SampledBackend(DuckDB)
```

**InMemoryBackend (Pandas):**
- Direct DataFrame operations
- Full dataset in memory
- Fast operations
- No sampling needed

**SampledBackend (DuckDB):**
- SQL-based operations
- Dataset stays on disk
- Sampling for profiling
- Extrapolation for estimates

### 5. Persistence Layer

**Checkpoint Storage:**
- Location: `data/checkpoints/checkpoints.db`
- Format: SQLite database
- Content: Full EDAState at each node
- Indexing: By thread_id

**Artifact Storage:**
- Datasets: `data/uploads/`
- Plots: `data/artifacts/plots/`
- Reports: `data/artifacts/reports/`

**State Versioning:**
- Each state update creates new version
- Previous states accessible
- Full audit trail

## Data Flow

### Typical Analysis Flow

```
1. User uploads CSV
   ↓
2. DatasetHandle created (auto-selects backend)
   ↓
3. User selects workflow or agent
   ↓
4. LangGraph creates initial state
   ↓
5. ProfileAgent node executes
   ↓
6. State updated with results + reasoning
   ↓
7. Human review node (interrupt)
   ↓
8. UI displays results with "Why?" section
   ↓
9. User approves/rejects/modifies
   ↓
10. State updated with decision
    ↓
11. Graph resumes with conditional routing
    ↓
12. Next agent executes based on decision
    ↓
    ... (loop continues)
```

### Interrupt-Resume Pattern

```python
# Graph execution
config = {"configurable": {"thread_id": "session_123"}}

# Start workflow
for event in graph.stream(initial_state, config):
    if "pending_approval" in event:
        # INTERRUPT - wait for user
        break

# Later... user responds
graph.update_state(config, {
    "user_decisions": [...],
    "pending_approval": False
})

# Resume workflow
for event in graph.stream(None, config):
    # Continues from interrupt point
    ...
```

## Explainability Architecture

Every agent action is logged with:

```python
ReasoningLog {
    timestamp: str,
    agent: str,
    action: str,
    reasoning: str,      # WHY this action
    impact: str,         # WHAT the consequences are
    confidence: float    # How certain (0-1)
}
```

**UI Presentation:**

```
┌─────────────────────────────────────┐
│ 📊 ProfileAgent Results             │
│ [result summary...]                 │
│                                     │
│ ▼ 🧠 Why did the agent do this?    │
│   Reasoning: ...                    │
│   Impact: ...                       │
│   Recommendations: ...              │
│   Confidence: 95%                   │
└─────────────────────────────────────┘
```

## Scalability Considerations

### Small Datasets (< 500MB)
- In-memory processing
- Full dataset operations
- No sampling overhead
- Faster execution

### Large Datasets (> 500MB)
- DuckDB SQL engine
- Sampling for profiling
- Lazy evaluation
- Memory-efficient

### Very Large Datasets (> 10GB)
Future enhancements:
- Chunked processing
- Distributed sampling
- Parallel agent execution
- Incremental checkpointing

## Security Considerations

1. **File Upload**: Size limits, type validation
2. **API Keys**: Environment variables only
3. **SQL Injection**: Parameterized queries in DuckDB
4. **State Isolation**: Thread-based separation
5. **Data Privacy**: Local processing, no external data transmission (except LLM API)

## Extension Points

### Adding New Agent

1. Create new agent class in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement `analyze()` method
4. Return `AgentResponse` with explainability
5. Add node to workflow graph
6. Update UI to display results

### Adding New Workflow

1. Define in `src/utils/types.py` `WORKFLOWS`
2. Add nodes to graph
3. Define interrupt points
4. Add UI trigger in sidebar
5. Document expected flow

### Custom Backend

1. Implement `DataBackend` interface
2. Add to `DatasetHandle` selection logic
3. Handle specific data format
4. Ensure consistent API

## Performance Optimization

1. **Caching**: Dataset handle caches basic info
2. **Sampling**: DuckDB creates sample once, reuses
3. **Lazy Loading**: State only loads what's needed
4. **Checkpointing**: Incremental state saves
5. **LLM Batching**: Multiple analyses in single call (Phase 2)

## Future Architecture Enhancements

1. **Plugin System**: Dynamic agent loading
2. **Multi-Modal**: Support for images, text data
3. **Distributed**: Multi-node processing
4. **Streaming**: Real-time data ingestion
5. **Federation**: Multi-dataset analysis
