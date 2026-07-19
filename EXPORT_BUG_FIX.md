# Export Functionality - Bug Fix

## Issue

The export functionality was throwing `KeyError` exceptions when trying to access fields that might not exist in the actual analysis results from agents.

**Error Example:**
```
File "src\utils\export.py", line 567, in _generate_profile_html
    <div class="value">{basic['memory_usage']}</div>
KeyError: 'memory_usage'
```

## Root Cause

The HTML generation methods were directly accessing dictionary keys without checking if they exist:
```python
# Before (unsafe)
basic = data['basic_info']
html += f"<div class='value'>{basic['memory_usage']}</div>"
```

This caused failures when:
- Agent results had slightly different structures
- Optional fields were missing
- Agents evolved and changed their output format

## Solution

### 1. Added Safe Access Helper Method

Created a `_safe_get()` static method to safely access nested dictionary keys:

```python
@staticmethod
def _safe_get(data: Dict[str, Any], *keys: str, default: Any = "N/A") -> Any:
    """
    Safely access nested dictionary keys
    
    Args:
        data: Dictionary to access
        *keys: Keys to traverse
        default: Default value if key not found
    
    Returns:
        Value at nested key or default
    """
    try:
        result = data
        for key in keys:
            result = result[key]
        return result if result is not None else default
    except (KeyError, TypeError, IndexError):
        return default
```

### 2. Updated All HTML Generation Methods

Updated all 6 HTML generation methods to use safe access:

#### ProfileAgent HTML
```python
# Before
basic = data['basic_info']
html += f"<div class='value'>{basic['memory_usage']}</div>"

# After
basic = data.get('basic_info', {})
memory = self._safe_get(basic, 'memory_usage', default='N/A')
if memory != 'N/A':
    html += f"<div class='value'>{memory}</div>"
```

#### QualityAgent HTML
```python
# Before
html += f"<div class='value'>{data['duplicates']['duplicate_percentage']:.1f}%</div>"

# After
dup_pct = self._safe_get(data, 'duplicates', 'duplicate_percentage', default=0)
html += f"<div class='value'>{dup_pct:.1f}%</div>"
```

#### FeatureAgent HTML
```python
# Before
corr = data['correlations']
html += f"<div class='value'>{corr['num_numeric_features']}</div>"

# After
corr = data.get('correlations', {})
num_features = corr.get('num_numeric_features', 0)
html += f"<div class='value'>{num_features}</div>"
```

Similar updates for:
- `_generate_stat_html()`
- `_generate_transform_html()`
- `_generate_visualization_html()`

### 3. Defensive Dictionary Access

Used `.get()` with default values throughout:

```python
# Before
data = result['result']
basic = data['basic_info']

# After
data = result.get('result', {})
basic = data.get('basic_info', {})
```

## Testing

### Edge Case Testing

Created `test_export_edge_cases.py` to test with minimal/missing data:

```python
minimal_results = {
    'profile': {
        'result': {
            'basic_info': {
                'rows': 100,
                'columns': 5
                # Missing: memory_usage, file_size
            }
        }
    }
}
```

**Results:**
✅ HTML export with missing fields: SUCCESS (10.6 KB)
✅ JSON export with missing fields: SUCCESS (0.9 KB)
✅ export_all with minimal data: SUCCESS

### Standard Testing

Existing tests still pass:
✅ `test_export.py` - All tests passing
✅ `demo_export.py` - Demo working correctly

## Changes Made

### Files Modified
- `src/utils/export.py` - Added safe access throughout

### Methods Updated
1. `_safe_get()` - NEW helper method
2. `_generate_profile_html()` - Safe access
3. `_generate_quality_html()` - Safe access
4. `_generate_feature_html()` - Safe access
5. `_generate_stat_html()` - Safe access
6. `_generate_transform_html()` - Safe access
7. `_generate_visualization_html()` - Safe access

### Test Files Created
- `test_export_edge_cases.py` - Edge case testing

## Benefits

✅ **No more KeyErrors**: Gracefully handles missing fields
✅ **Backwards Compatible**: Works with both old and new agent outputs
✅ **Future-Proof**: Agents can evolve without breaking exports
✅ **Robust**: Handles edge cases and incomplete data
✅ **Clear Defaults**: Missing data shows as "N/A" or 0 appropriately
✅ **Maintains Quality**: HTML reports still look professional

## Examples

### Before (Error-Prone)
```python
def _generate_profile_html(self, result):
    data = result['result']  # Fails if 'result' missing
    basic = data['basic_info']  # Fails if 'basic_info' missing
    rows = basic['rows']  # Fails if 'rows' missing
    return f"<div>{rows}</div>"
```

### After (Robust)
```python
def _generate_profile_html(self, result):
    data = result.get('result', {})  # Returns {} if missing
    basic = data.get('basic_info', {})  # Returns {} if missing
    rows = self._safe_get(basic, 'rows', default=0)  # Returns 0 if missing
    return f"<div>{rows:,}</div>"  # Always works
```

## Impact

### User Experience
- **Before**: Export would crash with KeyError
- **After**: Export always succeeds, shows "N/A" for missing data

### Developer Experience
- **Before**: Had to ensure exact field structure
- **After**: Can evolve agent outputs freely

### Maintenance
- **Before**: Brittle, broke with schema changes
- **After**: Resilient, adapts to variations

## Status

✅ **Bug Fixed**
✅ **Tests Passing**
✅ **Edge Cases Handled**
✅ **Production Ready**

## Deployment

No changes needed for deployment:
- Same dependencies
- Same file structure
- Same API
- Just more robust internally

---

**Fix Date**: July 19, 2026
**Status**: ✅ FIXED & TESTED
**Breaking Changes**: None
**Migration Required**: None
