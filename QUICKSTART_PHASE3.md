# Quick Start Guide - Phase 3 New Agents

## 🚀 Get Started in 5 Minutes

### Step 1: Ensure Dependencies are Installed

```bash
pip install -r requirements.txt
```

All necessary dependencies are already in requirements.txt:
- matplotlib, seaborn, plotly (for visualizations)
- scipy, statsmodels (for statistical tests)
- scikit-learn (for feature analysis)

### Step 2: Test the New Agents

Run the comprehensive test suite:

```bash
python test_new_agents.py
```

This will:
- ✅ Create a test dataset with interesting characteristics
- ✅ Test VisualizationAgent (generates plots)
- ✅ Test FeatureAgent (analyzes correlations and engineering opportunities)
- ✅ Test StatAgent (performs statistical validation)
- ✅ Display results and summaries

**Expected Output:**
```
============================================================
NEW AGENTS TEST SUITE
============================================================

Creating test dataset...
Test dataset created: data/uploads/test_dataset_enhanced.csv
Shape: (1000, 10)

Testing VisualizationAgent...
Total Plots Generated: 12
Plot Summary:
  - distribution: 6
  - correlation_heatmap: 1
  - box_plot: 3
  - categorical_bar: 2

Testing FeatureAgent...
Feature Analysis Summary:
  Total Features: 10
  Strong Correlations: 2
  Engineering Suggestions: 8

Testing StatAgent...
Statistical Analysis Summary:
  Normality Tests: 8 features tested
  Hypothesis Tests: 3 tests performed

ALL TESTS COMPLETED SUCCESSFULLY!
```

### Step 3: Review Generated Artifacts

Check the generated visualizations:

```bash
ls data/artifacts/plots/
```

You'll see files like:
- `viz_abc123_dist_age.png` - Distribution plots
- `viz_abc123_correlation_heatmap.png` - Correlation heatmap
- `viz_abc123_boxplot_score.png` - Outlier box plots
- `viz_abc123_categorical_region.png` - Categorical distributions
- `viz_abc123_missing_heatmap.png` - Missing value patterns

### Step 4: Use in Your Code

#### Example 1: Quick Analysis

```python
from src.data.dataset_handle import DatasetHandle
from src.agents import VisualizationAgent, FeatureAgent, StatAgent

# Load your dataset
handle = DatasetHandle("path/to/your/data.csv")

# Run visualization analysis
viz_agent = VisualizationAgent()
viz_results = viz_agent.analyze(handle)

print(f"Generated {viz_results['result']['total_plots']} plots")
print(f"Recommendations: {viz_results['recommendations']}")

# Run feature analysis
feature_agent = FeatureAgent()
feature_results = feature_agent.analyze(handle)

print(f"Found {len(feature_results['result']['correlations']['strong_correlations'])} strong correlations")
print(f"Engineering suggestions: {feature_results['result']['engineering_suggestions']['total_suggestions']}")

# Run statistical analysis
stat_agent = StatAgent()
stat_results = stat_agent.analyze(handle)

print(f"Normal features: {stat_results['result']['normality_tests']['normal_features']}")
print(f"Hypothesis tests: {stat_results['result']['hypothesis_tests']['total_tests']}")
```

#### Example 2: Integrated Pipeline

```python
from src.data.dataset_handle import DatasetHandle
from src.agents import (
    ProfileAgent, QualityAgent, VisualizationAgent,
    FeatureAgent, StatAgent, TransformAgent
)

# Load dataset
handle = DatasetHandle("data/uploads/dataset.csv")

# Step 1: Profile
profile_agent = ProfileAgent()
profile = profile_agent.analyze(handle)
print(f"📊 Profile: {profile['result']['basic_info']}")

# Step 2: Quality Check
quality_agent = QualityAgent()
quality = quality_agent.analyze(handle, {
    "profile_results": profile["result"]
})
print(f"✅ Quality: {quality['result']['duplicates']}")

# Step 3: Visualizations
viz_agent = VisualizationAgent()
viz = viz_agent.analyze(handle, {
    "profile_results": profile["result"],
    "quality_results": quality["result"]
})
print(f"📈 Visualizations: {viz['result']['total_plots']} plots")

# Step 4: Feature Analysis
feature_agent = FeatureAgent()
features = feature_agent.analyze(handle, {
    "profile_results": profile["result"]
})
print(f"🔍 Features: {features['result']['correlations']['summary']}")

# Step 5: Statistical Validation
stat_agent = StatAgent()
stats = stat_agent.analyze(handle, {
    "profile_results": profile["result"],
    "feature_results": features["result"]
})
print(f"📊 Statistics: {stats['result']['normality_tests']['summary']}")

# Step 6: Transformation Proposals
transform_agent = TransformAgent()
transforms = transform_agent.analyze(handle, {
    "profile_results": profile["result"],
    "quality_results": quality["result"]
})
print(f"🔧 Transforms: {transforms['result']['total_transformations']} proposed")
```

### Step 5: Understanding Agent Output

All agents return a standardized `AgentResponse` with:

```python
{
    "result": {
        # Detailed analysis results (agent-specific)
    },
    "reasoning": "WHY the analysis was performed and methodology used",
    "impact": "WHAT the findings mean for the dataset and analysis",
    "recommendations": [
        "Specific action 1",
        "Specific action 2",
        "Specific action 3"
    ],
    "confidence": 0.85  # Confidence score (0-1)
}
```

---

## 🎯 Agent-Specific Quick References

### VisualizationAgent

**Purpose**: Generate plots and visual insights

**Key Results:**
- `total_plots`: Number of plots generated
- `plots`: List of plot objects with paths
- `summary`: Breakdown by plot type

