# Presentation Generation Scripts

This directory contains Python scripts to automatically generate presentation materials for the EDA Pipeline project.

## Scripts

### 1. `create_presentation.py`
**Purpose**: Generate comprehensive PowerPoint presentation

**Output**: `EDA_Pipeline_Presentation_YYYYMMDD_HHMMSS.pptx` in `docs/presentations/`

**Content Generated**:
- 18 professional slides covering:
  - Title and agenda
  - Project overview and features
  - System architecture
  - Detailed agent descriptions
  - Human-in-the-Loop approval gates
  - Workflows and use cases
  - Tech stack
  - Best practices and roadmap

**Usage**:
```bash
python create_presentation.py
```

**Requirements**: `python-pptx`

---

### 2. `create_architecture_diagram.py`
**Purpose**: Generate high-resolution system architecture diagram

**Output**: `EDA_Pipeline_Architecture.png` in `docs/presentations/assets/`

**Features**:
- 300 DPI resolution
- 16" x 12" size
- Color-coded layers (UI, Orchestration, Agents, Data Layer)
- Complete tech stack annotations
- Professional styling with arrows and labels

**Usage**:
```bash
python create_architecture_diagram.py
```

**Requirements**: `matplotlib`, `pillow`

---

## Installation

Install all required dependencies:

```bash
pip install python-pptx matplotlib pillow
```

Or install separately:

```bash
# For PowerPoint generation
pip install python-pptx

# For diagram generation
pip install matplotlib pillow
```

## Quick Start

Generate all materials at once:

```bash
# From project root
cd docs/presentations/scripts

# Generate presentation
python create_presentation.py

# Generate diagram
python create_architecture_diagram.py

# Return to project root
cd ../../..
```

## Customization Guide

### Modifying Presentation Slides

Edit `create_presentation.py`:

```python
def create_custom_slide(prs):
    """Add your custom slide"""
    slide_layout = prs.slide_layouts[1]  # Title and content
    slide = prs.slides.add_slide(slide_layout)
    
    title = slide.shapes.title
    title.text = "Your Custom Title"
    
    content = slide.placeholders[1]
    # Add your content here
```

### Modifying Architecture Diagram

Edit `create_architecture_diagram.py`:

```python
# Change colors
color_ui = '#3498db'  # Blue - modify hex code
color_agents = '#2ecc71'  # Green - modify hex code

# Change layout
left = Inches(3)  # X position
top = Inches(9.5)  # Y position
width = Inches(10)  # Width
height = Inches(1.2)  # Height
```

## Output Examples

### PowerPoint Structure
1. Title Slide
2. Agenda
3. Project Overview
4. Key Features (v3.3, v3.2, v3.1)
5. System Architecture
6. Agents Overview
7. ProfileAgent Details
8. QualityAgent Details
9. TransformAgent Details
10. Approval Gates Feature
11. Available Workflows
12. Tech Stack
13. Export Capabilities
14. Use Case Example (Titanic)
15. Best Practices
16. Future Roadmap
17. Conclusion
18. Thank You

### Architecture Diagram Layers
1. **Top**: Streamlit UI (Blue)
2. **Orchestration**: LangGraph (Red)
3. **Agents**: 6 specialized agents (Green)
4. **Data Layer**: Pandas/DuckDB (Purple)
5. **Bottom**: Data Sources (Gray)
- **Side Panels**: Visualization & Statistics libraries (Orange)

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'pptx'`
```bash
pip install python-pptx
```

**Issue**: `ModuleNotFoundError: No module named 'matplotlib'`
```bash
pip install matplotlib pillow
```

**Issue**: Unicode errors on Windows
- Scripts have been updated to avoid emoji characters in console output
- If you see encoding errors, ensure your terminal supports UTF-8

**Issue**: Files not appearing in expected location
- Check that you're running scripts from the correct directory
- Output paths are relative to script execution location

## Best Practices

1. **Before Important Events**: Regenerate materials to ensure latest features are included
2. **Version Control**: Keep timestamped files for historical reference
3. **Consistency**: Update both scripts when project changes significantly
4. **Testing**: Run scripts after major feature additions to verify output
5. **Documentation**: Update slide content in `create_presentation.py` when features change

## Integration with CI/CD

These scripts can be integrated into automated workflows:

```bash
# In CI/CD pipeline
cd docs/presentations/scripts
python create_presentation.py
python create_architecture_diagram.py

# Archive generated files
tar -czf presentations_$(date +%Y%m%d).tar.gz ../EDA_Pipeline_Presentation_*.pptx ../assets/
```

## Maintenance

- Review and update content quarterly or with major releases
- Verify all technical details match current implementation
- Update version numbers and dates
- Test script execution after dependency updates

---

**Note**: These scripts are independent of the main EDA Pipeline application and only needed for generating marketing/documentation materials.
