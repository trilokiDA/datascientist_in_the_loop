# Quality Visualization Enhancement

## Overview

The Quality Visualization component transforms text-based quality reports into interactive, visual dashboards that make data quality issues immediately apparent and actionable. This addresses the critical UX issue where users had to read through lengthy text output to understand data quality problems.

## Features

### 1. **Overall Quality Dashboard**
A comprehensive 4-panel dashboard showing:
- **Duplicate Status**: Gauge chart showing duplicate row percentage
- **Outlier Severity**: Count of columns with outliers
- **Data Type Issues**: Count of type inconsistencies
- **Overall Quality Score**: Calculated score (0-100) based on all quality metrics

### 2. **Missing Values Analysis**

#### Interactive Bar Chart
- Shows missing value percentage for each column
- Color-coded severity:
  - 🟢 Green: < 20% missing (low severity)
  - 🟡 Orange: 20-40% missing (medium severity)
  - 🔴 Red: > 40% missing (high severity)
- Hover tooltips show exact counts and percentages
- Limited to top 20 columns for readability

#### Missing Value Heatmap
- Visual pattern detection across rows and columns
- Binary color scale: Green (present) → Red (missing)
- Interactive hover showing row/column coordinates
- Helps identify systematic missing patterns
- Samples first 1000 rows for performance

### 3. **Outlier Analysis**

#### Box Plots
- Distribution visualization for top 6 columns with outliers
- Shows median, quartiles, min/max, and outliers
- Displays mean and standard deviation
- Interactive tooltips with exact values
- Multi-panel layout for easy comparison

#### Scatter Plot with Outlier Highlighting
- 2D scatter plot of top 2 columns with outliers
- Normal points in green
- Outliers marked with red X symbols
- Z-score based detection (threshold: 3)
- Interactive hover for coordinates

### 4. **Duplicate Analysis**

#### Gauge Chart
- Visual representation of duplicate percentage
- Color-coded zones:
  - Light Green: 0-5% (acceptable)
  - Light Yellow: 5-15% (moderate concern)
  - Light Red: 15-100% (high concern)
- Reference threshold at 10%
- Shows delta from reference

### 5. **Data Type Consistency**

#### Bar Chart
- Shows count of inconsistent values per column
- Color scale indicating severity
- Hover tooltips with percentages
- Identifies mixed type columns (e.g., numeric strings in text columns)

### 6. **Value Range Visualization**

#### Range Bar Chart
- Shows numeric ranges for top 10 columns
- Displays min, max, and range
- Helps identify unusual value distributions
- Sorted by range size

## Architecture

### File Structure

```
src/ui/components/
└── quality_viz.py
    ├── QualityVisualizer       # Main visualization class
    └── display_quality_visualizations()  # Streamlit integration function
```

### Core Classes

**QualityVisualizer**
```python
class QualityVisualizer:
    def __init__(self):
        self.artifacts_dir = Path("data/artifacts/quality_viz")
    
    # Main visualization methods
    def create_missing_value_heatmap(df, missing_info) -> go.Figure
    def create_missing_value_bar_chart(missing_info) -> go.Figure
    def create_outlier_box_plots(df, outlier_details) -> go.Figure
    def create_outlier_scatter_plot(df, outlier_details) -> go.Figure
    def create_duplicate_visualization(duplicate_info) -> go.Figure
    def create_data_type_consistency_chart(data_type_issues) -> go.Figure
    def create_value_range_chart(value_ranges) -> go.Figure
    def create_quality_summary_dashboard(quality_results) -> go.Figure
    
    # Helper methods
    def _calculate_quality_score(quality_results) -> float
```

### Technology Stack

- **Plotly**: Interactive charts (go.Figure, px, subplots)
- **Streamlit**: UI integration
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations
- **Matplotlib/Seaborn**: Fallback static plots (future use)

## Integration

### 1. Import Components

```python
from src.ui.components import (
    QualityVisualizer,
    display_quality_visualizations
)
```

### 2. In Quality Results Display

```python
def display_quality_results():
    st.header("✅ Data Quality Assessment")
    
    result = st.session_state.analysis_results["quality"]
    
    # Show key metrics
    display_metrics(result)
    
    # Add interactive visualizations
    try:
        display_quality_visualizations(result, st.session_state.dataset_handle)
    except Exception as e:
        st.warning(f"Could not generate visualizations: {str(e)}")
        # Fallback to text-based display
        display_text_report(result)
```

### 3. Standalone Usage

```python
from src.ui.components import QualityVisualizer

# Initialize visualizer
viz = QualityVisualizer()

# Create specific visualizations
missing_fig = viz.create_missing_value_bar_chart(missing_info)
outlier_fig = viz.create_outlier_box_plots(df, outlier_details)

# Display in Streamlit
st.plotly_chart(missing_fig, use_container_width=True)
st.plotly_chart(outlier_fig, use_container_width=True)
```

## Data Requirements

### Input Format

