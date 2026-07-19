# Tests Directory

This directory contains test and demo files for the EDA Pipeline project.

## Test Files

### Agent Tests
- **test_new_agents.py** - Tests for the 6 specialized agents (Profile, Quality, Transform, Visualization, Feature, Stat)
- **test_complete_profile.py** - Complete profiling agent test
- **test_profile_titanic.py** - ProfileAgent test using Titanic dataset

### Feature-Specific Tests
- **test_export.py** - Export functionality tests (HTML, JSON, CSV)
- **test_export_edge_cases.py** - Edge case testing for export system
- **test_categorical_fix.py** - Categorical column handling fix verification
- **test_datetime_fix.py** - DateTime column processing fix verification
- **test_dataset_name.py** - Dataset name handling test

### Workflow Tests
- **test_workflow.py** - LangGraph workflow orchestration tests
- **test_pipeline.py** - Full pipeline integration tests
- **test_phase3_ui.py** - Phase 3 UI component tests

## Demo Files

### Interactive Demos
- **demo_enhancements.py** - Demo of UI/UX enhancements (progress tracking, quality viz)
- **demo_export.py** - Export functionality demonstration
- **demo_workflow.py** - Workflow system demonstration

## Running Tests

### Individual Test
```bash
python tests/test_export.py
```

### All Tests (if using pytest)
```bash
pytest tests/
```

### Demo Files
```bash
python tests/demo_export.py
```

## Notes

- Tests may require sample datasets in `data/uploads/`
- Ensure `.env` file is configured with GROQ_API_KEY
- Some tests require internet connection for API calls
- Demo files provide interactive examples of features

## Test Data

Sample datasets for testing should be placed in:
- `data/uploads/` - For upload simulation tests
- `tests/fixtures/` - For test-specific data (if needed)

## Adding New Tests

When adding new test files:
1. Follow naming convention: `test_*.py` or `demo_*.py`
2. Add description to this README
3. Ensure tests are self-contained
4. Include sample data or data generation
5. Document any special requirements
