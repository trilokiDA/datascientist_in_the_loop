# Before/After Transformation Comparison

## Overview

The Before/After Comparison component provides transparent, visual feedback on data transformations before they're permanently applied. This addresses the critical trust gap where users couldn't see the exact impact of proposed changes to their data.

## Features

### 1. **Side-by-Side Data Preview**
- Left panel: Original data
- Right panel: Transformed data
- Color-coded highlighting:
  - 🟢 **Green**: Missing values filled
  - 🔵 **Blue**: Values changed
  - ⚪ **White**: Unchanged
- Scrollable preview (default 15 rows)
- Column selector for focused comparison

### 2. **Delta Metrics Dashboard**
- Before vs After bar charts for:
  - **Missing Values**: Count reduction
  - **Duplicates**: Rows removed
  - **Total Data Points**: Overall size change
  - **Outliers**: Outlier count reduction
- Color-coded (Red=Before, Green=After)
- Interactive hover tooltips

### 3. **Distribution Comparison Charts**

#### Numeric Columns
- Overlaid histograms (Before=Red, After=Green)
- Shows distribution shifts
- Identifies skewness changes

#### Categorical Columns
- Grouped bar charts
- Top 10 value frequencies
- Shows category balance changes

### 4. **Statistical Summary Table**
- Comparison of key statistics:
  - Mean, Median, Standard Deviation
  - Absolute change
  - Percentage change
- Color-coded for significant changes:
  - 🔴 Red: > 10% change
  - 🟡 Yellow: 5-10% change
  - ⚪ White: < 5% change

### 5. **Impact Analysis**
- Automated impact assessment
- Categorized by severity (high/medium/low)
- Natural language descriptions:
  - "Filled 234 missing values"
  - "Removed 15 duplicate rows"
  - "Modified 1,234 values in 'age' column (12.3%)"

### 6. **Quick Action Buttons**
- **Preview All High Priority**: Apply all high-priority transformations
- **Preview Selected**: Apply custom selection
- **Reset**: Clear preview and start over
- Individual **👁️ Preview** buttons per transformation

## Architecture

### File Structure

```
src/ui/components/
└── comparison_view.py
    ├── ComparisonView               # Main comparison class
    ├── TransformationComparison     # Data class for metrics
    └── display_transformation_comparison()  # Streamlit integration
```

### Core Classes

**ComparisonView**
```python
class ComparisonView:
    # Visual comparison methods
    def create_side_by_side_preview(df_before, df_after, columns, max_rows)
    def create_delta_metrics(df_before, df_after) -> go.Figure
    def create_column_distribution_comparison(df_before, df_after, column) -> go.Figure
    def create_statistical_comparison_table(df_before, df_after, columns) -> pd.DataFrame
    def create_impact_summary(df_before, df_after, description) -> Dict
```

**TransformationComparison** (Data Class)
```python
@dataclass
class TransformationComparison:
    transformation_id: str
    transformation_type: str
    column: str
    before_stats: Dict[str, Any]
    after_stats: Dict[str, Any]
    rows_affected: int
    impact_score: float  # 0-1 scale
```

### Technology Stack

- **Plotly**: Interactive comparison charts
- **Pandas**: Data transformation preview
- **Streamlit**: UI rendering with styled dataframes
- **NumPy**: Statistical calculations

## Integration

### 1. Import Components

```python
from src.ui.components import (
    ComparisonView,
    TransformationComparison,
    display_transformation_comparison
)
```

### 2. In Transform Results Display

```python
def display_transform_results():
    # Show transformation proposals
    for transform in transformations:
        st.expander(transform['description'])
        
        # Add preview button
        if st.button("👁️ Preview", key=f"preview_{transform['id']}"):
            # Apply transformation to create preview
            df_before = dataset.sample(1000)
            df_after = apply_transformation(df_before, transform)
            
            # Display comparison
            display_transformation_comparison(
                df_before,
                df_after,
                transformation_info={'description': transform['description']},
                show_details=True
            )
```

### 3. Standalone Usage

