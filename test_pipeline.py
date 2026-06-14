"""
Test script to verify the EDA pipeline components work
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.dataset_handle import DatasetHandle
from src.agents.profile_agent import ProfileAgent
from src.utils.helpers import format_bytes
import pandas as pd
import os


def create_sample_dataset():
    """Create a sample dataset for testing"""
    print("Creating sample dataset...")

    # Create sample data
    data = {
        'age': [25, 30, 35, None, 45, 28, 32, None, 40, 29] * 100,
        'income': [50000, 60000, 75000, 80000, 90000, 55000, None, 70000, 85000, 62000] * 100,
        'category': ['A', 'B', 'A', 'C', 'B', 'A', 'D', 'C', 'B', 'A'] * 100,
        'id': range(1000),  # High cardinality
        'score': [85.5, 90.2, 78.3, 88.1, 92.5, 81.7, 89.3, 77.8, 91.2, 83.6] * 100
    }

    df = pd.DataFrame(data)

    # Save to CSV
    output_dir = Path("data/uploads")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "sample_data.csv"
    df.to_csv(output_path, index=False)

    print(f"✅ Sample dataset created: {output_path}")
    print(f"   Shape: {df.shape}")
    print(f"   Size: {format_bytes(os.path.getsize(output_path))}")

    return str(output_path)


def test_dataset_handle(path: str):
    """Test DatasetHandle"""
    print("\n" + "="*60)
    print("Testing DatasetHandle...")
    print("="*60)

    handle = DatasetHandle(path)

    print(f"\n📊 Dataset Info:")
    info = handle.get_info()
    print(f"  Mode: {info['mode']}")
    print(f"  Rows: {info['rows']:,}")
    print(f"  Columns: {info['columns']}")
    print(f"  File Size: {info['file_size_formatted']}")

    print(f"\n📋 Column Types:")
    col_types = handle.get_column_types()
    for type_name, cols in col_types.items():
        if cols:
            print(f"  {type_name}: {cols}")

    print(f"\n⚠️  Missing Values:")
    missing = handle.get_missing_info()
    for col, data in missing.items():
        if data['count'] > 0:
            print(f"  {col}: {data['count']} ({data['percentage']:.2f}%)")

    print(f"\n🔢 Cardinality:")
    cardinality = handle.get_cardinality_info()
    for col, data in list(cardinality.items())[:5]:
        print(f"  {col}: {data['unique_count']} unique ({data['unique_percentage']:.2f}%)")

    return handle


def test_profile_agent(handle: DatasetHandle):
    """Test ProfileAgent"""
    print("\n" + "="*60)
    print("Testing ProfileAgent...")
    print("="*60)

    agent = ProfileAgent()
    response = agent.analyze(handle)

    print(f"\n🤖 Agent: {agent.get_agent_name()}")

    print(f"\n💡 Reasoning:")
    print(f"  {response['reasoning']}")

    print(f"\n⚡ Impact:")
    print(f"  {response['impact']}")

    print(f"\n📝 Recommendations:")
    for i, rec in enumerate(response['recommendations'], 1):
        print(f"  {i}. {rec}")

    print(f"\n🎯 Confidence: {response['confidence']:.0%}")

    return response


def main():
    """Main test function"""
    print("\n🚀 EDA Pipeline Test\n")

    # Create sample dataset
    dataset_path = create_sample_dataset()

    # Test DatasetHandle
    handle = test_dataset_handle(dataset_path)

    # Test ProfileAgent
    response = test_profile_agent(handle)

    print("\n" + "="*60)
    print("✅ All tests completed successfully!")
    print("="*60)

    print("\n📌 Next Steps:")
    print("  1. Set your GROQ_API_KEY in .env file")
    print("  2. Run: streamlit run src/ui/app.py")
    print("  3. Upload the sample dataset and start analyzing!")


if __name__ == "__main__":
    main()
