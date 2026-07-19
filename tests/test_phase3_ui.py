"""
Quick test to verify Phase 3 agents integrate correctly with UI
"""
import sys
from pathlib import Path

# Test imports
print("Testing imports...")
try:
    from src.agents.viz_agent import VisualizationAgent
    from src.agents.stat_agent import StatAgent
    from src.agents.feature_agent import FeatureAgent
    from src.data.dataset_handle import DatasetHandle
    print("OK All Phase 3 agents imported successfully")
except ImportError as e:
    print(f"ERROR Import error: {e}")
    sys.exit(1)

# Test profile data structure
print("\nTesting profile data structure...")
try:
    # Create a simple test dataset
    import pandas as pd
    test_df = pd.DataFrame({
        'numeric_col': [1, 2, 3, 4, 5],
        'categorical_col': ['A', 'B', 'A', 'B', 'C'],
        'missing_col': [1, None, 3, None, 5]
    })

    test_path = Path("data/test_temp.csv")
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_df.to_csv(test_path, index=False)

    handle = DatasetHandle(str(test_path))
    profile = handle.get_profile_summary()

    # Check expected fields
    assert 'basic_info' in profile, "Missing basic_info"
    assert 'rows' in profile['basic_info'], "Missing rows"
    assert 'columns' in profile['basic_info'], "Missing columns"
    assert 'file_size' in profile['basic_info'], "Missing file_size"
    assert 'mode' in profile['basic_info'], "Missing mode"
    assert 'column_types' in profile, "Missing column_types"
    assert 'missing_info' in profile, "Missing missing_info"
    assert 'issues' in profile, "Missing issues"

    print("OK Profile data structure matches UI expectations")

    # Test that missing percentage can be calculated
    missing_info = profile.get('missing_info', {})
    total_missing = sum(v['count'] for v in missing_info.values())
    total_cells = profile['basic_info']['rows'] * profile['basic_info']['columns']
    missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
    print(f"OK Missing percentage calculated: {missing_pct:.1f}%")

    # Cleanup
    test_path.unlink()

except Exception as e:
    print(f"ERROR Profile test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test agent instantiation
print("\nTesting agent instantiation...")
try:
    viz_agent = VisualizationAgent()
    stat_agent = StatAgent()
    feature_agent = FeatureAgent()
    print("OK All agents instantiated successfully")
except Exception as e:
    print(f"ERROR Agent instantiation error: {e}")
    sys.exit(1)

print("\n[SUCCESS] All Phase 3 tests passed!")
print("\nYou can now run: streamlit run src/ui/app_v3.py")
