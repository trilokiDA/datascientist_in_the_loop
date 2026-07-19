# EDA Pipeline with Agentic Workflow

An intelligent, production-ready EDA (Exploratory Data Analysis) pipeline powered by LangGraph, Groq, and open-source tools. Features a complete suite of specialized agents with interactive visualizations, export capabilities, and human-in-the-loop interaction.

## Features

### Core Capabilities
- **6 Specialized Agents**: ProfileAgent, QualityAgent, TransformAgent, VisualizationAgent, FeatureAgent, StatAgent
- **Interactive Chat Interface**: Real-time Streamlit UI with progress tracking
- **Explainable AI**: Every agent explains WHY and WHAT impact their findings have
- **Persistent State**: LangGraph checkpoints for pause/resume workflows
- **Hybrid Scale**: Handles small datasets in-memory, large datasets with intelligent sampling
- **Flexible Workflows**: Pre-defined pipelines + individual agent execution

### Advanced Features
- **Progress Tracking**: Real-time visual workflow progress with status indicators and ETA
- **Quality Visualizations**: Interactive charts for missing values, outliers, duplicates, and data quality metrics
- **Before/After Comparison**: Side-by-side transformation previews with delta metrics and impact analysis
- **Export System**: Professional HTML reports, JSON data exports, and transformed CSV outputs
- **ML Preparation**: Automated feature engineering and data preparation for machine learning

## Architecture

```
┌─────────────────┐
│  Streamlit UI   │  ← Interactive interface with progress tracking
└────────┬────────┘
         │
┌────────▼────────┐
│  LangGraph      │  ← State machine orchestration
│  Orchestration  │
└────────┬────────┘
         │
┌────────▼────────────────────────────────────────────┐
│              Specialized Agents                      │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│ Profile  │ Quality  │Transform │Visualize │Features │
│  Agent   │  Agent   │  Agent   │  Agent   │ Agent   │
│          │          │          │          │  Stat   │
└──────────┴──────────┴──────────┴──────────┴─────────┘
         │
┌────────▼────────┐
│   Data Layer    │  ← Pandas/DuckDB with intelligent switching
└─────────────────┘
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd test

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your GROQ_API_KEY
# Get your key from: https://console.groq.com/
```

Example `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
LANGCHAIN_TRACING_V2=false
```

### 3. Run the Application

```bash
streamlit run src/ui/app.py
```

The app will open in your browser at `http://localhost:8501`

### 4. Usage

1. **Upload Dataset**: Click "Browse files" in the sidebar and upload a CSV file
2. **View Quick Stats**: See immediate dataset overview (rows, columns, size)
3. **Choose Analysis**:
   - **Quick Analysis**: Run all 6 agents sequentially
   - **Individual Agent**: Select and run specific agents
   - **Deep Dive**: Comprehensive analysis with detailed insights
   - **ML Preparation**: Prepare data for machine learning workflows
4. **View Results**: Explore interactive tabs for each agent's analysis
5. **Export**: Generate HTML reports, JSON data, or transformed CSV files

## Project Structure

```
├── src/
│   ├── agents/              # 6 Specialized EDA agents
│   │   ├── profile.py       # Dataset profiling and statistics
│   │   ├── quality.py       # Data quality assessment
│   │   ├── transform.py     # Data cleaning and transformation
│   │   ├── visualization.py # Chart generation and visual analysis
│   │   ├── feature.py       # Feature engineering and analysis
│   │   └── stat.py          # Statistical testing and analysis
│   ├── data/                # DatasetHandle and backend management
│   │   └── dataset_handle.py
│   ├── graph/               # LangGraph workflow definitions
│   ├── ui/                  # Streamlit interface
│   │   ├── app.py           # Main application
│   │   └── components/      # Reusable UI components
│   └── utils/               # Helper functions and utilities
│       ├── export.py        # Export manager for HTML/JSON/CSV
│       └── helpers.py
├── tests/                   # Test and demo files
│   ├── test_*.py            # Unit and integration tests
│   ├── demo_*.py            # Interactive demonstrations
│   └── README.md            # Test documentation
├── data/
│   ├── uploads/             # Uploaded datasets
│   ├── exports/             # Generated reports and exports
│   ├── artifacts/           # Generated plots and visualizations
│   └── checkpoints/         # LangGraph state persistence
├── docs/                    # Detailed documentation
│   ├── PROGRESS_TRACKER.md
│   ├── QUALITY_VISUALIZATION.md
│   ├── BEFORE_AFTER_COMPARISON.md
│   ├── EXPORT_FUNCTIONALITY.md
│   └── UI_UX_ENHANCEMENTS_SUMMARY.md
├── requirements.txt
├── .env.example
└── README.md
```

## Available Agents

### 1. ProfileAgent
- Dataset shape and structure
- Column types and distributions
- Memory usage analysis
- Basic statistics per column

### 2. QualityAgent
- Missing value detection and patterns
- Duplicate row identification
- Outlier detection (IQR method)
- Data quality scoring
- Interactive quality visualizations

### 3. TransformAgent
- Automated data cleaning
- Missing value imputation
- Outlier handling
- Data type conversions
- Before/after comparison views

### 4. VisualizationAgent
- Automatic chart generation
- Distribution plots
- Correlation heatmaps
- Trend analysis
- Interactive Plotly visualizations

### 5. FeatureAgent
- Feature importance analysis
- Correlation analysis
- Feature engineering suggestions
- ML-ready feature preparation

### 6. StatAgent
- Statistical hypothesis testing
- Distribution analysis (normality tests)
- Comparative statistics
- Confidence intervals

## Available Workflows