```python
from src.ui.components import ComparisonView

# Create comparison view
comparator = ComparisonView()

# Generate side-by-side preview
comparator.create_side_by_side_preview(
    df_before,
    df_after,
    columns=['age', 'salary', 'score'],
    max_rows=20
)

# Show delta metrics
fig = comparator.create_delta_metrics(df_before, df_after)
st.plotly_chart(fig)

# Distribution comparison for specific column
fig = comparator.create_column_distribution_comparison(
    df_before, df_after, 'age'
)
st.plotly_chart(fig)
```

## Transformation Types Supported

### 1. **Deduplication**
```python
# Before/After shows:
- Exact rows removed
- Impact on dataset size
- Distribution preservation
```

### 2. **Missing Value Handling**

**Strategies Visualized:**
- **Impute Median**: Shows distribution shift
- **Impute Mode**: Shows category frequency changes
- **Impute Constant**: Highlights filled cells
- **Drop Column**: Shows removed column

### 3. **Outlier Handling**

**Strategies Visualized:**
- **Capping**: Shows clipped values in distribution
- **Removal**: Shows reduced dataset size
- **Winsorization**: Shows bounded extremes

### 4. **Encoding**
```python
# Shows:
- Original categorical values
- Encoded numeric values
- Mapping table
```

### 5. **Scaling**
```python
# Shows:
- Original value ranges
- Scaled value ranges
- Distribution shape preservation
```

## Usage Examples

### Example 1: Preview Single Transformation

```python
# User clicks "Preview" on a missing value imputation
transform = {
    'type': 'missing_value_handling',
    'params': {
        'column': 'age',
        'strategy': 'impute_median'
    },
    'description': 'Fill missing ages with median (35.2)'
}

# Apply transformation
df_before = dataset.sample(1000)
df_after = df_before.copy()
median_age = df_before['age'].median()
df_after['age'] = df_after['age'].fillna(median_age)

# Show comparison
display_transformation_comparison(
    df_before,
    df_after,
    {'description': f"Filled missing ages with median ({median_age:.1f})"}
)
```

### Example 2: Preview Multiple Transformations

```python
# User clicks "Preview All High Priority"
high_priority_transforms = [
    {'type': 'deduplication', ...},
    {'type': 'missing_value_handling', ...},
    {'type': 'outlier_handling', ...}
]

df_before = dataset.sample(1000)
df_after = df_before.copy()

# Apply all transformations sequentially
for transform in high_priority_transforms:
    df_after = apply_transformation(df_after, transform)

# Show comprehensive comparison
display_transformation_comparison(
    df_before,
    df_after,
    {'description': f"Applied {len(high_priority_transforms)} transformations"}
)
```

### Example 3: Custom Comparison

```python
comparator = ComparisonView()

# Tab-based comparison
tab1, tab2, tab3 = st.tabs(["Preview", "Metrics", "Stats"])

with tab1:
    comparator.create_side_by_side_preview(df_before, df_after)

with tab2:
    fig = comparator.create_delta_metrics(df_before, df_after)
    st.plotly_chart(fig)

with tab3:
    stats_df = comparator.create_statistical_comparison_table(
        df_before, df_after
    )
    st.dataframe(stats_df)
```

## Comparison Metrics

### Automatic Calculations

The system automatically computes:

1. **Row-level Changes**
   ```python
   rows_added = len(df_after) - len(df_before)
   rows_removed = abs(min(0, rows_added))
   ```

2. **Missing Value Changes**
   ```python
   missing_before = df_before.isnull().sum().sum()
   missing_after = df_after.isnull().sum().sum()
   missing_filled = missing_before - missing_after
   ```

3. **Duplicate Changes**
   ```python
   dup_before = df_before.duplicated().sum()
   dup_after = df_after.duplicated().sum()
   dup_removed = dup_before - dup_after
   ```

4. **Outlier Changes**
   ```python
   outliers_before = count_outliers(df_before)
   outliers_after = count_outliers(df_after)
   outliers_handled = outliers_before - outliers_after
   ```

5. **Statistical Shifts**
   ```python
   mean_change = df_after[col].mean() - df_before[col].mean()
   median_change = df_after[col].median() - df_before[col].median()
   std_change = df_after[col].std() - df_before[col].std()
   ```

### Impact Scoring

Each transformation gets an impact score (0-1):

