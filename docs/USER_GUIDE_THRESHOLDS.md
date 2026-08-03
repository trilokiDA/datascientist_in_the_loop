# User Guide: Quality Threshold Configuration

## Overview

Quality thresholds control how sensitive the EDA pipeline is when detecting data issues. You can now customize these thresholds to match your specific needs.

---

## Quick Start

### 1. Using Preset Profiles (Easiest)

1. Upload your dataset
2. In the sidebar, expand **"🎯 Quality Thresholds"**
3. Click one of the preset buttons:
   - **🔴 Strict**: Low tolerance (flags more issues)
   - **🟡 Balanced**: Default settings (recommended)
   - **🟢 Permissive**: High tolerance (flags fewer issues)
4. Run your analysis

**When to use each:**
- **Strict**: Critical applications (healthcare, finance), high-quality data expected
- **Balanced**: General exploratory analysis, most use cases
- **Permissive**: Noisy data, research datasets, preliminary exploration

---

### 2. Custom Thresholds (Advanced)

1. Upload your dataset
2. In sidebar, expand **"🎯 Quality Thresholds"**
3. Click on tabs to adjust specific thresholds:

#### **📊 Missing & Cardinality**
- **High Missing % Threshold** (default: 40%)
  - Columns with missing values above this % are flagged
  - Lower = more sensitive (flags more columns)
  - Example: 20% will flag "Age" column with 25% missing
  
- **High Cardinality % Threshold** (default: 90%)
  - Columns with >90% unique values flagged as potential IDs
  - Example: 95% only flags columns with very few duplicates
  
- **Low Cardinality % Threshold** (default: 5%)
  - Columns with <5% unique values flagged as potential constants
  - Example: 10% will flag more columns as having "too few" unique values

#### **🔍 Outliers**
- **IQR Outlier Multiplier** (default: 1.5)
  - Standard IQR method: Q1 - 1.5×IQR, Q3 + 1.5×IQR
  - 1.5 = standard (flags moderate outliers)
  - 3.0 = extreme (only flags very extreme outliers)
  
- **Z-Score Threshold** (default: 3.0)
  - Standard deviations from mean
  - 3.0 = standard (flags values >3σ away)
  - 2.5 = stricter (flags more values)
  - 4.0 = more lenient

#### **🔗 Correlations**
- **Strong Correlation** (default: |r| > 0.7)
  - Absolute correlation coefficient threshold
  - 0.6 = flag more correlations as "strong"
  
- **Moderate Correlation** (default: |r| > 0.4)
  - Must be less than strong threshold

4. Click **"💾 Apply Thresholds"**
5. Run your analysis

---

### 3. Adjust During Analysis (Iterative)

When reviewing results in the approval gate:

1. Review agent results (e.g., ProfileAgent)
2. If too many/few issues flagged, expand **"⚙️ Adjust Thresholds & Retry"**
3. Tweak the relevant thresholds:
   - **ProfileAgent**: Missing %, Cardinality thresholds
   - **QualityAgent**: Outlier detection thresholds
4. Click **"🔄 Retry with New Thresholds"**
5. Click the main **"🔄 Retry This Agent"** button
6. Results update with new sensitivity

---

## Understanding Threshold Impact

### Missing Value Threshold

**Scenario**: Titanic dataset, "Age" column has 20% missing values

| Threshold | Result | When to Use |
|-----------|--------|-------------|
| 10% | ⚠️ Flagged as high missing | Critical data, imputation needed |
| 20% | ⚠️ Flagged (at boundary) | Moderate quality requirements |
| 40% | ✅ Not flagged | Exploratory analysis, missing OK |

---

### IQR Multiplier

**Scenario**: Salary data with some high earners

| Multiplier | Outliers Detected | Interpretation |
|------------|-------------------|----------------|
| 1.0 | 50 values | Very aggressive, flags many values |
| 1.5 (default) | 25 values | Standard statistical definition |
| 3.0 | 5 values | Only extreme outliers |

**Formula**: `[Q1 - k×IQR, Q3 + k×IQR]` where k = multiplier

---

### Correlation Thresholds

**Scenario**: Features with varying correlation strengths

| Strong | Moderate | Result |
|--------|----------|--------|
| >0.7 | >0.4 | Default: 5 strong, 12 moderate |
| >0.6 | >0.3 | Stricter: 8 strong, 18 moderate |
| >0.8 | >0.5 | Permissive: 2 strong, 7 moderate |

---

## Real-World Examples

### Example 1: Healthcare Data (Strict)

**Situation**: Patient records with critical measurements

