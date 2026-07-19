"""
Test that dataset name is correctly extracted and displayed
"""

from pathlib import Path
from src.data.dataset_handle import DatasetHandle
from src.utils.export import ExportManager

# Use a test dataset
test_file = "data/uploads/test_dataset.csv"

# Create a minimal CSV for testing if it doesn't exist
upload_dir = Path("data/uploads")
upload_dir.mkdir(parents=True, exist_ok=True)

test_path = upload_dir / "customer_data.csv"
if not test_path.exists():
    import pandas as pd
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'salary': [50000, 60000, 70000]
    })
    df.to_csv(test_path, index=False)
    print(f"Created test dataset: {test_path}")

# Test DatasetHandle
print("\n1. Testing DatasetHandle.get_info()...")
handle = DatasetHandle(str(test_path))
info = handle.get_info()

print(f"   Path field: {info.get('path', 'NOT FOUND')}")
print(f"   Name field: {info.get('name', 'NOT FOUND')}")

# Extract filename from path
dataset_name = Path(info['path']).name if 'path' in info else 'Unknown'
print(f"   Extracted name: {dataset_name}")

# Test with export
print("\n2. Testing export with dataset name...")

# Minimal analysis results
analysis_results = {
    'profile': {
        'confidence': 0.95,
        'reasoning': 'Test',
        'impact': 'Test',
        'recommendations': ['Test'],
        'result': {
            'basic_info': {
                'rows': 3,
                'columns': 4
            },
            'column_types': {
                'numeric': ['age', 'salary']
            }
        }
    }
}

dataset_info = {
    'name': dataset_name,
    'rows': info['rows'],
    'columns': info['columns'],
    'file_size_formatted': info['file_size_formatted']
}

print(f"   Dataset info: {dataset_info}")

# Export HTML
manager = ExportManager()
html_path = manager.export_html(
    analysis_results,
    dataset_info,
    "test_dataset_name.html"
)

print(f"\n3. HTML exported to: {html_path}")

# Check if name appears in HTML
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

if 'customer_data.csv' in html_content:
    print("   SUCCESS: Dataset name 'customer_data.csv' found in HTML!")
elif 'Unknown' in html_content:
    print("   ISSUE: 'Unknown' found in HTML instead of dataset name")
else:
    print("   WARNING: Neither dataset name nor 'Unknown' found")

print("\n" + "="*60)
print("Test complete!")