```python
def calculate_impact_score(df_before, df_after):
    score = 0.0
    
    # Row changes (0-0.3)
    row_change_pct = abs(len(df_after) - len(df_before)) / len(df_before)
    score += min(0.3, row_change_pct)
    
    # Missing value reduction (0-0.3)
    missing_reduction = (
        df_before.isnull().sum().sum() - df_after.isnull().sum().sum()
    ) / df_before.isnull().sum().sum()
    score += min(0.3, missing_reduction)
    
    # Statistical changes (0-0.4)
    numeric_cols = df_before.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        mean_change = abs(
            df_after[col].mean() - df_before[col].mean()
        ) / df_before[col].mean()
        score += min(0.1, mean_change)
    
    return min(1.0, score)
```

**Interpretation:**
- **0.0-0.2**: Low impact (minor tweaks)
- **0.2-0.5**: Medium impact (noticeable changes)
- **0.5-0.8**: High impact (significant transformation)
- **0.8-1.0**: Very high impact (major restructuring)

## Cell Highlighting Logic

### Side-by-Side Preview Highlighting

```python
def highlight_changes(row):
    styles = []
    for col in row.index:
        before_val = df_before.iloc[row.name][col]
        after_val = row[col]
        
        # Missing value filled
        if pd.isna(before_val) and not pd.isna(after_val):
            styles.append('background-color: #D1FAE5')  # Green
        
        # Value became missing
        elif not pd.isna(before_val) and pd.isna(after_val):
            styles.append('background-color: #FEE2E2')  # Red
        
        # Value changed
        elif before_val != after_val:
            styles.append('background-color: #DBEAFE')  # Blue
        
        # Unchanged
        else:
            styles.append('')
    
    return styles
```

## Customization

### Adjust Colors

```python
# Modify highlighting colors
COLORS = {
    'filled': '#D1FAE5',      # Green for filled missing
    'changed': '#DBEAFE',     # Blue for changed values
    'removed': '#FEE2E2',     # Red for removed values
    'unchanged': 'white'      # White for unchanged
}
```

### Adjust Preview Size

```python
# Show more/fewer rows
comparator.create_side_by_side_preview(
    df_before,
    df_after,
    max_rows=25  # Default is 10
)
```

### Custom Tabs

```python
# Add custom comparison views
tabs = st.tabs([
    "📋 Preview",
    "📊 Metrics",
    "📈 Distributions",
    "📉 Statistics",
    "🔍 Custom Analysis"  # Your custom tab
])

with tabs[4]:
    # Your custom comparison logic
    st.write("Custom analysis here")
```

## Performance Considerations

### Sampling Strategy

```python
# For large datasets, sample intelligently
SAMPLE_SIZE = 1000  # Preview sample size

if len(dataset) > SAMPLE_SIZE:
    # Stratified sampling if target column exists
    if 'target' in dataset.columns:
        df_sample = dataset.groupby('target').sample(
            n=SAMPLE_SIZE // dataset['target'].nunique(),
            random_state=42
        )
    else:
        df_sample = dataset.sample(n=SAMPLE_SIZE, random_state=42)
else:
    df_sample = dataset.copy()
```

### Lazy Computation

```python
# Only compute comparisons when tabs are opened
with tab1:
    if st.session_state.get('tab1_active'):
        # Heavy computation
        fig = create_comparison_chart()
        st.plotly_chart(fig)
```

### Caching

```python
@st.cache_data
def compute_delta_metrics(df_before_hash, df_after_hash):
    # Expensive metric calculation
    return metrics

# Use with dataframe hashes
metrics = compute_delta_metrics(
    hash(df_before.to_json()),
    hash(df_after.to_json())
)
```

## Error Handling

### Graceful Degradation

```python
try:
    display_transformation_comparison(df_before, df_after, info)
except Exception as e:
    st.warning(f"Could not generate comparison: {str(e)}")
    
    # Fallback: simple text comparison
    st.subheader("Basic Comparison")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Before:", df_before.shape)
    
    with col2:
        st.write("After:", df_after.shape)
```

### Validation

