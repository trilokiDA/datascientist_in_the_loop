"""
Phase 3 Streamlit UI - Complete EDA Pipeline with All 6 Agents
Comprehensive interface with visualizations, feature analysis, and statistical tests
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.dataset_handle import DatasetHandle
from src.agents import (
    ProfileAgent, QualityAgent, TransformAgent,
    VisualizationAgent, FeatureAgent, StatAgent
)
from src.utils.helpers import generate_id, get_timestamp
from src.ui.components import (
    create_workflow_tracker,
    WorkflowProgressTracker,
    PROGRESS_TRACKER_CSS,
    AGENT_STEPS
)
import os

# Page config
st.set_page_config(
    page_title="EDA Pipeline - Complete Suite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .agent-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .metric-box {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Add progress tracker CSS
st.markdown(PROGRESS_TRACKER_CSS, unsafe_allow_html=True)

# Initialize session state
if "dataset_handle" not in st.session_state:
    st.session_state.dataset_handle = None

if "session_id" not in st.session_state:
    st.session_state.session_id = generate_id("session")

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}

if "workflow_running" not in st.session_state:
    st.session_state.workflow_running = False

if "workflow_tracker" not in st.session_state:
    st.session_state.workflow_tracker = None


def display_header():
    """Display app header"""
    st.markdown('<div class="main-header">🚀 EDA Pipeline - Complete Agent Suite</div>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown("**📊 Profile**")
    with col2:
        st.markdown("**✅ Quality**")
    with col3:
        st.markdown("**🔧 Transform**")
    with col4:
        st.markdown("**🎨 Visualize**")
    with col5:
        st.markdown("**🔍 Features**")
    with col6:
        st.markdown("**📈 Statistics**")

    st.divider()


def display_sidebar():
    """Enhanced sidebar with all options"""
    with st.sidebar:
        st.header("📁 Dataset")

        uploaded_file = st.file_uploader(
            "Upload CSV File",
            type=['csv'],
            help="Upload your dataset for comprehensive analysis"
        )

        if uploaded_file is not None:
            # Save and load dataset
            upload_dir = Path("data/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)

            file_path = upload_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            if st.session_state.dataset_handle is None or \
               st.session_state.dataset_handle.path != str(file_path):
                st.session_state.dataset_handle = DatasetHandle(str(file_path))
                st.success(f"✅ Loaded: {uploaded_file.name}")

                # Display quick stats
                info = st.session_state.dataset_handle.get_info()

                st.markdown("### Quick Stats")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows", f"{info['rows']:,}")
                    st.metric("Columns", info['columns'])
                with col2:
                    st.metric("Size", info['file_size_formatted'])
                    st.metric("Mode", info['mode'].replace('_', ' ').title())

        st.divider()

        # Analysis options
        st.header("🔄 Analysis Options")

        if st.session_state.dataset_handle is None:
            st.warning("⚠️ Upload a dataset first")
        else:
            analysis_type = st.radio(
                "Select Analysis Type",
                [
                    "🎯 Quick Analysis (All Agents)",
                    "📊 Individual Agent",
                    "🔬 Deep Dive Workflow",
                    "🤖 ML Preparation"
                ]
            )

            if analysis_type == "📊 Individual Agent":
                agent_choice = st.selectbox(
                    "Choose Agent",
                    [
                        "ProfileAgent",
                        "QualityAgent",
                        "TransformAgent",
                        "VisualizationAgent",
                        "FeatureAgent",
                        "StatAgent"
                    ]
                )

                if st.button("🚀 Run Selected Agent", use_container_width=True, type="primary"):
                    run_single_agent(agent_choice)

            elif analysis_type == "🎯 Quick Analysis (All Agents)":
                if st.button("🚀 Run Complete Analysis", use_container_width=True, type="primary"):
                    run_complete_analysis()

            elif analysis_type == "🔬 Deep Dive Workflow":
                if st.button("🚀 Run Deep Dive", use_container_width=True, type="primary"):
                    run_deep_dive_workflow()

            elif analysis_type == "🤖 ML Preparation":
                if st.button("🚀 Prepare for ML", use_container_width=True, type="primary"):
                    run_ml_prep_workflow()

        st.divider()

        # Settings
        st.header("⚙️ Settings")
        show_reasoning = st.checkbox("Show Reasoning", value=True)
        show_confidence = st.checkbox("Show Confidence", value=True)
        st.session_state.show_reasoning = show_reasoning
        st.session_state.show_confidence = show_confidence


def run_single_agent(agent_name: str):
    """Run a single agent with progress tracking"""
    handle = st.session_state.dataset_handle

    # Map agent name to step ID
    agent_step_map = {
        "ProfileAgent": "profile",
        "QualityAgent": "quality",
        "TransformAgent": "transform",
        "VisualizationAgent": "visualization",
        "FeatureAgent": "feature",
        "StatAgent": "stat"
    }

    step_id = agent_step_map.get(agent_name)

    # Create a single-step tracker for this agent
    if step_id and step_id in AGENT_STEPS:
        step = AGENT_STEPS[step_id]
        tracker = WorkflowProgressTracker(f"Running {agent_name}", [step])
        st.session_state.workflow_tracker = tracker

        progress_container = st.empty()

        # Start the step
        step.start()
        with progress_container.container():
            tracker.render_compact()

        try:
            # Get context from previous results
            context = {
                "profile_results": st.session_state.analysis_results.get("profile", {}).get("result"),
                "quality_results": st.session_state.analysis_results.get("quality", {}).get("result"),
                "feature_results": st.session_state.analysis_results.get("feature", {}).get("result")
            }

            # Run agent
            if agent_name == "ProfileAgent":
                agent = ProfileAgent()
                result = agent.analyze(handle)
                st.session_state.analysis_results["profile"] = result

            elif agent_name == "QualityAgent":
                agent = QualityAgent()
                result = agent.analyze(handle, context)
                st.session_state.analysis_results["quality"] = result

            elif agent_name == "TransformAgent":
                agent = TransformAgent()
                result = agent.analyze(handle, context)
                st.session_state.analysis_results["transform"] = result

            elif agent_name == "VisualizationAgent":
                agent = VisualizationAgent()
                result = agent.analyze(handle, context)
                st.session_state.analysis_results["visualization"] = result

            elif agent_name == "FeatureAgent":
                agent = FeatureAgent()
                result = agent.analyze(handle, context)
                st.session_state.analysis_results["feature"] = result

            elif agent_name == "StatAgent":
                agent = StatAgent()
                result = agent.analyze(handle, context)
                st.session_state.analysis_results["stat"] = result

            # Complete the step
            step.complete()

            with progress_container.container():
                tracker.render_compact()

            st.success(f"✅ {agent_name} completed in {step.duration:.1f}s!")

        except Exception as e:
            step.fail(str(e))
            with progress_container.container():
                tracker.render_compact()
            st.error(f"❌ {agent_name} failed: {str(e)}")

    st.rerun()


def run_complete_analysis():
    """Run all agents in sequence with progress tracking"""
    handle = st.session_state.dataset_handle

    # Create workflow tracker
    tracker = create_workflow_tracker("complete_analysis")
    st.session_state.workflow_tracker = tracker
    st.session_state.workflow_running = True

    # Create progress container
    progress_container = st.empty()

    # Agent configuration
    agent_configs = [
        ("profile", "ProfileAgent", ProfileAgent()),
        ("quality", "QualityAgent", QualityAgent()),
        ("visualization", "VisualizationAgent", VisualizationAgent()),
        ("feature", "FeatureAgent", FeatureAgent()),
        ("stat", "StatAgent", StatAgent()),
        ("transform", "TransformAgent", TransformAgent())
    ]

    # Run each agent
    for step_id, agent_name, agent in agent_configs:
        # Find the step
        step = next((s for s in tracker.steps if s.id == step_id), None)
        if not step:
            continue

        # Start the step
        step.start()

        # Render progress
        with progress_container.container():
            tracker.render()

        try:
            # Get context
            context = {
                "profile_results": st.session_state.analysis_results.get("profile", {}).get("result"),
                "quality_results": st.session_state.analysis_results.get("quality", {}).get("result"),
                "feature_results": st.session_state.analysis_results.get("feature", {}).get("result")
            }

            # Run agent
            result = agent.analyze(handle, context)

            # Store result
            st.session_state.analysis_results[step_id] = result

            # Complete the step
            step.complete()

        except Exception as e:
            # Mark step as failed
            step.fail(str(e))
            st.error(f"❌ {agent_name} failed: {str(e)}")
            break

        # Update progress display
        with progress_container.container():
            tracker.render()

    # Final render
    with progress_container.container():
        tracker.render()

    # Check if all completed successfully
    if tracker.completed_count == tracker.total_steps:
        st.success("🎉 All agents completed successfully!")
        st.balloons()

    st.session_state.workflow_running = False
    st.rerun()


def run_deep_dive_workflow():
    """Deep dive analysis workflow (without transform)"""
    handle = st.session_state.dataset_handle

    # Create workflow tracker for deep dive (no transform)
    tracker = create_workflow_tracker("deep_dive")
    st.session_state.workflow_tracker = tracker
    st.session_state.workflow_running = True

    progress_container = st.empty()

    agent_configs = [
        ("profile", "ProfileAgent", ProfileAgent()),
        ("quality", "QualityAgent", QualityAgent()),
        ("visualization", "VisualizationAgent", VisualizationAgent()),
        ("feature", "FeatureAgent", FeatureAgent()),
        ("stat", "StatAgent", StatAgent())
    ]

    for step_id, agent_name, agent in agent_configs:
        step = next((s for s in tracker.steps if s.id == step_id), None)
        if not step:
            continue

        step.start()
        with progress_container.container():
            tracker.render()

        try:
            context = {
                "profile_results": st.session_state.analysis_results.get("profile", {}).get("result"),
                "quality_results": st.session_state.analysis_results.get("quality", {}).get("result"),
                "feature_results": st.session_state.analysis_results.get("feature", {}).get("result")
            }

            result = agent.analyze(handle, context)
            st.session_state.analysis_results[step_id] = result
            step.complete()

        except Exception as e:
            step.fail(str(e))
            st.error(f"❌ {agent_name} failed: {str(e)}")
            break

        with progress_container.container():
            tracker.render()

    with progress_container.container():
        tracker.render()

    if tracker.completed_count == tracker.total_steps:
        st.success("🎉 Deep dive analysis completed!")
        st.balloons()

    st.session_state.workflow_running = False
    st.rerun()


def run_ml_prep_workflow():
    """ML preparation workflow (profile, quality, feature, transform)"""
    handle = st.session_state.dataset_handle

    # Create workflow tracker for ML prep
    tracker = create_workflow_tracker("ml_prep")
    st.session_state.workflow_tracker = tracker
    st.session_state.workflow_running = True

    progress_container = st.empty()

    agent_configs = [
        ("profile", "ProfileAgent", ProfileAgent()),
        ("quality", "QualityAgent", QualityAgent()),
        ("feature", "FeatureAgent", FeatureAgent()),
        ("transform", "TransformAgent", TransformAgent())
    ]

    for step_id, agent_name, agent in agent_configs:
        step = next((s for s in tracker.steps if s.id == step_id), None)
        if not step:
            continue

        step.start()
        with progress_container.container():
            tracker.render()

        try:
            context = {
                "profile_results": st.session_state.analysis_results.get("profile", {}).get("result"),
                "quality_results": st.session_state.analysis_results.get("quality", {}).get("result"),
                "feature_results": st.session_state.analysis_results.get("feature", {}).get("result")
            }

            result = agent.analyze(handle, context)
            st.session_state.analysis_results[step_id] = result
            step.complete()

        except Exception as e:
            step.fail(str(e))
            st.error(f"❌ {agent_name} failed: {str(e)}")
            break

        with progress_container.container():
            tracker.render()

    with progress_container.container():
        tracker.render()

    if tracker.completed_count == tracker.total_steps:
        st.success("🎉 ML preparation completed!")
        st.balloons()

    st.session_state.workflow_running = False
    st.rerun()


def display_results():
    """Display analysis results in tabs"""
    if not st.session_state.analysis_results:
        st.info("👆 Upload a dataset and run analysis to see results")
        return

    # Create tabs for different views
    tabs = st.tabs([
        "📊 Overview",
        "📈 Profile",
        "✅ Quality",
        "🎨 Visualizations",
        "🔍 Features",
        "📉 Statistics",
        "🔧 Transformations"
    ])

    with tabs[0]:
        display_overview()

    with tabs[1]:
        if "profile" in st.session_state.analysis_results:
            display_profile_results()
        else:
            st.info("Run ProfileAgent to see results")

    with tabs[2]:
        if "quality" in st.session_state.analysis_results:
            display_quality_results()
        else:
            st.info("Run QualityAgent to see results")

    with tabs[3]:
        if "visualization" in st.session_state.analysis_results:
            display_visualization_results()
        else:
            st.info("Run VisualizationAgent to see results")

    with tabs[4]:
        if "feature" in st.session_state.analysis_results:
            display_feature_results()
        else:
            st.info("Run FeatureAgent to see results")

    with tabs[5]:
        if "stat" in st.session_state.analysis_results:
            display_stat_results()
        else:
            st.info("Run StatAgent to see results")

    with tabs[6]:
        if "transform" in st.session_state.analysis_results:
            display_transform_results()
        else:
            st.info("Run TransformAgent to see results")


def display_overview():
    """Display overview of all results"""
    st.header("📊 Analysis Overview")

    # Count completed agents
    completed = len(st.session_state.analysis_results)
    total = 6

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Completed Agents", f"{completed}/{total}")

    with col2:
        completion = (completed / total) * 100
        st.metric("Completion", f"{completion:.0f}%")

    with col3:
        if st.session_state.dataset_handle:
            info = st.session_state.dataset_handle.get_info()
            st.metric("Dataset Rows", f"{info['rows']:,}")

    st.divider()

    # Show agent status
    st.subheader("Agent Status")

    agent_status = {
        "ProfileAgent": "profile" in st.session_state.analysis_results,
        "QualityAgent": "quality" in st.session_state.analysis_results,
        "TransformAgent": "transform" in st.session_state.analysis_results,
        "VisualizationAgent": "visualization" in st.session_state.analysis_results,
        "FeatureAgent": "feature" in st.session_state.analysis_results,
        "StatAgent": "stat" in st.session_state.analysis_results
    }

    cols = st.columns(3)
    for idx, (agent, completed) in enumerate(agent_status.items()):
        with cols[idx % 3]:
            status = "✅" if completed else "⏳"
            st.markdown(f"{status} **{agent}**")
            if completed:
                result = st.session_state.analysis_results.get(agent.lower().replace("agent", ""))
                if result and st.session_state.get("show_confidence", True):
                    st.caption(f"Confidence: {result['confidence']:.0%}")


def display_profile_results():
    """Display profile agent results"""
    st.header("📈 Dataset Profile")

    result = st.session_state.analysis_results["profile"]
    data = result["result"]

    # Basic info
    st.subheader("Basic Information")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Rows", f"{data['basic_info']['rows']:,}")
    with col2:
        st.metric("Columns", data['basic_info']['columns'])
    with col3:
        st.metric("File Size", data['basic_info']['file_size'])
    with col4:
        # Calculate total missing from missing_info
        total_missing = sum(v['count'] for v in data.get('missing_info', {}).values())
        total_cells = data['basic_info']['rows'] * data['basic_info']['columns']
        missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
        st.metric("Missing", f"{missing_pct:.1f}%")

    # Column types
    st.subheader("Column Types")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Numeric", len(data['column_types'].get('numeric', [])))
    with col2:
        st.metric("Categorical", len(data['column_types'].get('categorical', [])))
    with col3:
        st.metric("Datetime", len(data['column_types'].get('datetime', [])))

    # Issues
    if data.get('issues'):
        st.subheader("⚠️ Issues Detected")
        issues = data['issues']

        if issues.get('high_missing_cols'):
            st.warning(f"**High Missing:** {', '.join(issues['high_missing_cols'][:5])}")

        if issues.get('high_cardinality_cols'):
            st.warning(f"**High Cardinality:** {', '.join(issues['high_cardinality_cols'][:5])}")

        if issues.get('low_cardinality_cols'):
            st.info(f"**Low Cardinality:** {', '.join(issues['low_cardinality_cols'][:5])}")

    # Explainability
    if st.session_state.get("show_reasoning", True):
        with st.expander("🧠 Agent Reasoning"):
            st.markdown(f"**Reasoning:** {result['reasoning']}")
            st.markdown(f"**Impact:** {result['impact']}")
            st.markdown("**Recommendations:**")
            for rec in result['recommendations']:
                st.markdown(f"- {rec}")


def display_quality_results():
    """Display quality agent results"""
    st.header("✅ Data Quality Assessment")

    result = st.session_state.analysis_results["quality"]
    data = result["result"]

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        dup_pct = data['duplicates']['duplicate_percentage']
        st.metric("Duplicates", f"{dup_pct:.1f}%",
                 delta=f"-{data['duplicates']['duplicate_rows']} rows" if dup_pct > 0 else "None")

    with col2:
        outlier_cols = data['outliers']['columns_with_outliers']
        st.metric("Outlier Columns", outlier_cols)

    with col3:
        inconsistencies = data['inconsistencies']['inconsistency_count']
        st.metric("Inconsistencies", inconsistencies)

    with col4:
        type_issues = data['data_types']['type_issue_count']
        st.metric("Type Issues", type_issues)

    # Detailed outlier info
    if data['outliers']['has_outliers']:
        st.subheader("📊 Outlier Details")
        outlier_data = []
        for col, details in list(data['outliers']['outlier_details'].items())[:5]:
            outlier_data.append({
                "Column": col,
                "IQR Outliers": details['iqr_outliers'],
                "Percentage": f"{details['iqr_percentage']:.1f}%",
                "Range": f"[{details['min']:.2f}, {details['max']:.2f}]"
            })

        st.dataframe(pd.DataFrame(outlier_data), use_container_width=True)

    # Explainability
    if st.session_state.get("show_reasoning", True):
        with st.expander("🧠 Agent Reasoning"):
            st.markdown(f"**Reasoning:** {result['reasoning']}")
            st.markdown(f"**Impact:** {result['impact']}")
            st.markdown("**Recommendations:**")
            for rec in result['recommendations']:
                st.markdown(f"- {rec}")


def display_visualization_results():
    """Display visualization results with inline images"""
    st.header("🎨 Visualizations")

    result = st.session_state.analysis_results["visualization"]
    data = result["result"]

    st.metric("Total Plots Generated", data['total_plots'])

    # Display plots by type
    plot_types = {}
    for plot in data['plots']:
        plot_type = plot['type']
        if plot_type not in plot_types:
            plot_types[plot_type] = []
        plot_types[plot_type].append(plot)

    for plot_type, plots in plot_types.items():
        st.subheader(f"{plot_type.replace('_', ' ').title()}")

        # Display plots in columns
        cols = st.columns(min(2, len(plots)))
        for idx, plot in enumerate(plots):
            with cols[idx % 2]:
                try:
                    image = Image.open(plot['path'])
                    st.image(image, caption=plot.get('column', plot_type), use_container_width=True)

                    # Show statistics if available
                    if 'statistics' in plot:
                        stats = plot['statistics']
                        st.caption(f"Mean: {stats['mean']:.2f} | Median: {stats['median']:.2f} | Std: {stats['std']:.2f}")

                    if 'interpretation' in plot:
                        st.info(plot['interpretation'])

                except Exception as e:
                    st.error(f"Could not load plot: {e}")

    # Explainability
    if st.session_state.get("show_reasoning", True):
        with st.expander("🧠 Agent Reasoning"):
            st.markdown(f"**Reasoning:** {result['reasoning']}")
            st.markdown(f"**Impact:** {result['impact']}")
            st.markdown("**Recommendations:**")
            for rec in result['recommendations']:
                st.markdown(f"- {rec}")


def display_feature_results():
    """Display feature analysis results"""
    st.header("🔍 Feature Analysis")

    result = st.session_state.analysis_results["feature"]
    data = result["result"]

    # Correlation summary
    st.subheader("Correlations")
    col1, col2, col3 = st.columns(3)

    corr_data = data['correlations']
    with col1:
        st.metric("Numeric Features", corr_data['num_numeric_features'])
    with col2:
        st.metric("Strong Correlations", len(corr_data['strong_correlations']))
    with col3:
        st.metric("Moderate Correlations", len(corr_data['moderate_correlations']))

    # Strong correlations
    if corr_data['strong_correlations']:
        st.markdown("**Strong Correlations (|r| > 0.7):**")
        corr_df = pd.DataFrame(corr_data['strong_correlations'])
        st.dataframe(corr_df, use_container_width=True)

    # Multicollinearity
    st.subheader("Multicollinearity")
    multi_data = data['multicollinearity']

    severity_color = {"none": "🟢", "moderate": "🟡", "high": "🔴"}
    st.markdown(f"{severity_color.get(multi_data['severity'], '⚪')} **Severity:** {multi_data['severity'].title()}")

    if multi_data.get('multicollinear_pairs'):
        st.warning("⚠️ Multicollinear pairs detected")
        pairs_df = pd.DataFrame(multi_data['multicollinear_pairs'])
        st.dataframe(pairs_df, use_container_width=True)

    # Engineering suggestions
    st.subheader("🛠️ Engineering Suggestions")
    eng_data = data['engineering_suggestions']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("High Priority", eng_data['by_priority']['high'])
    with col2:
        st.metric("Medium Priority", eng_data['by_priority']['medium'])
    with col3:
        st.metric("Low Priority", eng_data['by_priority']['low'])

    # Show suggestions
    suggestions = eng_data['suggestions']
    high_priority = [s for s in suggestions if s['priority'] == 'high']

    if high_priority:
        st.markdown("**High Priority Suggestions:**")
        for suggestion in high_priority[:5]:
            with st.expander(f"{suggestion['type']} - {suggestion.get('feature', 'Multiple features')}"):
                st.markdown(f"**Reasoning:** {suggestion['reasoning']}")
                st.markdown(f"**Priority:** {suggestion['priority']}")

    # Explainability
    if st.session_state.get("show_reasoning", True):
        with st.expander("🧠 Agent Reasoning"):
            st.markdown(f"**Reasoning:** {result['reasoning']}")
            st.markdown(f"**Impact:** {result['impact']}")
            st.markdown("**Recommendations:**")
            for rec in result['recommendations']:
                st.markdown(f"- {rec}")


def display_stat_results():
    """Display statistical analysis results"""
    st.header("📉 Statistical Analysis")

    result = st.session_state.analysis_results["stat"]
    data = result["result"]

    # Normality tests
    st.subheader("Normality Tests")
    norm_data = data['normality_tests']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Features Tested", norm_data['total_tested'])
    with col2:
        st.metric("Normal", norm_data['normal_features'])
    with col3:
        st.metric("Non-Normal", norm_data['non_normal_features'])

    if norm_data['results']:
        st.markdown("**Sample Results:**")
        norm_df_data = []
        for result_item in norm_data['results'][:5]:
            assessment = result_item['overall_assessment']
            desc = result_item.get('descriptive', {})
            norm_df_data.append({
                "Feature": result_item['feature'],
                "Is Normal": "✅" if assessment['is_likely_normal'] else "❌",
                "Skewness": f"{desc.get('skewness', 0):.2f}",
                "Kurtosis": f"{desc.get('kurtosis', 0):.2f}",
                "Confidence": assessment['confidence']
            })

        st.dataframe(pd.DataFrame(norm_df_data), use_container_width=True)

    # Hypothesis tests
    st.subheader("Hypothesis Tests")
    hyp_data = data['hypothesis_tests']

    st.metric("Tests Performed", hyp_data['total_tests'])

    if hyp_data['tests']:
        st.markdown("**Test Results:**")
        for test in hyp_data['tests']:
            with st.expander(f"{test['test_type']}"):
                st.markdown(f"**Interpretation:** {test['interpretation']}")
                st.markdown(f"**P-value:** {test.get('p_value', 'N/A')}")
                if 'feature1' in test:
                    st.markdown(f"**Features:** {test.get('feature1', '')} & {test.get('feature2', '')}")

    # Outlier statistics
    st.subheader("Outlier Statistics")
    outlier_data = data['outlier_statistics']

    if outlier_data['outlier_statistics']:
        outlier_df_data = []
        for stat in outlier_data['outlier_statistics'][:5]:
            outlier_df_data.append({
                "Feature": stat['feature'],
                "IQR Outliers": stat['iqr_outliers'],
                "Percentage": f"{stat['iqr_percentage']:.1f}%",
                "Severity": stat['severity'].title()
            })

        st.dataframe(pd.DataFrame(outlier_df_data), use_container_width=True)

    # Explainability
    if st.session_state.get("show_reasoning", True):
        with st.expander("🧠 Agent Reasoning"):
            st.markdown(f"**Reasoning:** {result['reasoning']}")
            st.markdown(f"**Impact:** {result['impact']}")
            st.markdown("**Recommendations:**")
            for rec in result['recommendations']:
                st.markdown(f"- {rec}")


def display_transform_results():
    """Display transformation proposals"""
    st.header("🔧 Transformation Proposals")

    result = st.session_state.analysis_results["transform"]
    data = result["result"]

    # Summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total", data['total_transformations'])
    with col2:
        st.metric("High Priority", data['high_priority'])
    with col3:
        st.metric("Medium Priority", data['medium_priority'])
    with col4:
        st.metric("Low Priority", data['low_priority'])

    # Group by priority
    transformations = data['transformations']

    for priority in ['high', 'medium', 'low']:
        priority_transforms = [t for t in transformations if t['priority'] == priority]

        if priority_transforms:
            st.subheader(f"{priority.title()} Priority Transformations")

            for transform in priority_transforms:
                with st.expander(f"{transform['type']} - {transform['description'][:50]}..."):
                    st.markdown(f"**Description:** {transform['description']}")
                    st.markdown(f"**Reasoning:** {transform['reasoning']}")
                    st.markdown(f"**Impact:** {transform['impact']}")
                    st.markdown(f"**Type:** {transform['type']}")

    # Explainability
    if st.session_state.get("show_reasoning", True):
        with st.expander("🧠 Agent Reasoning"):
            st.markdown(f"**Reasoning:** {result['reasoning']}")
            st.markdown(f"**Impact:** {result['impact']}")
            st.markdown("**Recommendations:**")
            for rec in result['recommendations']:
                st.markdown(f"- {rec}")


def main():
    """Main application"""
    display_header()
    display_sidebar()

    # Show progress tracker if workflow is running or just completed
    if st.session_state.workflow_tracker:
        st.markdown("---")
        with st.container():
            st.session_state.workflow_tracker.render_compact()
        st.markdown("---")

    display_results()

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p><strong>EDA Pipeline - Phase 3</strong></p>
        <p>Powered by 6 Specialized AI Agents | Built with Streamlit & LangGraph</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
