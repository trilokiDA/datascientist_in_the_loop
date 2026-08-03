# Threshold Configuration - UI Placement Options

## Current Sidebar Structure
```
📁 Dataset (file uploader + quick stats)
---
🔄 Analysis Options (analysis type + run buttons)
---
⚙️ Settings (show reasoning, show confidence)
---
💰 Token Usage & Cost Tracking
```

## **Option 1: In Settings Section (RECOMMENDED)**
**Best for: Quick access, always visible**

```python
# After line 314 in app.py
st.divider()

# Settings
st.header("⚙️ Settings")
show_reasoning = st.checkbox("Show Reasoning", value=True)
show_confidence = st.checkbox("Show Confidence", value=True)

# NEW: Quality Thresholds
with st.expander("🎯 Quality Thresholds", expanded=False):
    st.caption("Configure sensitivity for data quality checks")
    
    tab1, tab2, tab3 = st.tabs(["Missing & Cardinality", "Outliers", "Correlations"])
    
    with tab1:
        missing_threshold = st.slider(
            "High Missing % Threshold",
            min_value=0.0, max_value=100.0, value=40.0, step=5.0,
            help="Flag columns with missing values above this percentage"
        )
        high_card_threshold = st.slider(
            "High Cardinality % Threshold", 
            min_value=0.0, max_value=100.0, value=90.0, step=5.0,
            help="Flag columns with unique values above this percentage"
        )
        low_card_threshold = st.slider(
            "Low Cardinality % Threshold", 
            min_value=0.0, max_value=50.0, value=5.0, step=1.0,
            help="Flag columns with few unique values below this percentage"
        )
    
    with tab2:
        iqr_multiplier = st.number_input(
            "IQR Outlier Multiplier",
            min_value=0.5, max_value=5.0, value=1.5, step=0.5,
            help="IQR method: 1.5=standard, 3.0=extreme outliers only"
        )
        z_threshold = st.number_input(
            "Z-Score Threshold",
            min_value=1.0, max_value=5.0, value=3.0, step=0.5,
            help="Standard deviations for outlier detection"
        )
    
    with tab3:
        strong_corr = st.slider(
            "Strong Correlation Threshold",
            min_value=0.5, max_value=1.0, value=0.7, step=0.05,
            help="Minimum |r| to flag as strong correlation"
        )
        moderate_corr = st.slider(
            "Moderate Correlation Threshold",
            min_value=0.3, max_value=0.7, value=0.4, step=0.05,
            help="Minimum |r| to flag as moderate correlation"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset Defaults", use_container_width=True):
            st.session_state.thresholds = None
            st.rerun()
    with col2:
        if st.button("Apply", use_container_width=True, type="primary"):
            st.session_state.thresholds = {
                'missing_value_threshold': missing_threshold,
                'high_cardinality_threshold': high_card_threshold,
                'low_cardinality_threshold': low_card_threshold,
                'iqr_multiplier': iqr_multiplier,
                'z_score_threshold': z_threshold,
                'strong_correlation_threshold': strong_corr,
                'moderate_correlation_threshold': moderate_corr
            }
            st.success("✅ Thresholds updated!")
```

