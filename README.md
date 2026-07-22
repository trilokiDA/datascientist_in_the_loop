# EDA Pipeline with Agentic Workflow

An intelligent, production-ready EDA (Exploratory Data Analysis) pipeline powered by LangGraph, Groq, and open-source tools. Features a complete suite of specialized agents with interactive visualizations, export capabilities, and human-in-the-loop interaction.

## 🆕 What's New in v3.3

### 📊 Excel File Support (NEW!)
- ✅ **Excel Upload**: Support for `.xlsx` and `.xls` files in addition to CSV
- ✅ **Automatic Detection**: First sheet is automatically loaded and analyzed
- ✅ **Seamless Integration**: Excel files work with all agents and workflows
- ✅ **Same Performance**: Intelligent backend selection (in-memory vs sampled) for Excel files

## What's New in v3.2

### 🚦 Human-in-the-Loop Approval Gates (NEW!)
- ✅ **Agent Approval Gates**: Review and approve each agent before proceeding to the next
- ✅ **4 Decision Options**: Approve, Retry, Skip, or Stop at each agent
- ✅ **Decision History**: Track all approval decisions throughout workflow
- ✅ **3 New Workflows**: Quick Analysis, Deep Dive, and ML Prep with Approval Gates
- ✅ **Detailed Review UI**: See confidence scores, issues found, and recommendations
- ✅ **Agent-Specific Details**: Tailored detail views for each agent type
- ✅ **Thumbnail Gallery**: Quick preview of visualization plots with expand-to-full-size option

👉 **[Quick Start Guide](docs/APPROVAL_GATES_README.md)** | **[Full Documentation](docs/APPROVAL_GATES_GUIDE.md)**

#### Why Approval Gates Show Summary, Not Full Results?

The approval gate design follows a **two-phase workflow** for optimal user experience:

**Phase 1: Approval Gate (Quick Review)**
- **Purpose**: Fast decision-making - approve, retry, skip, or stop
- **Shows**: Summary metrics, key findings, reasoning, and thumbnail previews
- **Why compact?**
  - ⚡ **Speed**: Quick review enables fast decisions (30-60 seconds per agent)
  - 📏 **Size**: With 8+ plots and detailed tables, gates would become unwieldy
  - 🎯 **Focus**: Summary view keeps attention on decision-relevant information
  - 🔄 **Workflow**: Detailed analysis happens after approval, not during

**Phase 2: Results Tab (Deep Analysis)**
- **Purpose**: Comprehensive exploration of agent findings
- **Shows**: All plots in full size, complete tables, interactive visualizations, export options
- **When**: After workflow completes or individual agent runs
- **Where**: Navigate to tabbed interface (Profile, Quality, Visualizations, etc.)

This separation ensures approval gates remain **fast decision points** while full results provide **thorough analysis capabilities**.

### Enhanced Transformation System (v3.1)
- ✅ **Multi-Transformation Selection**: Select and apply multiple transformations at once with checkboxes
- ✅ **Complete CSV Export**: Apply transformations to full dataset and export as CSV
- ✅ **Column Change Visualization**: See exactly which columns are added/removed during transformations
- ✅ **One-Hot Encoding Preview**: Visual mapping showing how categorical columns transform to binary columns
- ✅ **Progress Tracking**: Real-time progress bar when applying transformations to large datasets
- ✅ **Quick Actions**: "Select All High Priority" for instant data cleaning

### Fixes & Improvements
- 🐛 Fixed transformation preview showing same results in before/after
- 🐛 Fixed DatasetHandle backend access for large datasets
- 🐛 Fixed CSV export not working
- 🔧 Added support for all 7 transformation types (encoding, scaling, imputation, etc.)
- 🔧 Enhanced error reporting with detailed tracebacks
- 🔧 Smart column comparison (only shows common columns to prevent errors)

## Features

### Core Capabilities
- **6 Specialized Agents**: ProfileAgent, QualityAgent, TransformAgent, VisualizationAgent, FeatureAgent, StatAgent
- **Interactive Chat Interface**: Real-time Streamlit UI with progress tracking
- **Explainable AI**: Every agent explains WHY and WHAT impact their findings have
- **Persistent State**: LangGraph checkpoints for pause/resume workflows
- **Hybrid Scale**: Handles small datasets in-memory, large datasets with intelligent sampling
- **Flexible Workflows**: Pre-defined pipelines + individual agent execution

