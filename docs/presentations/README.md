# Presentations & Marketing Materials

This directory contains presentation files, diagrams, and scripts for generating marketing/documentation materials for the EDA Pipeline project.

## Directory Structure

```
presentations/
├── README.md                              # This file
├── scripts/                               # Python scripts to generate materials
│   ├── create_presentation.py             # Generate PowerPoint presentation
│   └── create_architecture_diagram.py     # Generate architecture diagram PNG
├── assets/                                # Generated images and diagrams
│   └── EDA_Pipeline_Architecture.png      # System architecture diagram
└── EDA_Pipeline_Presentation_*.pptx       # Generated PowerPoint files
```

## Files Overview

### 📊 PowerPoint Presentations

**`EDA_Pipeline_Presentation_YYYYMMDD_HHMMSS.pptx`**
- Comprehensive 18-slide presentation covering:
  - Project overview and features
  - System architecture
  - All 6 specialized agents
  - Human-in-the-Loop approval gates
  - Tech stack and workflows
  - Use cases and best practices
  - Future roadmap

### 🎨 Assets

**`assets/EDA_Pipeline_Architecture.png`**
- High-resolution (300 DPI) system architecture diagram
- Shows 5-layer architecture with complete tech stack
- Color-coded components (UI, Orchestration, Agents, Data Layer)
- Includes all libraries and technologies used
- Ready for presentations, documentation, or reports

## How to Use

### Regenerate Presentation

```bash
cd docs/presentations/scripts
python create_presentation.py
```

This will create a new PowerPoint file with timestamp in the `docs/presentations/` directory.

### Regenerate Architecture Diagram

```bash
cd docs/presentations/scripts
python create_architecture_diagram.py
```

This will create/update `EDA_Pipeline_Architecture.png` in the `assets/` directory.

## Requirements

To run the generator scripts, install the required libraries:

```bash
pip install python-pptx matplotlib pillow
```

These are optional dependencies only needed for generating presentation materials, not for running the main EDA Pipeline application.

## Customization

### Modify Presentation Content

Edit `scripts/create_presentation.py` to:
- Add/remove slides
- Update content and text
- Change styling and colors
- Modify layout and formatting

### Modify Architecture Diagram

Edit `scripts/create_architecture_diagram.py` to:
- Change colors and styling
- Update component labels
- Adjust layout and positioning
- Add/remove layers or components

## Best Practices

1. **Version Control**: Keep timestamped versions of presentations for tracking changes
2. **Regenerate Before Important Events**: Always regenerate materials before demos, meetings, or releases to ensure latest information
3. **Update Scripts**: When project features change, update the generator scripts to reflect new capabilities
4. **Consistent Branding**: Maintain consistent colors, fonts, and styling across all materials

## Use Cases

### For Stakeholder Meetings
Use the PowerPoint presentation to:
- Explain project architecture
- Demonstrate features and capabilities
- Show roadmap and future plans

### For Documentation
Use the architecture diagram in:
- Technical documentation
- README files
- Wiki pages
- Developer onboarding materials

### For Marketing
Both materials can be used for:
- Conference presentations
- Blog posts
- Social media content
- Portfolio showcases

## Integration with Main Documentation

These materials complement the main documentation in `docs/`:
- **Technical Docs**: `docs/*.md` - Detailed implementation guides
- **Presentations**: `docs/presentations/` - Visual materials for communication
- **Code Examples**: `tests/demo_*.py` - Interactive demonstrations

## Notes

- Generated files have timestamps to prevent overwriting
- High-resolution outputs (300 DPI) suitable for printing
- All scripts are standalone and don't require the main application
- Materials can be regenerated anytime as project evolves

---

**Last Updated**: July 2026  
**Version**: 3.3