The `display_quality_visualizations()` function expects:

```python
quality_results = {
    'result': {
        'duplicates': {
            'duplicate_percentage': float,
            'duplicate_rows': int,
            'has_duplicates': bool
        },
        'outliers': {
            'columns_with_outliers': int,
            'has_outliers': bool,
            'outlier_details': {
                'column_name': {
                    'iqr_outliers': int,
                    'iqr_percentage': float,
                    'z_score_outliers': int,
                    'lower_bound': float,
                    'upper_bound': float,
                    'min': float,
                    'max': float
                }
            }
        },
        'inconsistencies': {
            'inconsistency_count': int,
            'type_mismatches': []
        },
        'data_types': {
            'type_issue_count': int,
            'issues': []
        }
    }
}
```

### Dataset Handle

The function also requires a `DatasetHandle` instance with:
- `.shape[0]`: Number of rows
- `.sample(n)`: Method to get n random rows as DataFrame

## Visualization Details

### Missing Value Heatmap

**Purpose**: Identify missing data patterns across rows and columns

**Implementation**:
```python
# Create binary matrix: 1 = missing, 0 = present
missing_matrix = df_sample.isnull().astype(int)

fig = go.Figure(data=go.Heatmap(
    z=missing_matrix.T.values,
    colorscale=[[0, '#10B981'], [1, '#EF4444']],  # Green to Red
    hovertemplate='Row: %{x}<br>Column: %{y}<br>Status: %{z}<extra></extra>'
))
```

**Best Practices**:
- Sample to max 1000 rows for performance
- Limit to top 20 columns with most missing values
- Transpose for better readability (columns on y-axis)

### Quality Score Calculation

The overall quality score is calculated as:

```python
def _calculate_quality_score(quality_results):
    score = 100.0
    
    # Penalize for duplicates (max 20 points)
    dup_pct = quality_results['duplicates']['duplicate_percentage']
    score -= min(dup_pct * 2, 20)
    
    # Penalize for outliers (max 30 points)
    outlier_count = len(quality_results['outliers']['outlier_details'])
    score -= min(outlier_count * 3, 30)
    
    # Penalize for inconsistencies (max 25 points)
    inconsistency_count = quality_results['inconsistencies']['inconsistency_count']
    score -= min(inconsistency_count * 5, 25)
    
    return max(0.0, score)
```

**Interpretation**:
- 80-100: Excellent data quality
- 60-80: Good, minor issues
- 40-60: Fair, needs attention
- 0-40: Poor, significant issues

## Usage Examples

### Example 1: Full Quality Dashboard

```python
import streamlit as st
from src.ui.components import display_quality_visualizations

# After running QualityAgent
quality_result = quality_agent.analyze(dataset_handle)

# Display all visualizations
display_quality_visualizations(
    quality_result,
    dataset_handle
)
```

### Example 2: Individual Visualizations

```python
from src.ui.components import QualityVisualizer

viz = QualityVisualizer()

# Missing values only
missing_info = {...}  # From analysis
fig = viz.create_missing_value_bar_chart(missing_info)
st.plotly_chart(fig)

# Outliers only
outlier_details = {...}  # From analysis
fig = viz.create_outlier_box_plots(df, outlier_details)
st.plotly_chart(fig)
```

### Example 3: Custom Dashboard

```python
viz = QualityVisualizer()

col1, col2 = st.columns(2)

with col1:
    # Duplicates
    dup_fig = viz.create_duplicate_visualization(duplicate_info)
    st.plotly_chart(dup_fig)

with col2:
    # Quality score
    dashboard_fig = viz.create_quality_summary_dashboard(quality_results)
    st.plotly_chart(dashboard_fig)
```

## Customization

### Color Schemes

Modify colors in visualization methods:

```python
# Severity color mapping
colors = {
    'low': '#10B981',      # Green
    'medium': '#F59E0B',   # Orange
    'high': '#EF4444'      # Red
}

# Update in specific visualizations
def create_missing_value_bar_chart(self, missing_info):
    colors = [
        colors['high'] if d['percentage'] > 40 else
        colors['medium'] if d['percentage'] > 20 else
        colors['low']
        for d in missing_data
    ]
```

### Chart Dimensions

Adjust height/width in layout updates:

```python
fig.update_layout(
    height=max(400, len(items) * 30),  # Dynamic based on data
    width=700,
    title="Chart Title"
)
```

### Sample Sizes

Modify sample sizes for performance:

```python
# In display_quality_visualizations()
sample_size = min(5000, dataset_handle.shape[0])  # Reduce for large datasets

# In heatmap creation
MAX_ROWS_HEATMAP = 500  # Reduce for better performance
```

## Performance Considerations

### Optimization Strategies

1. **Data Sampling**
   - Heatmap: Max 1000 rows
   - Charts: Max 10,000 rows
   - Adjustable based on dataset size

