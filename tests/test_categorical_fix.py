from src.data.dataset_handle import DatasetHandle
import json

# Load Titanic dataset
handle = DatasetHandle('data/uploads/titanic_train.csv')

# Get column types
column_types = handle.get_column_types()

print('Column Types Analysis:')
print('=' * 50)
print(f'Numeric columns ({len(column_types["numeric"])}):')
print('  ' + ', '.join(column_types['numeric']))
print(f'\nCategorical columns ({len(column_types["categorical"])}):')
print('  ' + ', '.join(column_types['categorical']))
print(f'\nDatetime columns ({len(column_types["datetime"])}):')
print('  ' + ', '.join(column_types['datetime']))
print(f'\nOther columns ({len(column_types["other"])}):')
print('  ' + ', '.join(column_types['other']))

print('\n' + '=' * 50)
print('Raw dtypes for reference:')
for col, dtype in handle.dtypes.items():
    print(f'  {col}: {dtype}')
