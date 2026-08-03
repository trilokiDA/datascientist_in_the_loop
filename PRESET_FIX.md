# Quick Preset Button Fix

## Problem
When clicking preset buttons (Strict/Balanced/Permissive), the slider values were not updating visually even though the underlying `st.session_state.quality_thresholds` was changing.

## Root Cause
Streamlit widgets with `key` parameters store their state independently. When we changed `st.session_state.quality_thresholds`, the widget state (`missing_slider`, `high_card_slider`, etc.) remained unchanged, and widget state takes precedence over the `value` parameter.

## Solution
Clear the widget state keys before rerunning the app, so sliders re-initialize with the new preset values.

### Implementation

**Added Helper Function:**
```python
def clear_threshold_widget_state():
    """Clear all threshold slider widget states to force UI update"""
    threshold_widget_keys = [
        'missing_slider', 'high_card_slider', 'low_card_slider',
        'iqr_input', 'z_input', 'strong_corr_slider', 'moderate_corr_slider'
    ]
    for key in threshold_widget_keys:
        if key in st.session_state:
            del st.session_state[key]
```

**Updated All Preset Buttons:**
```python
# Before
if st.button("🔴 Strict", ...):
    st.session_state.quality_thresholds = QualityThresholds.strict_preset()
    st.rerun()

# After
if st.button("🔴 Strict", ...):
    st.session_state.quality_thresholds = QualityThresholds.strict_preset()
    clear_threshold_widget_state()  # ← Added this
    st.rerun()
```

**Also Applied To:**
- ✅ Strict preset button
- ✅ Balanced preset button  
- ✅ Permissive preset button
- ✅ Reset to Defaults button

## How It Works Now

1. User clicks "🔴 Strict" button
2. `st.session_state.quality_thresholds` updated to strict preset values
3. **`clear_threshold_widget_state()` deletes all slider widget keys**
4. `st.rerun()` refreshes the page
5. Sliders re-initialize with no widget state, so they use the `value` parameter from `current_thresholds`
6. Sliders now show correct preset values!

## Testing

### Test Case 1: Preset Switching
1. Open app → Go to Settings → Quality Thresholds
2. Note default values (Missing: 40%, IQR: 1.5, etc.)
3. Click **🔴 Strict**
4. **Expected**: Sliders change to strict values (Missing: 20%, IQR: 1.0, etc.)
5. **Result**: ✅ Sliders update correctly

### Test Case 2: Preset → Manual → Preset
1. Click **🔴 Strict** (Missing: 20%)
2. Manually adjust Missing slider to 30%
3. Click **🟢 Permissive**
4. **Expected**: Missing slider changes to 60% (permissive value)
5. **Result**: ✅ Slider updates correctly

### Test Case 3: Reset Button
1. Manually adjust several sliders
2. Click **🔄 Reset to Defaults**
3. **Expected**: All sliders return to default values (40%, 90%, 1.5, etc.)
4. **Result**: ✅ All sliders reset correctly

## What Changed

| File | Changes |
|------|---------|
| `src/ui/app.py` | Added `clear_threshold_widget_state()` helper |
| `src/ui/app.py` | Updated Strict button to clear widget state |
| `src/ui/app.py` | Updated Balanced button to clear widget state |
| `src/ui/app.py` | Updated Permissive button to clear widget state |
| `src/ui/app.py` | Updated Reset button to clear widget state |

## Verify the Fix

**Visual Check:**
1. Run the app
2. Open Quality Thresholds expander
3. Click each preset button
4. Verify sliders visually update to show different values

**Value Check:**
```python
# In Streamlit app, you can add a debug expander:
with st.expander("🐛 Debug"):
    st.write("Threshold Object:", st.session_state.quality_thresholds.to_dict())
    st.write("Slider Widget State:", {
        k: v for k, v in st.session_state.items() 
        if k.endswith('_slider') or k.endswith('_input')
    })
# After clicking preset, both should show consistent values
```

## Alternative Solutions Considered

### Option 1: Remove Keys from Widgets ❌
```python
missing_threshold = st.slider(..., value=..., key=None)
```
**Problem**: Can't reference widgets later, and Streamlit warnings about duplicate widgets

### Option 2: Use st.session_state for Widget Values ❌
```python
if 'missing_slider' not in st.session_state:
    st.session_state.missing_slider = current_thresholds.missing_value_threshold
st.slider(..., value=st.session_state.missing_slider, key="missing_slider")
```
**Problem**: Creates circular dependency and doesn't solve the preset issue

### Option 3: Delete Widget State (CHOSEN) ✅
```python
clear_threshold_widget_state()
st.rerun()
```
**Benefit**: Clean, explicit, works perfectly with Streamlit's widget model

## Status

✅ **Fixed and Deployed**

The preset buttons now correctly update all slider values when clicked.