### Advanced Features
- **Human-in-the-Loop Control**: Agent approval gates for reviewing and approving each step
- **Progress Tracking**: Real-time visual workflow progress with status indicators and ETA
- **Quality Visualizations**: Interactive charts for missing values, outliers, duplicates, and data quality metrics
- **Before/After Comparison**: Side-by-side transformation previews with delta metrics and impact analysis
- **Multi-Transformation Selection**: Select and apply multiple transformations at once with checkboxes
- **Column Change Visualization**: See exactly which columns are added/removed during transformations
- **Export System**: Professional HTML reports, JSON data exports, and transformed CSV outputs with full dataset support
- **ML Preparation**: Automated feature engineering and data preparation for machine learning
- **Decision Tracking**: Complete audit trail of human approval decisions

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

1. **Upload Dataset**: Click "Browse files" in the sidebar and upload a CSV or Excel file (`.csv`, `.xlsx`, `.xls`)
2. **View Quick Stats**: See immediate dataset overview (rows, columns, size)
3. **Choose Analysis**:
   - **Quick Analysis**: Run all 6 agents sequentially
   - **Individual Agent**: Select and run specific agents
   - **Deep Dive**: Comprehensive analysis with detailed insights
   - **ML Preparation**: Prepare data for machine learning workflows
4. **Enable Approval Gates** (Optional - NEW! 🚦):
   - ☑️ Check "Enable Approval Gates" to review each agent before continuing
   - Uncheck for automatic execution
5. **View Results**: Explore interactive tabs for each agent's analysis
6. **Transform Data**:
   - ☑️ Select multiple transformations
   - Preview combined effect
   - Apply to full dataset
   - Export transformed CSV
7. **Export**: Generate HTML reports, JSON data, or transformed CSV files

### Example: Transform Titanic Dataset

```
1. Upload titanic_train.csv (891 rows, 12 columns)
2. Run "Quick Analysis"
3. Go to "Transform" tab
4. Click "☑️ Select All High Priority"
   → 3 transformations selected
5. Click "Preview Selected (3)"
   → See: Sex becomes Sex_male & Sex_female
   → See: Missing Age values filled with median (28)
   → See: Cabin column removed (77% missing)
6. Click "Apply 3 transformations to Full Dataset"
   → Progress: Loading → Applying → Saving (100%)
7. Go to "Export" tab
8. Check "Transformed CSV"
9. Export Now
10. Download: transformed_dataset_20260720.csv (891 rows, 13 columns)
    → Ready for ML! 🚀
```

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
- Automated data cleaning proposals
- Missing value imputation strategies
- Outlier handling (capping, removal)
- Data type conversions
- Categorical encoding (one-hot, label)
- Numeric scaling (standard, min-max)
- Before/after comparison views
- **Multi-selection**: Apply multiple transformations at once
- **Full dataset application**: Apply to entire dataset with progress tracking
- **CSV export**: Save transformed data for external use

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

## Transformation Workflow

The TransformAgent offers a complete data transformation pipeline:

### 1. **Review Proposals**
- Agent analyzes your data and proposes transformations
- Organized by priority (High, Medium, Low)
- Each proposal includes reasoning and impact

### 2. **Multi-Selection**
- ☑️ Check boxes to select multiple transformations
- **Quick Actions**:
  - "Select All High Priority" - Instant data cleaning
  - "Preview Selected (N)" - See combined effect
  - "Deselect All" - Clear selections

### 3. **Preview Transformations**
- See before/after comparison with sample data
- View removed columns and new columns side-by-side
- See exact value mappings (e.g., 'male' → [0,1])
- Understand the combined effect of all selected transformations

### 4. **Apply to Full Dataset**
- Click "Apply N transformations to Full Dataset"
- Progress tracking shows: Loading → Applying → Saving
- Warning for large datasets (memory usage)
- Preview transformed data inline

### 5. **Export Transformed CSV**
- Go to Export section
- Check "Transformed CSV" (now enabled)
- Download your transformed dataset
- Use in Excel, Python, R, ML tools, etc.

### Example Workflow
```
1. Load Titanic dataset
2. Review 8 transformation proposals
3. ☑️ Select: "One-hot encode Sex", "Impute Age", "Drop Cabin"
4. Preview → See 'Sex' becomes 'Sex_male' and 'Sex_female'
5. Apply 3 transformations → 891 rows processed
6. Export → Download transformed_dataset.csv
7. Use in your ML pipeline! 🚀
```