2. **Limiting Visualizations**
   - Missing values: Top 20 columns
   - Outliers: Top 6 columns
   - Value ranges: Top 10 columns

3. **Lazy Loading**
   - Visualizations generated on-demand
   - Not pre-computed during quality check

4. **Caching** (Future Enhancement)
   ```python
   @st.cache_data
   def create_visualization(data):
       # Expensive visualization logic
       pass
   ```

### Memory Management

- Use `.sample()` instead of loading full dataset
- Clear figures after display: `plt.close()`
- Limit Plotly data points to < 10K per chart

## Error Handling

### Graceful Degradation

```python
try:
    display_quality_visualizations(result, dataset_handle)
except Exception as e:
    st.warning(f"Could not generate visualizations: {str(e)}")
    # Fall back to text-based display
    display_text_report(result)
```

### Common Issues

1. **Missing Data Keys**
   - Solution: Provide default empty dicts
   - Check for key existence before accessing

2. **Empty DataFrames**
   - Solution: Return `None` from viz methods
   - Check before displaying

3. **Type Mismatches**
   - Solution: Explicit type conversions
   - Use `.astype()` where needed

## Benefits

### User Experience
- **Visual Clarity**: Issues visible at a glance
- **Pattern Recognition**: Heatmaps reveal systematic problems
- **Interactivity**: Hover tooltips provide details
- **Prioritization**: Color coding shows severity

### Data Quality Understanding
- **Holistic View**: Dashboard shows overall health
- **Drill-Down**: Detailed charts for each issue type
- **Comparative**: Multiple columns side-by-side
- **Quantified**: Exact numbers alongside visuals

### Decision Making
- **Actionable**: Clear what needs fixing
- **Prioritized**: Severity-based ordering
- **Confident**: Visual confirmation of text reports
- **Shareable**: Export-ready charts

## Future Enhancements

### Planned Features

1. **Interactive Filtering**
   ```python
   selected_cols = st.multiselect("Filter columns", df.columns)
   filtered_viz = create_filtered_visualization(selected_cols)
   ```

2. **Export Functionality**
   ```python
   fig.write_html("quality_report.html")
   fig.write_image("quality_dashboard.png")
   ```

3. **Comparison Mode**
   - Before/after cleaning comparison
   - Side-by-side heatmaps
   - Delta metrics

4. **Custom Thresholds**
   ```python
   thresholds = {
       'missing_high': 40,
       'outlier_z_score': 3,
       'duplicate_acceptable': 5
   }
   ```

5. **Drill-Down Views**
   - Click on heatmap cell → show row details
   - Click on outlier → show surrounding values
   - Click on bar → show column preview

6. **Animated Transitions**
   - Smooth transitions when updating data
   - Progress animations during computation

7. **3D Visualizations**
   - 3D scatter plots for multi-dimensional outliers
   - 3D surface plots for correlation analysis

## Integration with Other Features

### Phase 1: Progress Tracker
- Show "Generating Visualizations..." step
- Update progress as each chart completes

### Phase 3: Before/After Comparison
- Side-by-side quality dashboards
- Delta visualizations showing improvements
- Highlight fixed issues

### Phase 4: Export Reports
- Include quality visualizations in PDF export
- HTML report with interactive charts
- JSON export with chart data

## Testing

### Manual Testing Checklist
- [ ] Test with dataset containing all issue types
- [ ] Test with dataset with no issues (all green)
- [ ] Test with very large dataset (performance)
- [ ] Test with missing data (graceful degradation)
- [ ] Test hover interactions on all charts
- [ ] Test responsive layout on different screen sizes
- [ ] Test with extreme values (all duplicates, all outliers)

### Edge Cases
- Empty dataset
- Single column dataset
- All values missing
- No numeric columns (for outliers)
- 100% duplicates
- Very high cardinality (millions of unique values)

## Best Practices

### When to Use
✅ After QualityAgent completes
✅ When user requests "show quality issues"
✅ Before presenting transformation proposals
✅ In comparison mode (before/after)

### When NOT to Use
❌ During profiling (too early)
❌ On streaming data (use summary stats instead)
❌ With PII data (without anonymization)
❌ On extremely large datasets without sampling

### Performance Tips
- Always sample data before visualization
- Limit number of charts displayed
- Use caching for repeated visualizations
- Lazy-load charts in expanders
- Compress images if exporting

## Credits

- **Chart Library**: Plotly (plotly.com)
- **Color Palette**: Tailwind CSS colors
- **Design Inspiration**: Tableau, Power BI dashboards
- **Built with**: Streamlit, Python 3.10+

## Support

For issues or questions:
1. Check this documentation
2. Review `src/ui/components/quality_viz.py` source
3. See example usage in `src/ui/app_v3.py` → `display_quality_results()`
4. Raise issue in project repository

---

**Status**: ✅ Implemented in Phase 2 Enhancement  
**Version**: 1.0  
**Last Updated**: 2026-07-18  
**Dependencies**: plotly, streamlit, pandas, numpy
