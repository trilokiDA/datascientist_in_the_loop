"""
Create a professional system architecture diagram with tech stack
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines

def create_architecture_diagram():
    """Create comprehensive architecture diagram"""

    # Create figure with white background
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')

    # Color scheme
    color_ui = '#3498db'  # Blue
    color_orchestration = '#e74c3c'  # Red
    color_agents = '#2ecc71'  # Green
    color_data = '#9b59b6'  # Purple
    color_tech = '#f39c12'  # Orange

    # Title
    ax.text(8, 11.5, 'EDA Pipeline - System Architecture',
            fontsize=28, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', edgecolor='black', linewidth=2))

    # Layer 1: Streamlit UI
    ui_box = FancyBboxPatch((3, 9.5), 10, 1.2,
                            boxstyle="round,pad=0.1",
                            edgecolor='black', facecolor=color_ui,
                            linewidth=2, alpha=0.8)
    ax.add_patch(ui_box)
    ax.text(8, 10.3, 'Streamlit UI', fontsize=18, fontweight='bold',
            ha='center', va='center', color='white')
    ax.text(8, 9.9, 'Interactive Web Interface | Progress Tracking | Approval Gates',
            fontsize=11, ha='center', va='center', color='white')

    # Tech stack for UI
    ax.text(13.5, 10.1, 'Tech:', fontsize=9, fontweight='bold', ha='left')
    ax.text(13.5, 9.8, 'Streamlit', fontsize=8, ha='left')

    # Arrow from UI to Orchestration
    arrow1 = FancyArrowPatch((8, 9.5), (8, 8.5),
                            arrowstyle='->', mutation_scale=30,
                            linewidth=3, color='black')
    ax.add_patch(arrow1)

    # Layer 2: LangGraph Orchestration
    orch_box = FancyBboxPatch((3, 7), 10, 1.3,
                              boxstyle="round,pad=0.1",
                              edgecolor='black', facecolor=color_orchestration,
                              linewidth=2, alpha=0.8)
    ax.add_patch(orch_box)
    ax.text(8, 7.9, 'LangGraph Orchestration', fontsize=18, fontweight='bold',
            ha='center', va='center', color='white')
    ax.text(8, 7.45, 'State Machine | Workflow Management | Context Passing',
            fontsize=11, ha='center', va='center', color='white')

    # Tech stack for Orchestration
    ax.text(13.5, 7.8, 'Tech:', fontsize=9, fontweight='bold', ha='left')
    ax.text(13.5, 7.55, 'LangGraph', fontsize=8, ha='left')
    ax.text(13.5, 7.3, 'SQLite', fontsize=8, ha='left')

    # Arrow from Orchestration to Agents
    arrow2 = FancyArrowPatch((8, 7), (8, 6),
                            arrowstyle='->', mutation_scale=30,
                            linewidth=3, color='black')
    ax.add_patch(arrow2)

    # Layer 3: Specialized Agents (6 boxes)
    agents = [
        ('Profile\nAgent', 1.5, 'Dataset\nProfiling'),
        ('Quality\nAgent', 4, 'Quality\nAssessment'),
        ('Transform\nAgent', 6.5, 'Data\nCleaning'),
        ('Visualize\nAgent', 9, 'Chart\nGeneration'),
        ('Feature\nAgent', 11.5, 'Feature\nEngineering'),
        ('Stat\nAgent', 14, 'Statistical\nTesting')
    ]

    for agent_name, x_pos, desc in agents:
        agent_box = FancyBboxPatch((x_pos - 0.9, 4.2), 1.8, 1.5,
                                   boxstyle="round,pad=0.05",
                                   edgecolor='black', facecolor=color_agents,
                                   linewidth=2, alpha=0.8)
        ax.add_patch(agent_box)
        ax.text(x_pos, 5.3, agent_name, fontsize=10, fontweight='bold',
                ha='center', va='center', color='white')
        ax.text(x_pos, 4.7, desc, fontsize=7,
                ha='center', va='center', color='white')

    # Label for Agents layer
    ax.text(8, 6.2, 'Specialized AI Agents', fontsize=16, fontweight='bold',
            ha='center', bbox=dict(boxstyle='round,pad=0.3',
            facecolor=color_agents, alpha=0.3, edgecolor='black'))

    # Tech stack for Agents
    ax.text(0.3, 5.2, 'LLM:', fontsize=9, fontweight='bold', ha='left')
    ax.text(0.3, 4.9, 'Groq', fontsize=8, ha='left')
    ax.text(0.3, 4.65, 'Llama 3.1', fontsize=7, ha='left')

    # Arrows from Agents to Data Layer
    for agent_name, x_pos, desc in agents:
        arrow = FancyArrowPatch((x_pos, 4.2), (x_pos, 3.3),
                               arrowstyle='->', mutation_scale=20,
                               linewidth=1.5, color='gray', alpha=0.6)
        ax.add_patch(arrow)

    # Consolidating arrow
    arrow3 = FancyArrowPatch((8, 4.2), (8, 3.3),
                            arrowstyle='->', mutation_scale=30,
                            linewidth=3, color='black')
    ax.add_patch(arrow3)

    # Layer 4: Data Layer
    data_box = FancyBboxPatch((3, 1.8), 10, 1.3,
                              boxstyle="round,pad=0.1",
                              edgecolor='black', facecolor=color_data,
                              linewidth=2, alpha=0.8)
    ax.add_patch(data_box)
    ax.text(8, 2.7, 'Data Layer', fontsize=18, fontweight='bold',
            ha='center', va='center', color='white')
    ax.text(8, 2.25, 'Intelligent Backend Switching | In-Memory ↔ Sampled Processing',
            fontsize=11, ha='center', va='center', color='white')

    # Tech stack for Data Layer
    ax.text(13.5, 2.6, 'Tech:', fontsize=9, fontweight='bold', ha='left')
    ax.text(13.5, 2.35, 'Pandas', fontsize=8, ha='left')
    ax.text(13.5, 2.1, 'DuckDB', fontsize=8, ha='left')

    # Arrow from Data Layer to File System
    arrow4 = FancyArrowPatch((8, 1.8), (8, 1.2),
                            arrowstyle='->', mutation_scale=30,
                            linewidth=3, color='black')
    ax.add_patch(arrow4)

    # Layer 5: Data Sources
    sources_box = FancyBboxPatch((3, 0.3), 10, 0.7,
                                 boxstyle="round,pad=0.05",
                                 edgecolor='black', facecolor='lightgray',
                                 linewidth=2, alpha=0.9)
    ax.add_patch(sources_box)
    ax.text(8, 0.65, 'Data Sources: CSV Files | Excel Files (.xlsx, .xls)',
            fontsize=13, fontweight='bold', ha='center', va='center')

    # Tech stack for File Support
    ax.text(13.5, 0.65, 'Tech:', fontsize=9, fontweight='bold', ha='left')
    ax.text(13.5, 0.4, 'openpyxl', fontsize=8, ha='left')

    # Left side: Visualization Libraries
    viz_box = FancyBboxPatch((0.2, 1.8), 2.3, 1.3,
                             boxstyle="round,pad=0.1",
                             edgecolor='black', facecolor=color_tech,
                             linewidth=2, alpha=0.7)
    ax.add_patch(viz_box)
    ax.text(1.35, 2.8, 'Visualization', fontsize=11, fontweight='bold',
            ha='center', va='center')
    ax.text(1.35, 2.55, 'Libraries', fontsize=10, fontweight='bold',
            ha='center', va='center')
    ax.text(1.35, 2.25, '• Plotly', fontsize=9, ha='center', va='center')
    ax.text(1.35, 2.05, '• Seaborn', fontsize=9, ha='center', va='center')
    ax.text(1.35, 1.85, '• Matplotlib', fontsize=9, ha='center', va='center')

    # Right side: Statistics & ML
    stats_box = FancyBboxPatch((13.5, 1.8), 2.3, 1.3,
                               boxstyle="round,pad=0.1",
                               edgecolor='black', facecolor=color_tech,
                               linewidth=2, alpha=0.7)
    ax.add_patch(stats_box)
    ax.text(14.65, 2.8, 'Statistics &', fontsize=11, fontweight='bold',
            ha='center', va='center')
    ax.text(14.65, 2.55, 'ML Libraries', fontsize=10, fontweight='bold',
            ha='center', va='center')
    ax.text(14.65, 2.25, '• SciPy', fontsize=9, ha='center', va='center')
    ax.text(14.65, 2.05, '• Statsmodels', fontsize=9, ha='center', va='center')
    ax.text(14.65, 1.85, '• Scikit-learn', fontsize=9, ha='center', va='center')

    # Add legend/key features box at bottom
    features_box = FancyBboxPatch((0.2, 0.05), 15.6, 0.15,
                                  boxstyle="round,pad=0.02",
                                  edgecolor='black', facecolor='lightyellow',
                                  linewidth=1, alpha=0.9)
    ax.add_patch(features_box)

    # Key features text
    features_text = '✓ Explainable AI  |  ✓ Human-in-the-Loop  |  ✓ Hybrid Scaling  |  ✓ Progress Tracking  |  ✓ Multi-Format Export  |  ✓ Workflow Flexibility'
    ax.text(8, 0.125, features_text, fontsize=9, ha='center', va='center',
            fontweight='bold')

    plt.tight_layout()

    # Save the diagram
    filename = 'EDA_Pipeline_Architecture.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nArchitecture diagram created successfully!")
    print(f"File: {filename}")
    print(f"Resolution: 300 DPI")
    print(f"Size: {fig.get_size_inches()[0]:.1f}\" x {fig.get_size_inches()[1]:.1f}\"")

    plt.close()

    return filename

if __name__ == "__main__":
    create_architecture_diagram()
