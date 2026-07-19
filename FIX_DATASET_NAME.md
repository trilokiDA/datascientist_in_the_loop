# Fix: Dataset Name Display in HTML Export

## Issue

The HTML export was showing "Dataset: Unknown" instead of the actual dataset filename.

## Root Cause

The `DatasetHandle.get_info()` method returns a `path` field (full file path), not a `name` field. The export code was trying to access `info.get('name', 'Unknown')`, which always returned the default value 'Unknown'.

**Example of get_info() output:**
```python
{
    "path": "data/uploads/customer_data.csv",  # Full path returned
    "rows": 1000,
    "columns": 10,
    # No 'name' field exists
}
```

## Solution

Extract the filename from the path using `Path().name`:

### Fixed in: `src/ui/app_v3.py`

**Location 1: Export function (line ~1220)**
```python
# Before
dataset_info = {
    'name': info.get('name', 'Unknown'),  # Always returned 'Unknown'
    'rows': info['rows'],
    ...
}

# After
dataset_name = Path(info['path']).name if 'path' in info else 'Unknown'
dataset_info = {
    'name': dataset_name,  # Now correctly extracts filename
    'rows': info['rows'],
    ...
}
```

**Location 2: Export preview display (line ~1162)**
```python
# Before
st.markdown(f"- **Name:** {info.get('name', 'Unknown')}")

# After
dataset_name = Path(info['path']).name if 'path' in info else 'Unknown'
st.markdown(f"- **Name:** {dataset_name}")
```

## Testing

Created `test_dataset_name.py` to verify the fix:

**Test Results:**
```
1. DatasetHandle.get_info()
   Path field: data\uploads\customer_data.csv
   Name field: NOT FOUND
   Extracted name: customer_data.csv ✓

2. Export with dataset name
   Dataset info: {'name': 'customer_data.csv', ...} ✓

3. HTML exported
   SUCCESS: Dataset name 'customer_data.csv' found in HTML! ✓
```

**HTML Output Verification:**
```html
<p><strong>Dataset:</strong> customer_data.csv</p>
```

## Files Modified

- `src/ui/app_v3.py` (2 locations)

## Files Created

- `test_dataset_name.py` - Test script
- `FIX_DATASET_NAME.md` - This documentation

## Examples

### Before Fix
```
Dataset: Unknown
Rows: 1,000 | Columns: 10
```

### After Fix
```
Dataset: customer_data.csv
Rows: 1,000 | Columns: 10
```

## Impact

✅ HTML exports now show correct dataset filename
✅ Export preview shows correct dataset filename
✅ No breaking changes
✅ Backwards compatible (handles missing path gracefully)

## Status

✅ **FIXED**
✅ **TESTED**
✅ **VERIFIED**

---

**Fix Date**: July 19, 2026
**Tested**: Yes
**Breaking Changes**: None