### Quick Analysis (All Agents)
- Runs all 6 agents sequentially
- Comprehensive dataset overview
- ~5-10 minutes for typical datasets
- Best for: First-time analysis, complete understanding

### Deep Dive Workflow
- Thorough analysis with multiple approval gates
- Detailed quality assessment
- Advanced statistical tests
- Best for: Critical datasets, production data

### ML Preparation
- Feature engineering focus
- Correlation analysis
- Feature selection recommendations
- Training-ready data export
- Best for: Machine learning projects

### Individual Agent Execution
- Run any single agent on-demand
- Fast, targeted analysis
- Best for: Specific questions, iterative exploration

## Export Features

Generate professional outputs in multiple formats:

### HTML Reports
- Beautiful, interactive reports
- Embedded visualizations (Plotly charts)
- Confidence scores and reasoning
- Table of contents navigation
- Shareable with stakeholders

### JSON Data
- Complete analysis results
- Structured, hierarchical format
- Easy integration with other tools
- API-ready format

### Transformed CSV
- Cleaned and transformed dataset
- Ready for downstream processing
- Includes all TransformAgent changes

**Export Location**: `data/exports/`

**Naming Convention**: `[custom_name_]<type>_<timestamp>.<ext>`

See `docs/EXPORT_FUNCTIONALITY.md` for detailed documentation.

## UI Components & Visualizations

### Progress Tracking
- Visual workflow stepper
- Real-time status updates (pending → running → completed)
- Individual step timing with ETA
- Color-coded indicators

### Quality Dashboard
- Missing value heatmaps
- Outlier detection box plots
- Duplicate analysis gauge charts
- Overall quality score
- Interactive drill-down

### Before/After Comparison
- Side-by-side data preview
- Delta metrics (Missing, Duplicates, Outliers)
- Distribution comparison charts
- Statistical comparison tables
- Impact severity indicators

## Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Orchestration** | LangGraph | State machine workflow management |
| **LLM** | Groq (Llama 3.1) | Fast LLM inference for agent reasoning |
| **UI** | Streamlit | Interactive web interface |
| **Data Processing** | Pandas, DuckDB | In-memory and large dataset handling |
| **Visualization** | Plotly, Seaborn, Matplotlib | Interactive and static charts |
| **Statistics** | SciPy, Statsmodels, Scikit-learn | Statistical analysis and ML prep |
| **Persistence** | SQLite | State checkpointing |

## Configuration & Settings

### Environment Variables
- `GROQ_API_KEY` (required): Your Groq API key
- `LANGCHAIN_TRACING_V2` (optional): Enable LangSmith tracing
- `LANGCHAIN_API_KEY` (optional): LangSmith API key
- `LANGCHAIN_PROJECT` (optional): Project name for tracing

### In-App Settings
- **Show Reasoning**: Display agent's decision-making process
- **Show Confidence**: Show confidence scores for findings
- **Analysis Type**: Choose workflow type
- **Agent Selection**: Pick individual agents to run

## Requirements

- Python 3.9+
- 4GB RAM minimum (8GB recommended for large datasets)
- Internet connection (for Groq API)
- Modern web browser

## Best Practices

### For Small Datasets (< 10k rows)
- Use "Quick Analysis" for complete overview
- All processing happens in-memory
- Fast execution (~2-5 minutes)

### For Large Datasets (> 100k rows)
- System automatically switches to DuckDB backend
- Intelligent sampling for visualization
- Enable progress tracking to monitor long-running tasks

### For Production Use
1. Run Deep Dive Workflow for thorough analysis
2. Export HTML reports for documentation
3. Export JSON for integration with other systems
4. Use transformed CSV for downstream processing
5. Review confidence scores and reasoning before acting on recommendations

### For ML Projects
1. Use ML Preparation workflow
2. Review FeatureAgent recommendations
3. Check StatAgent for distribution assumptions
4. Export transformed CSV for model training
5. Use QualityAgent to ensure data cleanliness

## Troubleshooting

### "No API key found"
- Ensure `.env` file exists in project root
- Verify `GROQ_API_KEY` is set correctly
- Restart Streamlit after changing `.env`

### Dataset Upload Issues
- Ensure CSV is properly formatted
- Check file encoding (UTF-8 recommended)
- Verify no corrupted rows
- Maximum recommended size: 500MB

### Slow Performance
- Large datasets trigger automatic DuckDB backend
- Reduce sample size for visualizations
- Run individual agents instead of complete analysis
- Close other browser tabs to free memory

### Export Failures
- Ensure `data/exports/` directory exists
- Check disk space availability
- Verify write permissions
- For CSV export, TransformAgent must complete first

## Documentation

Detailed documentation available in `docs/`:

- **PROGRESS_TRACKER.md**: Progress tracking component guide
- **QUALITY_VISUALIZATION.md**: Quality visualization system
- **BEFORE_AFTER_COMPARISON.md**: Transformation comparison feature
- **EXPORT_FUNCTIONALITY.md**: Complete export system documentation
- **UI_UX_ENHANCEMENTS_SUMMARY.md**: All UI/UX improvements overview

## Contributing

Contributions welcome! Areas for improvement:
- Additional agent types (time series, text analysis)
- More export formats (PDF, Excel)
- Advanced visualizations
- Performance optimizations
- Custom workflow builders

## License

[Add your license here]

## Acknowledgments

Built with:
- [LangChain](https://langchain.com/) - LLM orchestration
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Graph-based workflows
- [Groq](https://groq.com/) - Ultra-fast LLM inference
- [Streamlit](https://streamlit.io/) - Interactive web UI
- [Plotly](https://plotly.com/) - Interactive visualizations

---

**Current Version**: 3.0
**Last Updated**: July 2026

For questions, issues, or feature requests, please open an issue on the repository.
