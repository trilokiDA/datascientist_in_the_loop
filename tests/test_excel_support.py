"""
Test script to verify Excel file support
"""
import pandas as pd
from pathlib import Path
from src.data.dataset_handle import DatasetHandle

def create_test_excel():
    """Create a test Excel file for demonstration"""
    # Create sample data
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 28, 32],
        'Salary': [50000, 60000, 75000, 55000, 65000],
        'Department': ['HR', 'IT', 'Finance', 'IT', 'HR'],
        'Join_Date': pd.date_range('2020-01-01', periods=5, freq='6ME')
    }

    df = pd.DataFrame(data)

    # Create test directory
    test_dir = Path("data/uploads")
    test_dir.mkdir(parents=True, exist_ok=True)

    # Save as Excel
    excel_path = test_dir / "test_sample.xlsx"
    df.to_excel(excel_path, index=False, sheet_name='Employees')

    print(f"[OK] Created test Excel file: {excel_path}")
    return excel_path

def test_excel_loading():
    """Test loading Excel file with DatasetHandle"""
    print("\n[INFO] Testing Excel File Support\n")

    # Create test file
    excel_path = create_test_excel()

    # Test loading
    print(f"Loading Excel file: {excel_path}")
    handle = DatasetHandle(str(excel_path))

    # Display info
    info = handle.get_info()
    print(f"\n[OK] Successfully loaded Excel file!")
    print(f"   - Rows: {info['rows']}")
    print(f"   - Columns: {info['columns']}")
    print(f"   - Size: {info['file_size_formatted']}")
    print(f"   - Mode: {info['mode']}")
    print(f"   - Column Names: {', '.join(info['column_names'])}")

    # Display preview
    print(f"\n[DATA] Preview (first 5 rows):")
    print(handle.head(5))

    # Test statistics
    print(f"\n[STATS] Basic Statistics:")
    print(handle.describe())

    print("\n[OK] All tests passed! Excel support is working.")

if __name__ == "__main__":
    try:
        test_excel_loading()
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
