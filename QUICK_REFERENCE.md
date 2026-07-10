# 🚀 Quick Reference Card - Phase 3 EDA Pipeline

## ⚡ 30-Second Start

```bash
pip install -r requirements.txt          # Install
python test_new_agents.py                # Test
streamlit run src/ui/app_v3.py          # Launch
```

---

## 🤖 The 6 Agents

| Agent | What It Does | Key Output |
|-------|--------------|------------|
| **ProfileAgent** | Dataset structure | Rows, columns, types, missing |
| **QualityAgent** | Data quality | Duplicates, outliers, issues |
| **TransformAgent** | Proposals | Transformations to apply |
| **VisualizationAgent** ✨ | Plots | 5 plot types, visual insights |
| **FeatureAgent** ✨ | Feature analysis | Correlations, engineering ideas |
| **StatAgent** ✨ | Statistics | Normality, hypothesis tests |

---

## 💻 Code Snippets

### Run Single Agent
```python
from src.data.dataset_handle import DatasetHandle
from src.agents import VisualizationAgent

handle = DatasetHandle("data.csv")
viz = VisualizationAgent()
result = viz.analyze(handle)

print(f"Generated {result['result']['total_plots']} plots")
print(result['recommendations'])
```

### Run All Agents
```python
from src.agents import *

handle = DatasetHandle("data.csv")

# Sequential execution with context
profile = ProfileAgent().analyze(handle)
quality = QualityAgent().analyze(handle, {"profile_results": profile["result"]})
viz = VisualizationAgent().analyze(handle, {"profile_results": profile["result"]})
features = FeatureAgent().analyze(handle, {"profile_results": profile["result"]})
stats = StatAgent().analyze(handle, {"profile_results": profile["result"]})
transforms = TransformAgent().analyze(handle, {
    "profile_results": profile["result"],
    "quality_results": quality["result"]
})
```

---

## 🎨 UI Quick Guide

### Launch
```bash
streamlit run src/ui/app_v3.py
```

### Workflow Options
1. **🎯 Quick Analysis** - All 6 agents (1 click)
2. **📊 Individual Agent** - Select specific agent
3. **🔬 Deep Dive** - Comprehensive analysis
4. **🤖 ML Prep** - Optimized for ML

### Tabs
```
📊 Overview → 📈 Profile → ✅ Quality → 🎨 Visualizations
🔍 Features → 📉 Statistics → 🔧 Transformations
```

---

## 📊 Agent Output Structure

All agents return:
```python
{
    "result": {...},              # Agent-specific results
    "reasoning": "WHY...",        # Explanation
    "impact": "WHAT...",          # Implications
    "recommendations": [...],     # Next steps
    "confidence": 0.85            # Confidence score
}
```

---

## 🎯 Common Tasks

### Generate Visualizations
```python
viz_agent = VisualizationAgent()
result = viz_agent.analyze(dataset_handle)
# Check: data/artifacts/plots/
```

### Check Correlations
```python
feature_agent = FeatureAgent()
result = feature_agent.analyze(dataset_handle)
strong_corr = result['result']['correlations']['strong_correlations']
```

### Test Normality
```python
stat_agent = StatAgent()
result = stat_agent.analyze(dataset_handle)
normal_features = result['result']['normality_tests']['normal_features']
```

### Get Transform Proposals
```python
transform_agent = TransformAgent()
result = transform_agent.analyze(dataset_handle, context)
high_priority = [t for t in result['result']['transformations'] 
                 if t['priority'] == 'high']
```

---

## 📁 File Locations

```
src/agents/
├── viz_agent.py        ← VisualizationAgent
├── feature_agent.py    ← FeatureAgent
└── stat_agent.py       ← StatAgent

src/ui/
├── app.py              ← Phase 1 UI
├── app_v2.py           ← Phase 2 UI
└── app_v3.py           ← Phase 3 UI (use this!)

data/artifacts/plots/   ← Generated visualizations
test_new_agents.py      ← Test all new agents
```

---

## 🐛 Quick Troubleshooting

| Issue | Fix |
|-------|-----|
| Import error | `pip install -r requirements.txt` |
| No plots | Check `data/artifacts/plots/` exists |
| Agent slow | Normal for large datasets (uses sampling) |
| UI not loading | `streamlit run src/ui/app_v3.py` |
| Memory error | Automatic DuckDB for large files |

---

## 📚 Documentation

- `QUICKSTART_PHASE3.md` - Start here
- `PHASE3_AGENTS_SUMMARY.md` - Technical details
- `UI_GUIDE_PHASE3.md` - UI walkthrough
- `INSTALLATION_PHASE3.md` - Setup help
- `COMPLETE_IMPLEMENTATION_SUMMARY.md` - Everything

---

## 🎯 Best Practices

1. **Run ProfileAgent first** - Establishes baseline
2. **Use context** - Pass previous results to later agents
3. **Check confidence** - Higher = more reliable
4. **Review plots** - Visual insights are powerful
5. **Read recommendations** - Actionable next steps

---

## ⚙️ Configuration

### Visualization Settings
```python
# In viz_agent.py
sample_size = min(10000, dataset_handle.shape[0])
dpi = 100
```

### Feature Analysis Settings
```python
# In feature_agent.py
strong_correlation = 0.7
moderate_correlation = 0.4
```

### Statistical Settings
```python
# In stat_agent.py
sample_size = min(5000, dataset_handle.shape[0])
alpha = 0.05
```

---

## 📊 Performance

| Agent | Typical Time | Sample Size |
|-------|--------------|-------------|
| VisualizationAgent | 5-10s | 10,000 rows |
| FeatureAgent | 3-5s | 10,000 rows |
| StatAgent | 5-8s | 5,000 rows |
| **All 3 New** | **13-23s** | **Auto-sampled** |

---

## 🎉 Quick Wins

### 1-Minute Win
```bash
python test_new_agents.py
# See all agents in action
```

### 5-Minute Win
```bash
streamlit run src/ui/app_v3.py
# Upload CSV, click "Quick Analysis"
```

### 10-Minute Win
```python
# Custom analysis in code
from src.agents import *
handle = DatasetHandle("your_data.csv")
result = VisualizationAgent().analyze(handle)
# Review plots in data/artifacts/plots/
```

---

## 🚀 Next Steps

1. ✅ Read `QUICKSTART_PHASE3.md`
2. ✅ Run `test_new_agents.py`
3. ✅ Launch `app_v3.py`
4. ✅ Upload your data
5. ✅ Explore results

---

## 💡 Pro Tips

- 🎯 Use "Quick Analysis" for first-time datasets
- 📊 Individual agents for specific checks
- 🎨 Visualizations tab shows all plots inline
- 🔍 Feature tab for ML preparation
- 📈 Statistics tab for assumptions validation

---

**You're ready to analyze! 🚀**

```bash
streamlit run src/ui/app_v3.py
```
