# Export Functionality Documentation

## Overview

The Export Functionality module provides comprehensive export capabilities for the EDA Pipeline analysis results. Users can export their analysis in multiple formats to share with stakeholders or for further processing.

## Supported Export Formats

### 1. HTML Report 📄
- **Purpose**: Interactive, shareable report with all visualizations and analysis
- **Features**:
  - Beautiful, professional formatting
  - Responsive design
  - Interactive Plotly charts (when available)
  - Table of contents for easy navigation
  - Comprehensive sections for each agent's results
  - Confidence scores and reasoning for explainability
  - Download or view in browser

### 2. JSON Data 📊
- **Purpose**: Raw analysis results for programmatic access
- **Features**:
  - Complete analysis results from all agents
  - Structured, hierarchical format
  - Includes metadata (timestamp, dataset info)
  - Easy to parse and integrate with other tools
  - Suitable for API consumption or further analysis

### 3. Transformed CSV 📋
- **Purpose**: Export the cleaned/transformed dataset
- **Features**:
  - Includes all transformations applied by TransformAgent
  - Standard CSV format
  - Ready for use in other tools or workflows
  - Only available after running TransformAgent

## Using Export Functionality

### In Streamlit UI

1. **Run Analysis**: Complete at least one agent analysis
2. **Navigate to Export Tab**: Click on the "💾 Export" tab
3. **Select Formats**: Choose which formats you want to export
   - HTML Report (default)
   - JSON Data (default)
   - Transformed CSV (requires TransformAgent)
4. **Optional Custom Name**: Provide a custom prefix for exported files
5. **Export**: Click "🚀 Export Now" button
6. **Download**: Download files directly or view in exports list

### Programmatically

```python
from src.utils.export import ExportManager

# Initialize export manager
manager = ExportManager(output_dir="data/exports")

# Export all formats
exported_files = manager.export_all(
    analysis_results=your_analysis_results,
    dataset_info=your_dataset_info,
    formats=['html', 'json', 'csv'],
    session_id='my_analysis'
)

# Or export individual formats
html_path = manager.export_html(analysis_results, dataset_info, "report.html")
json_path = manager.export_json(analysis_results, dataset_info, "results.json")
```

### Quick Functions

```python
from src.utils.export import export_to_html, export_to_json

# Quick HTML export
html_path = export_to_html(analysis_results, dataset_info)

# Quick JSON export
json_path = export_to_json(analysis_results, dataset_info)
```

## File Naming Convention

Exported files follow this naming pattern:

```
[custom_prefix_]<type>_<timestamp>.<extension>

Examples:
- report_20260719_153336.html
- my_analysis_report_20260719_153336.html
- results_20260719_153336.json
- transformed_20260719_153336.csv
```

## HTML Report Structure

The HTML report includes the following sections:

1. **Header**
   - Report title
   - Generation timestamp
   - Dataset metadata (name, rows, columns)

2. **Table of Contents**
   - Quick navigation links to all sections

3. **Overview Section**
   - Completion status of all agents
   - Key dataset metrics
   - Agent status with confidence scores

4. **Agent-Specific Sections** (when available)
   - Dataset Profile (ProfileAgent)
   - Quality Assessment (QualityAgent)
   - Visualizations (VisualizationAgent)
   - Feature Analysis (FeatureAgent)
   - Statistical Analysis (StatAgent)
   - Transformations (TransformAgent)

5. **Each Agent Section Includes**:
   - Confidence score badge
   - Key metrics and findings
   - Visual representations (tables, metrics)
   - Reasoning (explainability)
   - Impact assessment
   - Recommendations

6. **Footer**
   - Generation credits
   - Technology stack

## JSON Export Structure

```json
{
  "metadata": {
    "export_timestamp": "2026-07-19T15:53:36.722873",
    "dataset_info": {
      "name": "dataset.csv",
      "rows": 1000,
      "columns": 10,
      "file_size_formatted": "50 KB"
    }
  },
  "analysis_results": {
    "profile": { ... },
    "quality": { ... },
    "visualization": { ... },
    "feature": { ... },
    "stat": { ... },
    "transform": { ... }
  }
}
```

## Storage Location

All exports are stored in:
```
data/exports/
```

Directory structure:
```
data/
  exports/
    ├── report_20260719_153336.html
    ├── results_20260719_153336.json
    ├── transformed_20260719_153336.csv
    └── ...
```

## Viewing Past Exports

In the Streamlit UI:

1. Navigate to "💾 Export" tab
2. Click "📂 View Exports" button
3. Browse past exports by type (HTML/JSON/CSV)
4. Download any previous export
5. See file metadata (size, modification time)

