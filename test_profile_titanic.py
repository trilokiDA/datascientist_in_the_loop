from src.data.dataset_handle import DatasetHandle
import json

# Load Titanic dataset
handle = DatasetHandle('data/uploads/titanic_train.csv')

# Get profile summary
profile = handle.get_profile_summary()

print('=' * 60)
print('TITANIC DATASET PROFILE')
print('=' * 60)

print('\nBasic Info:')
print(f"  Rows: {profile['basic_info']['rows']:,}")
print(f"  Columns: {profile['basic_info']['columns']}")
print(f"  File Size: {profile['basic_info']['file_size']}")
print(f"  Processing Mode: {profile['basic_info']['mode']}")

print('\nColumn Types:')
print(f"  Numeric: {len(profile['column_types']['numeric'])} columns")
print(f"    {', '.join(profile['column_types']['numeric'])}")
print(f"  Categorical: {len(profile['column_types']['categorical'])} columns")
print(f"    {', '.join(profile['column_types']['categorical'])}")
print(f"  Datetime: {len(profile['column_types']['datetime'])} columns")
print(f"  Other: {len(profile['column_types']['other'])} columns")

print('\nIssues Detected:')
print(f"  High missing columns (>40%): {len(profile['issues']['high_missing_cols'])}")
if profile['issues']['high_missing_cols']:
    print(f"    {', '.join(profile['issues']['high_missing_cols'])}")
print(f"  High cardinality columns (>90% unique): {len(profile['issues']['high_cardinality_cols'])}")
if profile['issues']['high_cardinality_cols']:
    print(f"    {', '.join(profile['issues']['high_cardinality_cols'])}")

print('\nTop Missing Value Columns:')
missing_sorted = sorted(profile['missing_info'].items(),
                        key=lambda x: x[1]['percentage'],
                        reverse=True)[:5]
for col, info in missing_sorted:
    if info['count'] > 0:
        print(f"  {col}: {info['count']} ({info['percentage']:.2f}%)")

print('\nCardinality Summary (Top 5):')
cardinality_sorted = sorted(profile['cardinality_info'].items(),
                            key=lambda x: x[1]['unique_count'],
                            reverse=True)[:5]
for col, info in cardinality_sorted:
    print(f"  {col}: {info['unique_count']} unique ({info['unique_percentage']:.2f}%)")

print('\n' + '=' * 60)