**Pros:**
- ✅ Grouped with other settings (logical placement)
- ✅ Collapsed by default (doesn't clutter sidebar)
- ✅ Accessible before AND during analysis
- ✅ Tabs organize thresholds by category

**Cons:**
- ❌ Sidebar might feel crowded with long lists

---

## **Option 2: Dedicated Settings Page**
**Best for: Advanced users, comprehensive configuration**

Add a new page using Streamlit's multipage app structure:

```
src/ui/
├── app.py (main analysis page)
├── pages/
    ├── 1_Settings.py (NEW - threshold configuration)
    ├── 2_Export_History.py
    └── 3_Help.py
```

```python
# pages/1_Settings.py
import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️")

st.title("⚙️ Quality Threshold Configuration")

# Full-width, comprehensive settings UI
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Data Profiling Thresholds")
    # All missing/cardinality thresholds
    
    st.subheader("🔍 Outlier Detection")
    # Outlier method thresholds

with col2:
    st.subheader("🔗 Feature Engineering")
    # Correlation thresholds
    
    st.subheader("📈 Statistical Tests")
    # Skewness, kurtosis thresholds

# Preset profiles
st.divider()
st.subheader("📋 Preset Profiles")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔴 Strict", use_container_width=True):
        # Load strict thresholds (low tolerance)
        pass
with col2:
    if st.button("🟡 Balanced (Default)", use_container_width=True):
        # Load default thresholds
        pass
with col3:
    if st.button("🟢 Permissive", use_container_width=True):
        # Load permissive thresholds (high tolerance)
        pass
```

**Pros:**
- ✅ Dedicated space for comprehensive configuration
- ✅ Can add presets, import/export, documentation
- ✅ Doesn't clutter main analysis flow
- ✅ Scales well for future settings

**Cons:**
- ❌ Users must navigate away from main page
- ❌ Requires page structure setup

---

## **Option 3: Modal Dialog / Popup**
**Best for: Occasional adjustments, clean UI**

```python
# In sidebar, add a button
if st.button("🎯 Configure Thresholds", use_container_width=True):
    st.session_state.show_threshold_modal = True

# In main area (app.py), show modal dialog
if st.session_state.get('show_threshold_modal', False):
    with st.container():
        st.markdown("""
        <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                    background: white; padding: 2rem; border-radius: 10px; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3); z-index: 1000; 
                    width: 600px; max-height: 80vh; overflow-y: auto;">
        """, unsafe_allow_html=True)
        
        st.subheader("🎯 Quality Threshold Configuration")
        # Threshold sliders here...
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_threshold_modal = False
                st.rerun()
        with col2:
            if st.button("Save", use_container_width=True, type="primary"):
                # Save thresholds
                st.session_state.show_threshold_modal = False
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
```

**Pros:**
- ✅ Clean, focused interaction
- ✅ Doesn't take sidebar real estate
- ✅ Modern UI pattern

**Cons:**
- ❌ Streamlit doesn't have native modals (requires CSS hacks)
- ❌ May have z-index issues with other components

---

## **Option 4: Contextual Placement (During Analysis)**
**Best for: Just-in-time configuration**

Show threshold options when relevant results appear:

```python
# In approval_gate.py, after rendering quality issues
if self.step_id == "quality":
    st.divider()
    with st.expander("⚙️ Adjust Quality Thresholds & Rerun"):
        st.caption("Not satisfied with results? Adjust sensitivity and retry.")
        
        missing_threshold = st.slider("High Missing % Threshold", ...)
        # Other thresholds...
        
        if st.button("🔄 Rerun with New Thresholds"):
            # Update thresholds and retry
            return "retry"
```

**Pros:**
- ✅ Contextual - appears when most relevant
- ✅ Encourages iterative tuning
- ✅ No extra navigation needed

**Cons:**
- ❌ Only available during analysis (not before)
- ❌ May clutter approval gate UI

---

## **Recommendation: Hybrid Approach (Best of All)**

**Implement BOTH Option 1 + Option 4:**

1. **Option 1 (Settings Section)** - For pre-analysis configuration
2. **Option 4 (Contextual)** - Quick adjustment in approval gates

**Why Hybrid?**
- ✅ Power users can configure upfront in settings
- ✅ New users discover thresholds when they see results
- ✅ Encourages experimentation during approval flow
- ✅ No page navigation required
- ✅ Progressive disclosure (collapsed by default)

**Implementation Priority:**
1. **Phase 1**: Add to Settings section (Option 1) - 1-2 hours
2. **Phase 2**: Add contextual adjustments in approval gates (Option 4) - 2-3 hours
3. **Phase 3** (optional): Create dedicated settings page (Option 2) - 4-6 hours

---

## Visual Mockup - Option 1 (Recommended)

```
SIDEBAR
┌─────────────────────────────┐
│ 📁 Dataset                   │
│  [Upload CSV/Excel]          │
│  Rows: 150 | Cols: 5         │
├─────────────────────────────┤
│ 🔄 Analysis Options          │
│  ○ Quick Analysis            │
│  [🚀 Run Complete Analysis]  │
├─────────────────────────────┤
│ ⚙️ Settings                  │
│  ☑ Show Reasoning            │
│  ☑ Show Confidence           │
│  ▼ 🎯 Quality Thresholds     │ <-- NEW: Collapsed expander
│    [Missing] [Outliers] [Corr]│
│    Missing %: ----●----  40%  │
│    Cardinality: ---●---  90%  │
│    [Reset] [Apply]            │
├─────────────────────────────┤
│ 💰 Token Usage               │
└─────────────────────────────┘
```

---

## Next Steps

1. Create `src/config/quality_thresholds.py` (dataclass)
2. Implement Option 1 in sidebar settings
3. Pass thresholds to agents via constructor
4. Add threshold display in approval gate
5. (Optional) Add contextual adjustments in approval gate

Would you like me to implement the recommended hybrid approach?