## Use Cases

### 1. Executive Reporting
- Export HTML report for stakeholders
- Professional, easy-to-read format
- No technical knowledge required

### 2. Data Science Workflows
- Export JSON for integration with ML pipelines
- Export CSV for further preprocessing
- Programmatic access to all metrics

### 3. Documentation
- Attach HTML reports to project documentation
- Share analysis results with team members
- Archive analysis snapshots

### 4. Compliance & Auditing
- Timestamped exports for audit trails
- Complete analysis history
- Reproducible results

## Best Practices

1. **Naming Conventions**: Use descriptive custom names for important analyses
   - Good: `customer_churn_analysis`
   - Bad: `test` or `abc`

2. **Format Selection**: Choose formats based on use case
   - Presentation → HTML
   - Integration → JSON
   - Further Analysis → CSV

3. **Storage Management**: Periodically clean up old exports
   - Keep important exports
   - Archive or delete test exports

4. **Security**: Be mindful of sensitive data
   - Exports contain full analysis results
   - Consider access controls for export directory
   - Don't share exports with sensitive information

## Technical Details

### Dependencies
- pandas: Data handling
- plotly: Interactive charts (for HTML)
- pathlib: File management
- json: JSON serialization
- datetime: Timestamp generation

### Performance
- HTML generation: ~1-2 seconds for typical datasets
- JSON export: <1 second
- CSV export: Depends on dataset size

### Limitations
- CSV export requires TransformAgent results
- Very large datasets may produce large HTML files
- Plotly charts in HTML require internet connection (CDN)

## Troubleshooting

### Export Button Disabled
- Ensure you've run at least one agent analysis

### Transformed CSV Not Available
- Run TransformAgent first
- Check that transformations were applied successfully

### HTML Report Not Loading
- Check internet connection (for Plotly CDN)
- Verify file permissions in export directory

### File Too Large
- Consider exporting only necessary formats
- For very large datasets, JSON/CSV may be more suitable than HTML

## Future Enhancements

Potential future additions:
- PDF export with ReportLab
- Excel export with multiple sheets
- Email delivery of reports
- Scheduled exports
- Cloud storage integration (S3, Google Drive)
- Custom report templates
- Comparison reports across multiple analyses

## API Reference

### ExportManager Class

```python
class ExportManager:
    def __init__(self, output_dir: str = "data/exports")
    
    def export_all(
        self,
        analysis_results: Dict[str, Any],
        dataset_info: Dict[str, Any],
        formats: List[str] = ['html', 'json'],
        session_id: Optional[str] = None
    ) -> Dict[str, str]
    
    def export_html(
        self,
        analysis_results: Dict[str, Any],
        dataset_info: Dict[str, Any],
        filename: str
    ) -> str
    
    def export_json(
        self,
        analysis_results: Dict[str, Any],
        dataset_info: Dict[str, Any],
        filename: str
    ) -> str
    
    def export_transformed_csv(
        self,
        transform_result: Dict[str, Any],
        filename: str
    ) -> Optional[str]
```

### Helper Functions

```python
def export_to_html(
    analysis_results: Dict[str, Any],
    dataset_info: Dict[str, Any],
    output_path: Optional[str] = None
) -> str

def export_to_json(
    analysis_results: Dict[str, Any],
    dataset_info: Dict[str, Any],
    output_path: Optional[str] = None
) -> str
```

## Examples

### Complete Workflow Example

```python
# 1. Run analysis
from src.data.dataset_handle import DatasetHandle
from src.agents import ProfileAgent, QualityAgent, TransformAgent

handle = DatasetHandle("data.csv")

# Run agents
profile_agent = ProfileAgent()
quality_agent = QualityAgent()
transform_agent = TransformAgent()

analysis_results = {
    'profile': profile_agent.analyze(handle),
    'quality': quality_agent.analyze(handle, {}),
    'transform': transform_agent.analyze(handle, {})
}

# 2. Prepare dataset info
dataset_info = handle.get_info()

# 3. Export
from src.utils.export import ExportManager

manager = ExportManager()
exported = manager.export_all(
    analysis_results,
    dataset_info,
    formats=['html', 'json', 'csv'],
    session_id='production_analysis'
)

print("Exported files:")
for format_type, path in exported.items():
    print(f"  {format_type}: {path}")
```

## Conclusion

The Export Functionality provides a robust, flexible system for sharing and preserving analysis results. Whether you need a professional report for stakeholders, structured data for integration, or transformed datasets for downstream processing, the export module has you covered.
