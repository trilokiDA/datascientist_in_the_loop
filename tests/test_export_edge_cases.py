"""
Test export functionality with edge cases and missing data
"""

from pathlib import Path
from src.utils.export import ExportManager

# Minimal analysis results with missing fields
minimal_results = {
    'profile': {
        'confidence': 0.95,
        'reasoning': 'Basic profiling completed',
        'impact': 'Provides structure information',
        'recommendations': ['Review data types'],
        'result': {
            'basic_info': {
                'rows': 100,
                'columns': 5
                # Missing: memory_usage, file_size
            },
            'column_types': {
                'numeric': ['col1', 'col2']
                # Missing: categorical, datetime
            }
            # Missing: missing_info
        }
    },
    'quality': {
        'confidence': 0.90,
        'reasoning': 'Quality check completed',
        'impact': 'Identifies issues',
        'recommendations': [],
        'result': {
            'duplicates': {
                'duplicate_percentage': 0.5
                # Missing: duplicate_rows
            },
            'outliers': {
                'has_outliers': False
                # Missing: columns_with_outliers, outlier_details
            }
            # Missing: inconsistencies, data_types
        }
    }
}

# Empty dataset info
minimal_info = {
    'name': 'minimal_test.csv'
    # Missing: rows, columns, file_size_formatted
}

manager = ExportManager()

print("Testing Export with Minimal/Missing Data")
print("=" * 60)

try:
    print("\n1. Testing HTML export with missing fields...")
    html_path = manager.export_html(
        minimal_results,
        minimal_info,
        "test_minimal.html"
    )
    print(f"   SUCCESS: {html_path}")

    # Check file exists and has content
    file_size = Path(html_path).stat().st_size
    print(f"   File size: {file_size} bytes")

    if file_size > 1000:  # At least 1KB
        print("   File has reasonable content")

except Exception as e:
    print(f"   FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n2. Testing JSON export with missing fields...")
    json_path = manager.export_json(
        minimal_results,
        minimal_info,
        "test_minimal.json"
    )
    print(f"   SUCCESS: {json_path}")

    file_size = Path(json_path).stat().st_size
    print(f"   File size: {file_size} bytes")

except Exception as e:
    print(f"   FAILED: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n3. Testing export_all with minimal data...")
    exported = manager.export_all(
        minimal_results,
        minimal_info,
        formats=['html', 'json'],
        session_id='minimal_test'
    )

    print("   SUCCESS: All formats exported")
    for format_type, path in exported.items():
        size = Path(path).stat().st_size / 1024
        print(f"   - {format_type.upper()}: {size:.1f} KB")

except Exception as e:
    print(f"   FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Edge case testing complete!")
print("\nIf all tests passed, the export module handles missing data gracefully.")
