# Installation Guide - Phase 3 Enhanced EDA Pipeline

## 📦 Updated Dependencies

The requirements.txt file has been enhanced with proper version constraints and documentation for Phase 3 agents.

## 🚀 Installation Options

### Option 1: Fresh Installation (Recommended)

If you're starting fresh or want to ensure clean dependencies:

```bash
# Create a new virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Option 2: Update Existing Installation

If you already have Phase 1 or Phase 2 installed:

```bash
# Update to latest versions
pip install --upgrade -r requirements.txt
```

### Option 3: Install Only New Dependencies

If you only want to add Phase 3 agent dependencies:

```bash
# Install visualization libraries
pip install matplotlib>=3.7.0 seaborn>=0.12.0 plotly>=5.18.0

# Install statistical analysis libraries
pip install scipy>=1.11.0 statsmodels>=0.14.0 scikit-learn>=1.3.0
```

## 📋 Dependency Breakdown

### Core Dependencies (Phase 1 & 2)
```
langchain>=0.1.0           # LLM orchestration framework
langchain-groq>=0.1.0      # Groq LLM integration
langgraph>=0.0.40          # Workflow state management
langchain-community>=0.0.20 # Community tools
pandas>=2.0.0              # Data manipulation
duckdb>=0.9.0              # SQL database for large files
polars>=0.19.0             # Fast dataframe library
numpy>=1.24.0              # Numerical computing
streamlit>=1.28.0          # UI framework
python-dotenv>=1.0.0       # Environment variables
pydantic>=2.0.0            # Data validation
```

### Visualization Libraries (Phase 3 - NEW) ✨
```
plotly>=5.18.0             # Interactive plotting
seaborn>=0.12.0            # Statistical visualization
matplotlib>=3.7.0          # Core plotting library
```

**Used by:** `VisualizationAgent`
- Distribution plots (histograms, box plots)
- Correlation heatmaps
- Categorical bar charts
- Missing value visualizations

### Statistical Analysis Libraries (Phase 3 - NEW) ✨
```
scipy>=1.11.0              # Scientific computing & statistics
statsmodels>=0.14.0        # Statistical modeling
scikit-learn>=1.3.0        # Machine learning utilities
```

**Used by:** `StatAgent` and `FeatureAgent`
- Normality tests (Shapiro-Wilk, D'Agostino)
- Hypothesis testing (t-tests, ANOVA, Chi-square)
- Correlation analysis
- Feature engineering utilities

## ✅ Verify Installation

After installation, verify everything is working:

```bash
# Quick verification
python -c "import langchain, pandas, numpy, matplotlib, seaborn, plotly, scipy, sklearn; print('✅ All dependencies installed!')"
```

### Detailed Verification

Run the test suite to verify all agents work correctly:

```bash
python test_new_agents.py
```

This will test:
- ✅ Data loading and processing
- ✅ VisualizationAgent (plot generation)
- ✅ FeatureAgent (correlation analysis)
- ✅ StatAgent (statistical tests)
- ✅ Integration between agents

## 🐛 Common Installation Issues

### Issue 1: "Microsoft Visual C++ is required"

**Problem:** Some libraries (like scipy) require C++ build tools on Windows

**Solution:**
```bash
# Option A: Install pre-built wheels
pip install scipy --only-binary :all:

# Option B: Install Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### Issue 2: "No module named 'sklearn'"

**Problem:** scikit-learn not installed properly

**Solution:**
```bash
pip install scikit-learn>=1.3.0
```

### Issue 3: Matplotlib backend errors on Windows

**Problem:** Default matplotlib backend may not work in some environments

**Solution:**
The agents already handle this with:
```python
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
```

If you still have issues:
```bash
# Set environment variable
set MPLBACKEND=Agg  # Windows
export MPLBACKEND=Agg  # macOS/Linux
```

### Issue 4: "Could not find a version that satisfies the requirement"

**Problem:** Python version too old or pip needs updating

**Solution:**
```bash
# Update pip
python -m pip install --upgrade pip

# Use Python 3.9 or higher
python --version  # Should show 3.9+
```

