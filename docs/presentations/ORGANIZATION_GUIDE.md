# Presentation Materials Organization Guide

This document explains how presentation and marketing materials are organized in the EDA Pipeline project.

## Recommended Structure

```
docs/presentations/
├── README.md                              # Main documentation for presentations
├── ORGANIZATION_GUIDE.md                  # This file - explains organization
├── scripts/                               # Generator scripts
│   ├── README.md                          # Script documentation
│   ├── create_presentation.py             # PowerPoint generator
│   └── create_architecture_diagram.py     # Diagram generator
├── assets/                                # Generated images and diagrams
│   ├── EDA_Pipeline_Architecture.png      # Architecture diagram
│   └── [future diagrams]                  # Additional visual assets
└── *.pptx                                 # Generated PowerPoint files (timestamped)
```

## Why This Structure?

### 1. **Centralized Location** (`docs/presentations/`)
- **Benefit**: All presentation materials in one place
- **Reasoning**: Easy to find and maintain
- **Alternative Considered**: Root directory - rejected because it clutters main project structure

### 2. **Separated Scripts** (`scripts/` subdirectory)
- **Benefit**: Separates generators from generated content
- **Reasoning**: Keeps source code separate from outputs
- **Alternative Considered**: Root of presentations - rejected because it mixes code with documents

### 3. **Assets Folder** (`assets/` subdirectory)
- **Benefit**: Dedicated location for reusable images
- **Reasoning**: Images can be used across multiple presentations and documents
- **Alternative Considered**: Inline with presentations - rejected because it reduces reusability

### 4. **Documentation at Each Level**
- **presentations/README.md**: Overview and usage guide
- **scripts/README.md**: Technical details for generators
- **Benefit**: Context-specific documentation where needed

## File Naming Conventions

### PowerPoint Presentations
**Format**: `EDA_Pipeline_Presentation_YYYYMMDD_HHMMSS.pptx`

**Example**: `EDA_Pipeline_Presentation_20260723_093045.pptx`

**Reasoning**:
- Timestamp prevents accidental overwrites
- Easy to identify latest version
- Useful for version history

### Architecture Diagrams
**Format**: `EDA_Pipeline_Architecture.png`

**Reasoning**:
- Static name for consistent referencing
- Older versions can be backed up manually if needed
- Usually only one "current" version needed

### Generator Scripts
**Format**: `create_[artifact_type].py`

**Examples**:
- `create_presentation.py`
- `create_architecture_diagram.py`

**Reasoning**:
- Clear purpose from filename
- Follows Python naming conventions
- Easy to understand what each script generates

## Integration with Main Project

### Project Structure Reference
The presentations directory integrates into the main project structure:

```
test/                          # Project root
├── src/                       # Source code
├── tests/                     # Tests and demos
├── data/                      # Data files
└── docs/                      # ALL documentation
    ├── presentations/         # ✨ Presentations (NEW)
    ├── *.md                   # Technical docs
    └── ...
```

### Main README Integration
The main `README.md` now includes:
- Reference to presentations in Project Structure section
- Link in Documentation section
- Maintains consistency with overall documentation approach

## Best Practices

### 1. **Version Control**
✅ **DO**: Keep timestamped presentation files for important milestones
❌ **DON'T**: Commit every single generated file - clean up old versions periodically

### 2. **Regeneration Workflow**
✅ **DO**: Regenerate before demos, meetings, releases
❌ **DON'T**: Manually edit PowerPoint - always update the script instead

### 3. **Asset Management**
✅ **DO**: Store reusable images in `assets/`
❌ **DON'T**: Duplicate images across multiple locations

### 4. **Documentation Updates**
✅ **DO**: Update scripts when features change
❌ **DON'T**: Let presentations get out of sync with actual features

## Comparison with Alternatives

### Alternative 1: Root Directory
```
test/
├── EDA_Pipeline_Presentation.pptx  ❌
├── architecture.png                ❌
├── create_presentation.py          ❌
└── ...
```
**Problem**: Clutters root, mixes code with artifacts, poor organization

### Alternative 2: Separate Top-Level Directory
```
test/
├── src/
├── docs/
├── presentations/                  ⚠️
│   └── ...
└── ...
```
**Problem**: Creates top-level clutter, separates from documentation

### Alternative 3: Inside Data Directory
```
test/
└── data/
    └── presentations/              ❌
        └── ...
```
**Problem**: Wrong semantic location - presentations aren't "data"

### ✅ Chosen Solution: Inside Docs Directory
```
test/
└── docs/
    └── presentations/              ✅
        ├── scripts/
        ├── assets/
        └── *.pptx
```
**Advantages**:
- Logical grouping with documentation
- Clean project root
- Clear separation of concerns
- Easy to find and maintain

## Future Expansion

This structure easily accommodates future materials:

```
docs/presentations/
├── scripts/
│   ├── create_presentation.py
│   ├── create_architecture_diagram.py
│   ├── create_infographic.py              # NEW
│   └── create_comparison_chart.py         # NEW
├── assets/
│   ├── EDA_Pipeline_Architecture.png
│   ├── workflow_diagram.png               # NEW
│   ├── logo.png                           # NEW
│   └── screenshots/                       # NEW
│       ├── dashboard.png
│       └── approval_gate.png
├── templates/                             # NEW
│   └── slide_template.pptx
└── archives/                              # NEW
    └── 2026_Q3/
        └── old_presentations.pptx
```

## Quick Reference

### Generate New Presentation
```bash
cd docs/presentations/scripts
python create_presentation.py
```

### Generate Architecture Diagram
```bash
cd docs/presentations/scripts
python create_architecture_diagram.py
```

### Find Latest Presentation
```bash
# Windows PowerShell
Get-ChildItem docs/presentations/*.pptx | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

### Clean Up Old Presentations (Keep Last 3)
```bash
# Windows PowerShell
Get-ChildItem docs/presentations/*.pptx | Sort-Object LastWriteTime -Descending | Select-Object -Skip 3 | Remove-Item
```

## Summary

**Best Location**: `docs/presentations/`

**Reasoning**:
1. ✅ Logical grouping with documentation
2. ✅ Clean project structure
3. ✅ Easy to find and maintain
4. ✅ Scalable for future materials
5. ✅ Follows common project organization patterns

**Key Principle**: Keep generated materials separate from source code but close to related documentation.

---

**Established**: July 2026  
**Last Updated**: July 2026  
**Version**: 1.0