**Settings**:
```
Missing: 20% (can't tolerate much missing data)
IQR: 1.0 (flag unusual vital signs aggressively)
Z-Score: 2.5 (catch anomalies early)
```

**Why**: Patient safety requires high data quality

---

### Example 2: Marketing Data (Permissive)

**Situation**: Web analytics with optional fields

**Settings**:
```
Missing: 60% (optional fields expected to be sparse)
High Cardinality: 95% (user IDs, session IDs OK)
IQR: 3.0 (wide range of user behavior normal)
```

**Why**: Noisy data, focus on overall patterns

---

### Example 3: Research Dataset (Balanced → Adjusted)

**Initial**: Balanced preset (40% missing threshold)

**After ProfileAgent**: 10 columns flagged with >40% missing

**User Action**:
1. Opens "Adjust Thresholds & Retry"
2. Changes missing threshold to 50%
3. Retries ProfileAgent
4. Only 4 columns now flagged (truly problematic ones)

**Why**: Iterative refinement to focus on real issues

---

## Tips & Best Practices

### 🎯 Start with Balanced
- Most users should start with the default **Balanced** preset
- Adjust only if results seem too aggressive or too lenient

### 📊 Domain Matters
- Finance/Healthcare → Strict
- Marketing/Social Media → Permissive
- Scientific Research → Balanced (then adjust)

### 🔄 Iterate During Approval
- First run: Use defaults
- Review results: Too many false positives?
- Adjust: Use contextual controls in approval gate
- Retry: Fine-tune until satisfied

### 📈 Document Your Choices
- Note which thresholds work best for your datasets
- Share with team for consistency
- Consider creating custom presets (future feature)

### ⚠️ Don't Over-Tune
- If you're constantly adjusting, your data might have quality issues
- Thresholds are for sensitivity, not to hide problems

---

## FAQ

### Q: Do thresholds affect my data?
**A**: No, thresholds only affect **detection** and **flagging**. Your actual data is never modified.

### Q: What happens if I set invalid thresholds?
**A**: The system validates thresholds and shows an error. For example, moderate correlation must be < strong correlation.

### Q: Do thresholds persist across sessions?
**A**: Currently no - thresholds reset when you reload the app. Future versions will support saving profiles.

### Q: Can I set different thresholds per column?
**A**: Not yet - current version uses global thresholds. Per-column thresholds are a planned enhancement.

### Q: Which agents use which thresholds?

| Agent | Thresholds Used |
|-------|----------------|
| ProfileAgent | Missing %, High/Low Cardinality |
| QualityAgent | IQR, Z-Score, Format Variance |
| FeatureAgent | Strong/Moderate Correlation |
| StatAgent | Skewness, Kurtosis (future) |

### Q: Can I see which thresholds were used?
**A**: Yes! In the approval gate, expand "🔍 View Detailed Results" - thresholds are shown at the bottom of each agent's details.

### Q: What if I want to revert changes?
**A**: Click **"🔄 Reset to Defaults"** in the sidebar Quality Thresholds section.

---

## Keyboard Shortcuts

None currently - all threshold controls are UI-based.

---

## Troubleshooting

### Issue: Too many issues flagged
**Solution**: 
1. Increase thresholds (e.g., 40% → 50% for missing)
2. Or switch to Permissive preset
3. Or adjust contextually after seeing results

### Issue: No issues flagged (but data looks problematic)
**Solution**:
1. Decrease thresholds (e.g., 40% → 30% for missing)
2. Or switch to Strict preset
3. Manually inspect data in approval gate

### Issue: Thresholds not applying
**Solution**:
1. Make sure you clicked "Apply Thresholds" button
2. Check for validation errors (red error message)
3. Verify you're running a new analysis (not viewing old results)

### Issue: Can't find threshold controls
**Solution**:
1. Look in sidebar under **Settings** section
2. Expand **"🎯 Quality Thresholds"** (collapsed by default)
3. Make sure you've uploaded a dataset first

---

## Getting Help

If you need assistance:
1. Check this guide first
2. Hover over ℹ️ help icons in the UI
3. Review the approval gate threshold displays
4. Check `THRESHOLD_IMPLEMENTATION_SUMMARY.md` for technical details

---

## What's Next?

Future enhancements planned:
- 💾 Save/Load custom threshold profiles
- 📚 Domain-specific preset library (Healthcare, Finance, etc.)
- 🎯 Per-column threshold overrides
- 🤖 AI-suggested thresholds based on dataset characteristics
- 📊 Threshold impact preview ("If you change this, X more issues will be flagged")

---

**Happy Analyzing!** 🚀