**Plot Types:**
- Distribution (histogram + box plot)
- Correlation heatmap
- Box plots for outliers
- Categorical bar charts
- Missing value heatmap

**Access Plots:**
```python
result = viz_agent.analyze(handle)
for plot in result['result']['plots']:
    print(f"{plot['type']}: {plot['path']}")
```

---

### FeatureAgent

**Purpose**: Analyze relationships and suggest engineering

**Key Results:**
- `correlations`: Strong and moderate correlations
- `multicollinearity`: VIF-based detection
- `feature_importance_hints`: Variance-based hints
- `feature_interactions`: Suggested new features
- `engineering_suggestions`: Transformations to apply

**Common Use Cases:**
```python
result = feature_agent.analyze(handle)

# Check for multicollinearity
if result['result']['multicollinearity']['has_multicollinearity']:
    pairs = result['result']['multicollinearity']['multicollinear_pairs']
    print(f"Remove one from each pair: {pairs}")

# Get engineering suggestions
suggestions = result['result']['engineering_suggestions']['suggestions']
high_priority = [s for s in suggestions if s['priority'] == 'high']
print(f"High priority transformations: {len(high_priority)}")
```

---

### StatAgent

**Purpose**: Statistical validation and hypothesis testing

**Key Results:**
- `normality_tests`: Shapiro-Wilk, D'Agostino tests
- `distribution_analysis`: Skewness, kurtosis, moments
- `hypothesis_tests`: Correlation, independence, ANOVA tests
- `outlier_statistics`: Multiple detection methods

**Common Use Cases:**
```python
result = stat_agent.analyze(handle)

# Check normality for modeling
normal_features = result['result']['normality_tests']['normal_features']
print(f"Can use parametric methods for {normal_features} features")

# Review hypothesis tests
for test in result['result']['hypothesis_tests']['tests']:
    print(f"{test['test_type']}: {test['interpretation']}")

# Assess outlier severity
for stat in result['result']['outlier_statistics']['outlier_statistics']:
    if stat['severity'] == 'high':
        print(f"High outliers in {stat['feature']}: {stat['iqr_outliers']}")
```

---

## 🔧 Configuration

### Visualization Settings

Edit `src/agents/viz_agent.py`:
```python
# Sample size for visualization
sample_size = min(10000, dataset_handle.shape[0])

# Plot DPI
plt.savefig(plot_path, dpi=100, bbox_inches='tight')

# Number of plots
numeric_cols[:6]  # Top 6 numeric columns
categorical_cols[:4]  # Top 4 categorical
```

### Feature Analysis Settings

Edit `src/agents/feature_agent.py`:
```python
# Correlation thresholds
strong_correlation = 0.7  # |r| > 0.7
moderate_correlation = 0.4  # |r| > 0.4

# Multicollinearity threshold
multicollinear_threshold = 0.85

# Sample size
sample_size = min(10000, dataset_handle.shape[0])
```

### Statistical Analysis Settings

Edit `src/agents/stat_agent.py`:
```python
# Sample size (smaller for statistical tests)
sample_size = min(5000, dataset_handle.shape[0])

# Significance level
alpha = 0.05

# Outlier thresholds
iqr_multiplier = 1.5
z_threshold = 3
modified_z_threshold = 3.5
```

---

## 🐛 Troubleshooting

### Issue: "Module not found: matplotlib"

**Solution:**
```bash
pip install matplotlib seaborn plotly
```

### Issue: "No plots generated"

**Possible Causes:**
1. No numeric columns in dataset → Add numeric features
2. Sample size too small → Use larger dataset
3. Plotting backend issues → Try `matplotlib.use('Agg')`

**Debug:**
```python
result = viz_agent.analyze(handle)
print(f"Total plots: {result['result']['total_plots']}")
print(f"Plot types: {result['result']['summary']}")
```

### Issue: "Statistical tests failing"

**Possible Causes:**
1. Sample size too small (< 3 samples) → Use larger dataset
2. Constant features → Check for variance
3. All missing values → Handle missing data first

**Debug:**
```python
result = stat_agent.analyze(handle)
print(f"Sample size: {result['result']['sample_size']}")
print(f"Tests performed: {result['result']['hypothesis_tests']['total_tests']}")
```

### Issue: "Feature analysis returns empty"

**Possible Causes:**
1. Only 1 numeric column → Need at least 2 for correlations
2. All categorical columns → Feature analysis focuses on numeric
3. High cardinality everywhere → Check data types

**Debug:**
```python
result = feature_agent.analyze(handle)
print(f"Numeric features: {result['result']['correlations']['num_numeric_features']}")
```

---

## 📚 Learn More

- **Full Documentation**: See `PHASE3_AGENTS_SUMMARY.md`
- **Architecture**: See `ARCHITECTURE.md`
- **API Reference**: See docstrings in agent files
- **Examples**: See `test_new_agents.py`

---

## 🎉 Success Checklist

- [ ] Dependencies installed
- [ ] Test suite runs successfully
- [ ] Plots generated in `data/artifacts/plots/`
- [ ] Understand agent output structure
- [ ] Tried example code snippets
- [ ] Reviewed generated visualizations
- [ ] Read full documentation

**You're ready to use the enhanced EDA pipeline!** 🚀

---

## 🚀 Next Steps

1. **Integrate with UI**: Update Streamlit app to display new agent results
2. **Custom Workflows**: Create workflows using new agents
3. **Real Data**: Test on your actual datasets
4. **Customize**: Adjust thresholds and settings for your use case

**Happy Analyzing!** 📊✨
