# EDA Pipeline with Agentic Workflow

An intelligent EDA (Exploratory Data Analysis) pipeline powered by LangGraph, Groq, and open-source tools, featuring human-in-the-loop interaction and persistent state management.

## Features

- 🤖 **Agentic Analysis**: Specialized agents for profiling, quality checks, feature analysis, and more
- 💬 **Real-time Chat Interface**: Interactive Streamlit UI for collaboration
- 🔍 **Explainability**: Every agent explains WHY and WHAT impact their findings have
- 💾 **Persistence**: LangGraph checkpoints allow pause/resume workflows
- 📊 **Hybrid Scale**: Handles small datasets in-memory, large datasets with sampling
- 🎯 **Customizable Workflows**: Pre-defined pipelines + manual step injection

## Architecture

```
Streamlit UI ↔ LangGraph Orchestration ↔ Specialized Agents ↔ Data Layer (Pandas/DuckDB)
```

## Quick Start

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

3. **Run the app**
```bash
streamlit run src/ui/app.py
```

4. **Upload a CSV** and start chatting with the EDA agents!

## Project Structure

```
├── src/
│   ├── agents/          # Specialized EDA agents
│   ├── data/            # DatasetHandle and backends
│   ├── graph/           # LangGraph workflow definitions
│   ├── ui/              # Streamlit interface
│   └── utils/           # Helper functions
├── data/
│   ├── uploads/         # Uploaded datasets
│   ├── artifacts/       # Generated plots and reports
│   └── checkpoints/     # LangGraph state persistence
└── requirements.txt
```

## Available Workflows

1. **Quick Profile**: Fast overview of dataset health (5 min)
2. **Deep Clean**: Thorough cleaning with multiple approval gates
3. **Feature Engineering**: ML prep with correlation and feature analysis

## Tech Stack

- **LangGraph**: State machine orchestration
- **Groq**: Fast LLM inference (Llama 3.1)
- **Streamlit**: Interactive UI
- **Pandas/DuckDB**: Data processing
- **Plotly/Seaborn**: Visualizations
- **SQLite**: Persistence layer