### Issue 5: Plotly charts not displaying

**Problem:** Plotly not configured for Streamlit

**Solution:**
Plotly works automatically in Streamlit. If you have issues:
```bash
pip install --upgrade plotly streamlit
```

## 📊 Minimum Requirements

### Python Version
- **Minimum:** Python 3.9
- **Recommended:** Python 3.10 or 3.11
- **Not Tested:** Python 3.12+ (may work but not officially tested)

### System Requirements
- **RAM:** 4GB minimum, 8GB+ recommended for large datasets
- **Disk Space:** 500MB for dependencies + space for your data
- **OS:** Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)

## 🔧 Development Installation

If you want to contribute or modify the code:

```bash
# Clone the repository (if applicable)
git clone <your-repo-url>
cd test

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
pip install -r requirements.txt

# Install additional development tools (optional)
pip install pytest black flake8 mypy
```

## 🌐 Environment Setup

After installing dependencies, configure your environment:

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# GROQ_API_KEY=your_key_here
```

Get a free Groq API key: https://console.groq.com/

## 📦 Dependency Size Reference

Approximate download sizes:
- **Core dependencies (Phase 1 & 2):** ~200MB
- **Visualization libraries (Phase 3):** ~50MB
- **Statistical libraries (Phase 3):** ~100MB
- **Total:** ~350MB

After installation:
- **Total disk space:** ~800MB - 1GB

## 🔄 Keeping Dependencies Updated

### Check for updates:
```bash
pip list --outdated
```

### Update specific package:
```bash
pip install --upgrade <package-name>
```

### Update all packages (use with caution):
```bash
pip install --upgrade -r requirements.txt
```

**Note:** Always test after major updates to ensure compatibility.

## 🎯 Minimal Installation (Testing Only)

If you only want to test specific agents:

### Just VisualizationAgent:
```bash
pip install pandas matplotlib seaborn plotly langchain langchain-groq python-dotenv
```

### Just FeatureAgent:
```bash
pip install pandas numpy scipy scikit-learn langchain langchain-groq python-dotenv
```

### Just StatAgent:
```bash
pip install pandas numpy scipy statsmodels langchain langchain-groq python-dotenv
```

## 📱 Installation Verification Checklist

After installation, check:

- [ ] All dependencies installed: `pip list`
- [ ] Python version is 3.9+: `python --version`
- [ ] Can import all packages: Run verification script above
- [ ] Groq API key configured: Check `.env` file
- [ ] Test suite passes: `python test_new_agents.py`
- [ ] Plots directory created: `data/artifacts/plots/` exists
- [ ] No import errors in test run

## 🚀 Quick Start After Installation

```bash
# 1. Verify installation
python -c "import matplotlib, seaborn, scipy; print('✅ Ready!')"

# 2. Test new agents
python test_new_agents.py

# 3. Check generated plots
ls data/artifacts/plots/  # macOS/Linux
dir data\artifacts\plots\  # Windows

# 4. Run the application
streamlit run src/ui/app_v2.py
```

## 💡 Pro Tips

1. **Use Virtual Environments:** Always use venv or conda to isolate dependencies
2. **Pin Versions:** The requirements.txt already has minimum versions specified
3. **Regular Updates:** Check for security updates monthly
4. **Test After Updates:** Always run `test_new_agents.py` after updating
5. **Monitor Disk Space:** Large datasets + plots can consume significant space

## 📞 Getting Help

If you encounter issues:

1. **Check Python version:** `python --version` (must be 3.9+)
2. **Update pip:** `python -m pip install --upgrade pip`
3. **Check error messages:** Look for specific package name
4. **Search for package-specific issues:** Many common issues are documented
5. **Try fresh installation:** Create new venv and reinstall

## 🎉 Success!

If `python test_new_agents.py` runs successfully and generates plots, you're all set!

**Next steps:**
- Read `QUICKSTART_PHASE3.md` for usage examples
- Review `PHASE3_AGENTS_SUMMARY.md` for detailed documentation
- Start analyzing your data with the new agents!

---

**Installation complete! Your enhanced EDA pipeline is ready to use.** 🚀