```python
def validate_comparison(df_before, df_after):
    """Validate dataframes before comparison"""
    
    # Check if both are DataFrames
    if not isinstance(df_before, pd.DataFrame):
        raise ValueError("df_before must be a DataFrame")
    
    # Check if not empty
    if df_before.empty or df_after.empty:
        raise ValueError("DataFrames cannot be empty")
    
    # Warn if shapes are very different
    if abs(len(df_before) - len(df_after)) > len(df_before) * 0.5:
        st.warning("⚠️ Transformation removed >50% of rows")
    
    return True
```

## Benefits

### User Trust
- **Transparency**: See exactly what changes
- **Confidence**: No surprises after applying
- **Control**: Preview before committing
- **Understanding**: Visual > text explanations

### Data Quality
- **Validation**: Catch unintended side effects
- **Verification**: Confirm transformations work as expected
- **Refinement**: Adjust parameters based on preview
- **Rollback**: Easy to reset if preview doesn't look right

### Decision Making
- **Informed**: Make data-driven transformation choices
- **Comparative**: Weigh multiple transformation strategies
- **Prioritized**: See which changes matter most
- **Documented**: Preview serves as audit trail

## Future Enhancements

### Planned Features

1. **Diff View for Text Columns**
   ```python
   # Character-level diff highlighting
   show_text_diff(before_text, after_text, column='description')
   ```

2. **Interactive Rollback**
   ```python
   if st.button("⏪ Undo Last Transform"):
       df = rollback_to_checkpoint(checkpoint_id)
   ```

3. **Transformation History**
   ```python
   # Timeline of all previewed transformations
   show_transformation_timeline()
   ```

4. **Export Comparison Report**
   ```python
   comparison_report = generate_comparison_pdf(
       df_before, df_after, transformations
   )
   st.download_button("Download Report", comparison_report)
   ```

5. **A/B Testing Mode**
   ```python
   # Compare two different transformation strategies
   strategy_a_result = apply_strategy_a(df)
   strategy_b_result = apply_strategy_b(df)
   compare_strategies(strategy_a_result, strategy_b_result)
   ```

6. **Animated Transitions**
   ```python
   # Animated visualization showing transformation
   show_transformation_animation(df_before, df_after)
   ```

## Integration with Other Features

### Phase 1: Progress Tracker
- Show "Generating Preview..." step
- Update progress as transformations apply

### Phase 2: Quality Visualizations
- Include quality score before/after
- Show quality dashboard comparison

### Phase 4: Export
- Include before/after in export report
- Side-by-side screenshots in PDF

## Testing

### Manual Testing Checklist
- [ ] Test with single transformation
- [ ] Test with multiple transformations
- [ ] Test with missing value imputation
- [ ] Test with outlier capping
- [ ] Test with deduplication
- [ ] Test highlighting colors
- [ ] Test metric calculations
- [ ] Test distribution charts
- [ ] Test statistical table
- [ ] Test on large dataset (performance)

### Edge Cases
- Transformation removes all rows
- Transformation removes all columns
- All values change
- No values change
- Mixed type columns
- Very wide datasets (many columns)
- Very long datasets (many rows)

## Best Practices

### When to Show Comparison
✅ Before applying any destructive transformation  
✅ When user requests preview  
✅ For high-impact transformations (> 10% data change)  
✅ Before committing to database  

### When NOT to Show
❌ For trivial transformations (< 1% change)  
❌ During live streaming data  
❌ When performance is critical  

### UX Guidelines
- **Default to collapsed**: Don't overwhelm with data
- **Progressive disclosure**: Start with summary, expand for details
- **Clear actions**: Make "Apply" vs "Cancel" obvious
- **Reversible**: Always allow going back
- **Feedback**: Show success/failure clearly

## Credits

- **Design Pattern**: Git diff viewer inspiration
- **Color Scheme**: Tailwind CSS colors
- **Chart Library**: Plotly
- **Built with**: Streamlit, Pandas, Python 3.10+

## Support

For issues or questions:
1. Check this documentation
2. Review `src/ui/components/comparison_view.py` source
3. See example in `src/ui/app_v3.py` → `display_transform_results()`
4. Raise issue in project repository

---

**Status**: ✅ Implemented in Phase 3 Enhancement  
**Version**: 1.0  
**Last Updated**: 2026-07-18  
**Dependencies**: plotly, streamlit, pandas, numpy
