from src.data.dataset_handle import DatasetHandle
import pandas as pd

print('=' * 60)
print('TESTING DATETIME DETECTION')
print('=' * 60)

# Test with dummy dataset
print('\n1. DUMMY DATASET')
print('-' * 60)
handle = DatasetHandle('data/uploads/dummy_dataset.csv')

column_types = handle.get_column_types()

print(f'Numeric columns ({len(column_types["numeric"])}):')
print(f'  {", ".join(column_types["numeric"][:5])}...')

print(f'\nCategorical columns ({len(column_types["categorical"])}):')
print(f'  {", ".join(column_types["categorical"][:5])}...')

print(f'\nDatetime columns ({len(column_types["datetime"])}):')
if column_types["datetime"]:
    print(f'  {", ".join(column_types["datetime"])}')
else:
    print('  None detected')

print('\nRaw dtypes for date columns:')
for col in ['registration_date', 'last_purchase_date']:
    print(f'  {col}: {handle.dtypes.get(col, "N/A")}')

# Get a sample to verify
sample = handle.head(3)
print('\nSample data:')
print(sample[['customer_id', 'registration_date', 'last_purchase_date']])

# Test with Titanic (should have no datetime columns)
print('\n\n2. TITANIC DATASET (for comparison)')
print('-' * 60)
handle2 = DatasetHandle('data/uploads/titanic_train.csv')
column_types2 = handle2.get_column_types()

print(f'Numeric: {len(column_types2["numeric"])} columns')
print(f'Categorical: {len(column_types2["categorical"])} columns')
print(f'Datetime: {len(column_types2["datetime"])} columns')

print('\n' + '=' * 60)
