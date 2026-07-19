"""
Test script for export functionality
"""

from pathlib import Path
from src.utils.export import ExportManager

# Sample analysis results
analysis_results = {
    'profile': {
        'confidence': 0.95,
        'reasoning': 'Dataset profiled successfully with comprehensive statistics',
        'impact': 'Provides foundational understanding of data structure',
        'recommendations': [
            'Handle missing values in key columns',
            'Consider encoding categorical variables'
        ],
        'result': {
            'basic_info': {
                'rows': 1000,
                'columns': 10,
                'file_size': '50 KB',
                'memory_usage': '100 KB'
            },
            'column_types': {
                'numeric': ['age', 'salary', 'score'],
                'categorical': ['category', 'status'],
                'datetime': ['date']
            },
            'missing_info': {
                'age': {'count': 5, 'percentage': 0.5}
            }
        }
    },
    'quality': {
        'confidence': 0.92,
        'reasoning': 'Quality assessment completed with detailed anomaly detection',
        'impact': 'Identifies data quality issues requiring attention',
        'recommendations': [
            'Remove duplicate rows',
            'Handle outliers in numeric columns'
        ],
        'result': {
            'duplicates': {
                'duplicate_rows': 10,
                'duplicate_percentage': 1.0
            },
            'outliers': {
                'has_outliers': True,
                'columns_with_outliers': 2,
                'outlier_details': {
                    'salary': {
                        'iqr_outliers': 15,
                        'iqr_percentage': 1.5,
                        'min': 20000,
                        'max': 200000
                    }
                }
            },
            'inconsistencies': {
                'inconsistency_count': 3
            },
            'data_types': {
                'type_issue_count': 1
            }
        }
    }
}

dataset_info = {
    'name': 'test_dataset.csv',
    'rows': 1000,
    'columns': 10,
    'file_size_formatted': '50 KB'
}

# Test export
manager = ExportManager()

print("Testing Export Functionality\n")

# Test HTML export
print("Exporting HTML report...")
html_path = manager.export_html(analysis_results, dataset_info, "test_report.html")
print(f"HTML exported to: {html_path}")

# Test JSON export
print("\nExporting JSON data...")
json_path = manager.export_json(analysis_results, dataset_info, "test_results.json")
print(f"JSON exported to: {json_path}")

# Test export_all
print("\nTesting export_all...")
exported = manager.export_all(
    analysis_results,
    dataset_info,
    formats=['html', 'json'],
    session_id='test_session'
)

print("\nExport All Results:")
for format_type, path in exported.items():
    print(f"  - {format_type.upper()}: {path}")

print("\nAll tests passed!")
