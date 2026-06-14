# Setup Guide

## Prerequisites

- Python 3.10 or higher
- Groq API key (get free at https://console.groq.com)

## Installation Steps

### 1. Clone or Download the Project

```bash
cd test
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_actual_key_here
```

**Getting a Groq API Key:**
1. Go to https://console.groq.com
2. Sign up for free account
3. Navigate to API Keys section
4. Create new API key
5. Copy and paste into .env file

### 5. Test the Installation

Run the test script to verify everything works:

```bash
python test_pipeline.py
```

This will:
- Create a sample dataset
- Test the DatasetHandle (in-memory and sampled modes)
- Test the ProfileAgent
- Show example output

### 6. Run the Streamlit App

```bash
streamlit run src/ui/app.py
```

The app will open in your browser at http://localhost:8501

## Quick Start Usage

1. **Upload Dataset**: Use the sidebar to upload a CSV file
2. **Profile Dataset**: Click "Profile Dataset" button to run initial analysis
3. **Review Results**: See agent findings with explainability
4. **Ask Questions**: Use the chat to ask about your data
5. **Choose Workflow**: Select from pre-defined workflows:
   - Quick Profile (5 min)
   - Deep Clean (15 min)
   - Feature Engineering (20 min)

## Project Structure

```
test/
├── src/
│   ├── agents/          # AI agents for analysis
│   │   ├── base_agent.py
│   │   └── profile_agent.py
│   ├── data/            # Data handling layer
│   │   ├── backends.py
│   │   └── dataset_handle.py
│   ├── graph/           # LangGraph workflows
│   │   └── workflow.py
│   ├── ui/              # Streamlit UI
│   │   └── app.py
│   └── utils/           # Helper functions
│       ├── types.py
│       └── helpers.py
├── data/
│   ├── uploads/         # Uploaded datasets
│   ├── artifacts/       # Generated visualizations
│   └── checkpoints/     # LangGraph state
├── test_pipeline.py     # Test script
├── requirements.txt     # Python dependencies
└── .env                 # Configuration (you create this)
```

## Troubleshooting

### Import Errors

If you get import errors, make sure:
1. Virtual environment is activated
2. All dependencies installed: `pip install -r requirements.txt`
3. You're running from project root directory

### Groq API Errors

If you get API errors:
1. Check your API key is correct in .env
2. Verify you have API credits (free tier available)
3. Check internet connection

### File Not Found Errors

If dataset upload fails:
1. Ensure `data/uploads/` directory exists
2. Check file permissions
3. Try with a smaller CSV first

### Memory Issues

For large datasets (>500MB):
- The system automatically switches to sampling mode
- DuckDB handles processing without loading full dataset

## Next Steps

After setup, you can:

1. **Try the sample dataset**: Run `test_pipeline.py` to create sample data
2. **Upload your own data**: Use any CSV file
3. **Explore workflows**: Try different analysis workflows
4. **Extend agents**: Add new agents in `src/agents/`
5. **Customize workflows**: Modify `src/graph/workflow.py`

## Phase 2 Features (Coming Soon)

- QualityAgent: Duplicates, outliers, data validation
- TransformAgent: Apply transformations with approval
- VisualizationAgent: Generate plots and charts
- FeatureAgent: Correlation and feature engineering
- StatAgent: Statistical tests and validation

## Support

For issues or questions:
1. Check this setup guide
2. Review README.md
3. Check error messages carefully
4. Verify environment setup

## Development

To extend the pipeline:

1. **Add new agent**: Create in `src/agents/`, inherit from `BaseAgent`
2. **Modify workflow**: Edit `src/graph/workflow.py` to add nodes
3. **Update UI**: Modify `src/ui/app.py` for new features
4. **Test**: Run `test_pipeline.py` after changes