## Available Workflows

### Quick Analysis (All Agents)
- Runs all 6 agents sequentially
- Comprehensive dataset overview
- ~5-10 minutes for typical datasets
- Best for: First-time analysis, complete understanding
- **NEW**: Available with Approval Gates for human review

### Deep Dive Workflow
- Thorough analysis (5 agents: Profile, Quality, Viz, Feature, Stat)
- Detailed quality assessment
- Advanced statistical tests
- Best for: Critical datasets, production data
- **NEW**: Available with Approval Gates for step-by-step review

### ML Preparation
- Feature engineering focus (4 agents: Profile, Quality, Feature, Transform)
- Correlation analysis
- Feature selection recommendations
- Training-ready data export
- Best for: Machine learning projects
- **NEW**: Available with Approval Gates for controlled ML prep

### Individual Agent Execution
- Run any single agent on-demand
- Fast, targeted analysis
- Best for: Specific questions, iterative exploration

### 🚦 NEW: Workflows with Approval Gates
All workflows now available with **Human-in-the-Loop approval gates**:
- Pause after each agent for human review
- See confidence scores, issues, and recommendations
- **4 decision options**: Approve, Retry, Skip, or Stop
- Full decision history tracking
- Best for: Critical analysis, compliance, learning

👉 **[Get Started with Approval Gates](docs/APPROVAL_GATES_README.md)**

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
- Apply multiple transformations: encoding, imputation, scaling, etc.
- Full dataset processing (not just samples)
- Progress tracking for large datasets
- Ready for downstream processing (Excel, Python, R, ML tools)
- Includes all selected TransformAgent changes

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
- **Column transformation mapping**: See exactly how columns change
- **Removed vs New columns**: Side-by-side view of added/removed columns
- **One-hot encoding visualization**: Grouped display of encoded columns
- **Value-by-value mapping**: See how original values transform to new values

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
- **For CSV export**: Must click "Apply to Full Dataset" first
- Check that transformed dataset shows "✅ Ready (N rows)"

### Transformation Issues
- **CSV checkbox disabled**: Apply transformations to full dataset first
- **Columns not showing**: Check the "Removed vs New Columns" section in preview
- **One-hot encoding not visible**: Look for new columns like `ColumnName_value1`, `ColumnName_value2`
- **DatasetHandle error**: Restart the app if backend connection issues occur
- **Large dataset slow**: Normal - check progress bar for status

## Documentation

Detailed documentation available in `docs/`:

### Core Features
- **PROGRESS_TRACKER.md**: Progress tracking component guide
- **QUALITY_VISUALIZATION.md**: Quality visualization system
- **EXPORT_FUNCTIONALITY.md**: Complete export system documentation
- **UI_UX_ENHANCEMENTS_SUMMARY.md**: All UI/UX improvements overview

### Transformation Features (NEW!)
- **TRANSFORMATION_PREVIEW_FIX.md**: Technical details of transformation preview fix
- **HOW_TO_SEE_NEW_COLUMNS.md**: Guide to viewing transformed columns
- **UI_LAYOUT_DIAGRAM.md**: Visual layout of transformation UI
- **TRANSFORMATION_PREVIEW_VISUAL_GUIDE.md**: Before/after comparison guide
- **CSV_EXPORT_FEATURE.md**: Complete CSV export documentation
- **EXPORT_CSV_QUICK_GUIDE.md**: Quick start guide for CSV export
- **CSV_EXPORT_FIX.md**: Technical fix for DatasetHandle backend
- **MULTI_TRANSFORMATION_SELECTION.md**: Multi-selection feature guide

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

**Current Version**: 3.2  
**Last Updated**: July 2026

### Recent Updates
- **v3.3** (July 2026): 📊 Excel file support (.xlsx, .xls), automatic sheet detection, seamless integration
- **v3.2** (July 2026): 🚦 Human-in-the-Loop approval gates, decision tracking, step-by-step agent review
- **v3.1** (July 2026): Multi-transformation selection, CSV export, column visualization
- **v3.0** (June 2026): Complete agent suite, progress tracking, quality visualizations

For questions, issues, or feature requests, please open an issue on the repository.
