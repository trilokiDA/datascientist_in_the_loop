# Export Functionality - Quick Start Guide

## 🚀 30-Second Quickstart

1. Run your analysis in Streamlit
2. Click **"💾 Export"** tab
3. Select your formats (HTML/JSON/CSV)
4. Click **"🚀 Export Now"**
5. Download your files!

## 📋 Export Formats

| Format | Use Case | Size | Features |
|--------|----------|------|----------|
| **HTML** 📄 | Share with stakeholders | ~20KB | Interactive, professional report |
| **JSON** 📊 | API integration | ~10KB | Complete structured data |
| **CSV** 📋 | Further analysis | Varies | Transformed dataset |

## 💻 Code Examples

### Quick Export
```python
from src.utils.export import export_to_html, export_to_json

# HTML report
html_path = export_to_html(analysis_results, dataset_info)

# JSON data
json_path = export_to_json(analysis_results, dataset_info)
```

### Full Control
```python
from src.utils.export import ExportManager

manager = ExportManager()

exported = manager.export_all(
    analysis_results,
    dataset_info,
    formats=['html', 'json', 'csv'],
    session_id='my_analysis'
)
```

## 📁 File Locations

All exports are saved to:
```
data/exports/
```

## 🎯 Common Tasks

### Export After Complete Analysis
1. Run complete analysis
2. Go to Export tab
3. Select all formats
4. Click Export Now

### Export Specific Format
1. Go to Export tab
2. Uncheck unwanted formats
3. Click Export Now

### View Past Exports
1. Go to Export tab
2. Click "📂 View Exports"
3. Browse by format type
4. Download any file

### Custom Export Name
1. Enter name in "Custom Export Name" field
2. Example: `customer_churn_analysis`
3. Click Export Now

## ⚡ Pro Tips

✅ **HTML**: Best for presentations and stakeholder reports
✅ **JSON**: Best for programmatic access and APIs  
✅ **CSV**: Only available after running TransformAgent
✅ **Custom names**: Use descriptive names for important analyses
✅ **History**: Recent exports are kept in export history for quick access

## 🔧 Troubleshooting

**Export button disabled?**
→ Run at least one agent first

**CSV not available?**
→ Run TransformAgent first

**HTML not loading?**
→ Check internet connection (Plotly CDN required)

**Can't find exports?**
→ Check `data/exports/` directory

## 📚 Full Documentation

For complete documentation, see:
- `docs/EXPORT_FUNCTIONALITY.md` - Full user guide
- `EXPORT_FEATURE_SUMMARY.md` - Feature overview
- `IMPLEMENTATION_COMPLETE.md` - Technical details

## 🎉 That's It!

You're ready to export your analysis results!

Questions? Check the full documentation or contact the team.

---

**Version**: 1.0
**Last Updated**: July 19, 2026
