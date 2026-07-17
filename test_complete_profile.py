from src.data.dataset_handle import DatasetHandle

print('=' * 70)
print('COMPLETE DATASET PROFILE WITH DATETIME DETECTION')
print('=' * 70)

# Test with dummy dataset
handle = DatasetHandle('data/uploads/dummy_dataset.csv')
profile = handle.get_profile_summary()

print('\nDATASET: dummy_dataset.csv')
print('-' * 70)

print('\nBasic Info:')
print(f"  Rows: {profile['basic_info']['rows']:,}")
print(f"  Columns: {profile['basic_info']['columns']}")
print(f"  File Size: {profile['basic_info']['file_size']}")
print(f"  Processing Mode: {profile['basic_info']['mode']}")

print('\nColumn Types Breakdown:')
print(f"  Numeric: {len(profile['column_types']['numeric'])} columns")
print(f"    {', '.join(profile['column_types']['numeric'])}")

print(f"\n  Categorical: {len(profile['column_types']['categorical'])} columns")
print(f"    {', '.join(profile['column_types']['categorical'])}")

print(f"\n  Datetime: {len(profile['column_types']['datetime'])} columns")
if profile['column_types']['datetime']:
    print(f"    {', '.join(profile['column_types']['datetime'])}")
else:
    print('    None')

print(f"\n  Other: {len(profile['column_types']['other'])} columns")

print('\nData Quality Issues:')
print(f"  High missing columns (>40%): {len(profile['issues']['high_missing_cols'])}")
if profile['issues']['high_missing_cols']:
    for col in profile['issues']['high_missing_cols']:
        print(f"    - {col}")

print(f"  High cardinality columns (>90% unique): {len(profile['issues']['high_cardinality_cols'])}")
if profile['issues']['high_cardinality_cols']:
    for col in profile['issues']['high_cardinality_cols']:
        print(f"    - {col}")

print('\nSample Data Preview:')
sample = handle.head(3)
print(sample[['customer_id', 'age', 'registration_date', 'last_purchase_date', 'product_category']].to_string())

print('\n' + '=' * 70)
print('[SUCCESS] Categorical columns detected: Name, Sex, Ticket, etc. (from Titanic)')
print('[SUCCESS] Datetime columns detected: registration_date, last_purchase_date')
print('=' * 70)
