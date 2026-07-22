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
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.dataset_handle import DatasetHandle
from src.agents import (
    ProfileAgent, QualityAgent, TransformAgent,
    VisualizationAgent, FeatureAgent, StatAgent
)
from src.utils.helpers import generate_id, get_timestamp
from src.utils.export import ExportManager
from src.ui.components import (
    create_workflow_tracker,
    WorkflowProgressTracker,
    PROGRESS_TRACKER_CSS,
    AGENT_STEPS,
    display_quality_visualizations,
    display_transformation_comparison,
    ApprovalGate,
    store_user_decision
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

if "export_manager" not in st.session_state:
    st.session_state.export_manager = ExportManager()

# Approval gate workflow state
if "workflow_mode" not in st.session_state:
    st.session_state.workflow_mode = None

if "current_agent_index" not in st.session_state:
    st.session_state.current_agent_index = 0

if "waiting_for_approval" not in st.session_state:
    st.session_state.waiting_for_approval = False

if "user_decisions" not in st.session_state:
    st.session_state.user_decisions = []

if "agent_configs" not in st.session_state:
    st.session_state.agent_configs = []


def display_header():
    """Display app header"""
    st.markdown('<div class="main-header">🚀 EDA Pipeline - Complete Agent Suite</div>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown("**📊 Profile**")
    with col2:
        st.markdown("**✅ Quality**")
    with col3:
        st.markdown("**🎨 Visualize**")
    with col4:
        st.markdown("**🔍 Features**")
    with col5:
        st.markdown("**📈 Statistics**")
    with col6:
        st.markdown("**🔧 Transform**")

    st.divider()


def display_sidebar():
    """Enhanced sidebar with all options"""
    with st.sidebar:
        st.header("📁 Dataset")

        uploaded_file = st.file_uploader(
            "Upload Dataset File",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your dataset (CSV or Excel) for comprehensive analysis. For Excel files, the first sheet will be analyzed."
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
                try:
                    st.session_state.dataset_handle = DatasetHandle(str(file_path))

                    # Show appropriate message based on file type
                    file_ext = Path(uploaded_file.name).suffix.lower()
                    if file_ext in ['.xlsx', '.xls']:
                        st.success(f"✅ Loaded: {uploaded_file.name} (Excel - first sheet)")
                    else:
                        st.success(f"✅ Loaded: {uploaded_file.name}")
                except ImportError as e:
                    st.error(f"❌ Excel support not available: {str(e)}")
                    st.info("💡 Install Excel support with: `pip install openpyxl>=3.1.0`")
                    st.session_state.dataset_handle = None
                    return
                except Exception as e:
                    st.error(f"❌ Failed to load file: {str(e)}")
                    st.info(f"File type detected: {Path(uploaded_file.name).suffix.lower()}")
                    with st.expander("🔍 Error Details"):
                        import traceback
                        st.code(traceback.format_exc())
                    st.session_state.dataset_handle = None
                    return

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
            # Analysis type selection
            analysis_type = st.radio(
                "Select Analysis Type",
                [
                    "🎯 Quick Analysis (All Agents)",
                    "📊 Individual Agent",
                    "🔬 Deep Dive Workflow",
                    "🤖 ML Preparation"
                ]
            )

            # Approval gates toggle
            if analysis_type != "📊 Individual Agent":
                st.markdown("---")
                enable_approval_gates = st.checkbox(
                    "🚦 Enable Approval Gates (Human-in-the-Loop)",
                    value=False,
                    help="Pause after each agent for review and approval before continuing"
                )

                if enable_approval_gates:
                    st.info("✨ **Approval Gates Enabled**: You'll review each agent's results before proceeding to the next step.")
            else:
                enable_approval_gates = False

            # Show appropriate options based on analysis type
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
                button_label = "🚀 Run Complete Analysis" if not enable_approval_gates else "🚀 Run with Approval Gates"

                if st.button(button_label, use_container_width=True, type="primary"):
                    if enable_approval_gates:
                        # Run with approval gates
                        st.session_state.workflow_mode = "complete_with_approval"
                        st.session_state.workflow_running = True
                        st.session_state.current_agent_index = 0
                        st.rerun()
                    else:
                        # Run without approval gates
                        run_complete_analysis()

            elif analysis_type == "🔬 Deep Dive Workflow":
                button_label = "🚀 Run Deep Dive" if not enable_approval_gates else "🚀 Run Deep Dive with Approval"

                if st.button(button_label, use_container_width=True, type="primary"):
                    if enable_approval_gates:
                        # Run with approval gates
                        st.session_state.workflow_mode = "deep_dive_with_approval"
                        st.session_state.workflow_running = True
                        st.session_state.current_agent_index = 0
                        st.rerun()
                    else:
                        # Run without approval gates
                        run_deep_dive_workflow()

            elif analysis_type == "🤖 ML Preparation":
                button_label = "🚀 Prepare for ML" if not enable_approval_gates else "🚀 ML Prep with Approval"

                if st.button(button_label, use_container_width=True, type="primary"):
                    if enable_approval_gates:
                        # Run with approval gates
                        st.session_state.workflow_mode = "ml_prep_with_approval"
                        st.session_state.workflow_running = True
                        st.session_state.current_agent_index = 0
                        st.rerun()
                    else:
                        # Run without approval gates
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


def run_workflow_with_approval_gates():
    """
    Run workflow with approval gates between agents
    This function handles the step-by-step execution with human review
    """
    handle = st.session_state.dataset_handle

    # Define agent configurations based on workflow mode
    workflow_mode = st.session_state.workflow_mode

    if workflow_mode == "complete_with_approval":
        agent_configs = [
            ("profile", "ProfileAgent", ProfileAgent()),
            ("quality", "QualityAgent", QualityAgent()),
            ("visualization", "VisualizationAgent", VisualizationAgent()),
            ("feature", "FeatureAgent", FeatureAgent()),
            ("stat", "StatAgent", StatAgent()),
            ("transform", "TransformAgent", TransformAgent())
        ]
        tracker_type = "complete_analysis"
    elif workflow_mode == "deep_dive_with_approval":
        agent_configs = [
            ("profile", "ProfileAgent", ProfileAgent()),
            ("quality", "QualityAgent", QualityAgent()),
            ("visualization", "VisualizationAgent", VisualizationAgent()),
            ("feature", "FeatureAgent", FeatureAgent()),
            ("stat", "StatAgent", StatAgent())
        ]
        tracker_type = "deep_dive"
    elif workflow_mode == "ml_prep_with_approval":
        agent_configs = [
            ("profile", "ProfileAgent", ProfileAgent()),
            ("quality", "QualityAgent", QualityAgent()),
            ("feature", "FeatureAgent", FeatureAgent()),
            ("transform", "TransformAgent", TransformAgent())
        ]
        tracker_type = "ml_prep"
    else:
        st.error("Invalid workflow mode")
        return

    # Store agent configs in session state
    if not st.session_state.agent_configs:
        st.session_state.agent_configs = agent_configs

    # Create tracker if not exists
    if st.session_state.workflow_tracker is None:
        tracker = create_workflow_tracker(tracker_type)
        st.session_state.workflow_tracker = tracker

    current_index = st.session_state.current_agent_index
    tracker = st.session_state.workflow_tracker

    # Check if workflow is complete
    if current_index >= len(agent_configs):
        st.success("🎉 Workflow completed successfully!")
        st.balloons()

        # Show summary of decisions
        if st.session_state.user_decisions:
            with st.expander("📋 View Decision History"):
                for i, decision in enumerate(st.session_state.user_decisions, 1):
                    decision_emoji = {
                        "approved": "✅",
                        "retry": "🔄",
                        "skip": "⏩",
                        "stop": "⏹️"
                    }.get(decision['decision'], "❓")

                    st.markdown(f"**{i}. {decision['step_id']}**: {decision_emoji} {decision['decision']}")
                    if decision.get('feedback'):
                        st.caption(f"Feedback: {decision['feedback']}")

        # Reset workflow state
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Start New Workflow", use_container_width=True):
                st.session_state.workflow_mode = None
                st.session_state.workflow_running = False
                st.session_state.current_agent_index = 0
                st.session_state.waiting_for_approval = False
                st.session_state.workflow_tracker = None
                st.session_state.agent_configs = []
                st.rerun()

        with col2:
            st.info("👇 Scroll down to view detailed results in the tabs below")

        # Mark workflow as complete - allow results to display
        st.session_state.workflow_running = False
        st.session_state.workflow_mode = None

        st.divider()
        # Return here - main() will continue and call display_results()
        return

    # Get current agent (only reached if workflow is still running)
    step_id, agent_name, agent = agent_configs[current_index]

    # Find the step in tracker
    step = next((s for s in tracker.steps if s.id == step_id), None)

    # If not waiting for approval, run the agent
    if not st.session_state.waiting_for_approval:
        st.info(f"🔄 Running {agent_name}...")

        # Show progress
        progress_container = st.empty()

        if step:
            step.start()
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
            if step:
                step.complete()

            # Update progress display
            with progress_container.container():
                tracker.render()

            st.success(f"✅ {agent_name} completed!")

            # Set waiting for approval
            st.session_state.waiting_for_approval = True
            st.rerun()

        except Exception as e:
            if step:
                step.fail(str(e))
                with progress_container.container():
                    tracker.render()

            st.error(f"❌ {agent_name} failed: {str(e)}")
            st.session_state.workflow_running = False
            return

    # Show approval gate
    else:
        # Show progress tracker
        tracker.render()

        st.divider()

        # Get the result
        result = st.session_state.analysis_results.get(step_id)

        if result:
            # Create and render approval gate
            gate = ApprovalGate(agent_name, result, step_id)
            decision = gate.render()

            # Handle decision
            if decision == "approved":
                store_user_decision(step_id, "approved")
                st.session_state.current_agent_index += 1
                st.session_state.waiting_for_approval = False
                st.rerun()

            elif decision == "retry":
                store_user_decision(step_id, "retry")
                # Remove the result to force re-run
                if step_id in st.session_state.analysis_results:
                    del st.session_state.analysis_results[step_id]
                st.session_state.waiting_for_approval = False
                st.rerun()

            elif decision == "skip":
                store_user_decision(step_id, "skip")
                # Keep result but move to next
                st.session_state.current_agent_index += 1
                st.session_state.waiting_for_approval = False
                st.rerun()

            elif decision == "stop":
                store_user_decision(step_id, "stop")
                st.warning("⏹️ Workflow stopped by user")
                st.session_state.workflow_running = False
                st.session_state.workflow_mode = None

                # Reset button
                if st.button("🔄 Reset Workflow"):
                    st.session_state.current_agent_index = 0
                    st.session_state.waiting_for_approval = False
                    st.session_state.workflow_tracker = None
                    st.session_state.agent_configs = []
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
        "🔧 Transformations",
        "💾 Export"
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

    with tabs[7]:
        display_export_options()


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
    """Display quality agent results with visualizations"""
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

    st.divider()

    # Interactive Quality Visualizations
    try:
        display_quality_visualizations(result, st.session_state.dataset_handle)
    except Exception as e:
        st.warning(f"Could not generate quality visualizations: {str(e)}")

        # Fallback to text-based display
        st.subheader("📊 Detailed Analysis")

        # Detailed outlier info
        if data['outliers']['has_outliers']:
            st.subheader("⚠️ Outlier Details")
            outlier_data = []
            for col, details in list(data['outliers']['outlier_details'].items())[:5]:
                outlier_data.append({
                    "Column": col,
                    "IQR Outliers": details['iqr_outliers'],
                    "Percentage": f"{details['iqr_percentage']:.1f}%",
                    "Range": f"[{details['min']:.2f}, {details['max']:.2f}]"
                })

            st.dataframe(pd.DataFrame(outlier_data), use_container_width=True)

    st.divider()

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
    """Display transformation proposals with before/after comparison"""
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

    st.divider()

    # Group by priority
    transformations = data['transformations']

    # Initialize session state for applied transformations
    if "applied_transformations" not in st.session_state:
        st.session_state.applied_transformations = []

    if "transform_preview_df" not in st.session_state:
        st.session_state.transform_preview_df = None

    if "selected_transform_ids" not in st.session_state:
        st.session_state.selected_transform_ids = set()

    # Quick action buttons
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        if st.button("☑️ Select All High Priority", use_container_width=True):
            high_priority = [t for t in transformations if t['priority'] == 'high']
            st.session_state.selected_transform_ids = {t['id'] for t in high_priority}
            st.rerun()

    with col2:
        selected_count = len(st.session_state.selected_transform_ids)
        if st.button(f"🔍 Preview Selected ({selected_count})", use_container_width=True, type="primary", disabled=selected_count == 0):
            selected_transforms = [t for t in transformations if t['id'] in st.session_state.selected_transform_ids]
            st.session_state.selected_transforms_for_preview = selected_transforms
            st.rerun()

    with col3:
        if st.button("☐ Deselect All", use_container_width=True):
            st.session_state.selected_transform_ids = set()
            st.rerun()

    with col4:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.selected_transforms_for_preview = []
            st.session_state.selected_transform_ids = set()
            st.session_state.transform_preview_df = None
            st.rerun()

    st.divider()

    # Show transformations by priority with checkboxes
    for priority in ['high', 'medium', 'low']:
        priority_transforms = [t for t in transformations if t['priority'] == priority]

        if priority_transforms:
            st.subheader(f"{priority.title()} Priority Transformations")

            for idx, transform in enumerate(priority_transforms):
                col1, col2, col3 = st.columns([0.5, 3.5, 1])

                with col1:
                    # Checkbox for selection
                    is_selected = transform['id'] in st.session_state.selected_transform_ids
                    if st.checkbox("", value=is_selected, key=f"select_{priority}_{idx}", label_visibility="collapsed"):
                        st.session_state.selected_transform_ids.add(transform['id'])
                    else:
                        st.session_state.selected_transform_ids.discard(transform['id'])

                with col2:
                    with st.expander(f"{transform['type'].replace('_', ' ').title()} - {transform['description'][:60]}..."):
                        st.markdown(f"**Description:** {transform['description']}")
                        st.markdown(f"**Reasoning:** {transform['reasoning']}")
                        st.markdown(f"**Impact:** {transform['impact']}")
                        st.markdown(f"**Type:** {transform['type']}")

                        # Show parameters if available
                        if 'params' in transform:
                            st.markdown("**Parameters:**")
                            for key, value in transform['params'].items():
                                st.markdown(f"  - {key}: `{value}`")

                with col3:
                    if st.button("👁️ Preview", key=f"preview_{priority}_{idx}"):
                        st.session_state.selected_transforms_for_preview = [transform]
                        st.session_state.selected_transform_ids = {transform['id']}
                        st.rerun()

    st.divider()

    # Show selection summary
    if st.session_state.selected_transform_ids:
        selected_transforms = [t for t in transformations if t['id'] in st.session_state.selected_transform_ids]

        st.info(f"""
        📋 **{len(selected_transforms)} transformation(s) selected**

        Selected transformations will be applied in sequence when you preview or apply to full dataset.
        """)

        with st.expander(f"📝 View Selected Transformations ({len(selected_transforms)})"):
            for i, t in enumerate(selected_transforms, 1):
                st.markdown(f"{i}. **{t['type'].replace('_', ' ').title()}** - {t['description']}")

    st.divider()

    # Show before/after comparison if transformations are selected
    if st.session_state.get('selected_transforms_for_preview'):
        st.subheader("🔄 Before/After Comparison")

        selected_transforms = st.session_state.selected_transforms_for_preview

        # Create simulated transformed dataset
        df_before = st.session_state.dataset_handle.sample(min(1000, st.session_state.dataset_handle.shape[0]))
        df_after = df_before.copy()

        # Apply transformations to create preview
        transform_desc = []
        for transform in selected_transforms:
            transform_type = transform['type']
            params = transform.get('params', {})

            if transform_type == 'deduplication':
                before_len = len(df_after)
                df_after = df_after.drop_duplicates(keep=params.get('keep', 'first'))
                transform_desc.append(f"Removed {before_len - len(df_after)} duplicate rows")

            elif transform_type == 'missing_value_handling':
                col = params.get('column')
                strategy = params.get('strategy')

                if col and col in df_after.columns:
                    if strategy == 'drop_column':
                        df_after = df_after.drop(columns=[col])
                        transform_desc.append(f"Dropped column '{col}'")

                    elif strategy == 'impute_median':
                        median_val = df_after[col].median()
                        missing_count = df_after[col].isnull().sum()
                        df_after[col] = df_after[col].fillna(median_val)
                        transform_desc.append(f"Filled {missing_count} missing values in '{col}' with median ({median_val:.2f})")

                    elif strategy == 'impute_mode':
                        mode_val = df_after[col].mode()[0] if not df_after[col].mode().empty else 'Unknown'
                        missing_count = df_after[col].isnull().sum()
                        df_after[col] = df_after[col].fillna(mode_val)
                        transform_desc.append(f"Filled {missing_count} missing values in '{col}' with mode ('{mode_val}')")

                    elif strategy == 'impute_constant':
                        constant = params.get('value', 'Unknown')
                        missing_count = df_after[col].isnull().sum()
                        df_after[col] = df_after[col].fillna(constant)
                        transform_desc.append(f"Filled {missing_count} missing values in '{col}' with constant ('{constant}')")

            elif transform_type == 'outlier_handling':
                col = params.get('column')
                strategy = params.get('strategy', 'cap')

                if col and col in df_after.columns:
                    Q1 = df_after[col].quantile(0.25)
                    Q3 = df_after[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR

                    if strategy == 'cap':
                        outliers_count = ((df_after[col] < lower) | (df_after[col] > upper)).sum()
                        df_after[col] = df_after[col].clip(lower, upper)
                        transform_desc.append(f"Capped {outliers_count} outliers in '{col}'")

            elif transform_type == 'categorical_encoding':
                col = params.get('column')
                method = params.get('method', 'onehot')

                if col and col in df_after.columns:
                    if method == 'onehot':
                        # Apply one-hot encoding
                        unique_vals = df_after[col].nunique()
                        dummies = pd.get_dummies(df_after[col], prefix=col, drop_first=False)
                        df_after = pd.concat([df_after.drop(columns=[col]), dummies], axis=1)
                        transform_desc.append(f"One-hot encoded '{col}' into {len(dummies.columns)} binary columns")
                    elif method == 'label':
                        # Label encoding
                        df_after[col] = pd.Categorical(df_after[col]).codes
                        transform_desc.append(f"Label encoded '{col}'")

            elif transform_type == 'type_conversion':
                col = params.get('column')
                to_type = params.get('to_type')

                if col and col in df_after.columns:
                    try:
                        if to_type == 'numeric':
                            df_after[col] = pd.to_numeric(df_after[col], errors='coerce')
                            transform_desc.append(f"Converted '{col}' to numeric")
                        elif to_type == 'datetime':
                            df_after[col] = pd.to_datetime(df_after[col], errors='coerce')
                            transform_desc.append(f"Converted '{col}' to datetime")
                        elif to_type == 'categorical':
                            df_after[col] = df_after[col].astype('category')
                            transform_desc.append(f"Converted '{col}' to categorical")
                    except Exception as e:
                        transform_desc.append(f"Failed to convert '{col}': {str(e)}")

            elif transform_type == 'scaling':
                cols = params.get('columns', [])
                method = params.get('method', 'standard')

                scaled_count = 0
                for col in cols:
                    if col in df_after.columns and pd.api.types.is_numeric_dtype(df_after[col]):
                        if method == 'standard':
                            mean = df_after[col].mean()
                            std = df_after[col].std()
                            if std > 0:
                                df_after[col] = (df_after[col] - mean) / std
                                scaled_count += 1
                        elif method == 'minmax':
                            min_val = df_after[col].min()
                            max_val = df_after[col].max()
                            if max_val > min_val:
                                df_after[col] = (df_after[col] - min_val) / (max_val - min_val)
                                scaled_count += 1

                if scaled_count > 0:
                    transform_desc.append(f"Scaled {scaled_count} numeric columns using {method} scaling")

            elif transform_type == 'cardinality_reduction':
                col = params.get('column')
                action = params.get('suggested_action', 'review')

                if col and col in df_after.columns and action == 'drop':
                    df_after = df_after.drop(columns=[col])
                    transform_desc.append(f"Dropped high-cardinality column '{col}'")

        # Display comparison
        transformation_info = {
            'description': ' | '.join(transform_desc) if transform_desc else 'Multiple transformations applied'
        }

        display_transformation_comparison(
            df_before,
            df_after,
            transformation_info,
            show_details=True
        )

        # Add "Apply Transformations" button
        st.divider()
        st.subheader("💾 Apply Transformations to Full Dataset")

        # Check dataset size and show warning for large datasets
        dataset_mode = st.session_state.dataset_handle.mode
        dataset_size = st.session_state.dataset_handle.shape[0]

        if dataset_mode == "sampled":
            st.warning(f"""
            ⚠️ **Large Dataset Detected** ({dataset_size:,} rows)

            Applying transformations will load the entire dataset into memory.
            This may take some time and use significant memory.
            """)
        else:
            st.info("""
            **Preview shows a sample.** Click below to apply these transformations to the **entire dataset**
            and save the result for export.
            """)

        col1, col2, col3 = st.columns([2, 2, 1])

        # Show count of transformations being applied
        num_transforms = len(selected_transforms)
        transform_text = f"transformation{'s' if num_transforms > 1 else ''}"

        with col1:
            apply_to_full = st.button(
                f"✅ Apply {num_transforms} {transform_text} to Full Dataset",
                type="primary",
                use_container_width=True,
                help=f"Apply {num_transforms} selected {transform_text} to the entire dataset and save for export"
            )

        with col2:
            if 'transformed_dataset' in st.session_state and st.session_state.transformed_dataset is not None:
                st.success(f"✅ Transformed dataset ready ({len(st.session_state.transformed_dataset):,} rows)")

        with col3:
            if 'transformed_dataset' in st.session_state and st.session_state.transformed_dataset is not None:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.transformed_dataset = None
                    if 'transformed_data_path' in st.session_state:
                        del st.session_state.transformed_data_path
                    st.rerun()

        if apply_to_full:
            try:
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Load dataset
                status_text.text("📥 Loading full dataset into memory...")
                df_full = st.session_state.dataset_handle.backend.get_dataframe().copy()
                progress_bar.progress(0.2)

                # Apply the same transformations
                total_transforms = len(selected_transforms)
                for idx, transform in enumerate(selected_transforms):
                    # Update progress
                    progress = 0.2 + (0.6 * (idx / total_transforms))
                    progress_bar.progress(progress)
                    status_text.text(f"🔄 Applying transformation {idx + 1}/{total_transforms}: {transform['type']}...")

                    transform_type = transform['type']
                    params = transform.get('params', {})

                    if transform_type == 'deduplication':
                        df_full = df_full.drop_duplicates(keep=params.get('keep', 'first'))

                    elif transform_type == 'missing_value_handling':
                        col = params.get('column')
                        strategy = params.get('strategy')

                        if col and col in df_full.columns:
                            if strategy == 'drop_column':
                                df_full = df_full.drop(columns=[col])
                            elif strategy == 'impute_median':
                                df_full[col] = df_full[col].fillna(df_full[col].median())
                            elif strategy == 'impute_mode':
                                mode_val = df_full[col].mode()[0] if not df_full[col].mode().empty else 'Unknown'
                                df_full[col] = df_full[col].fillna(mode_val)
                            elif strategy == 'impute_constant':
                                constant = params.get('value', 'Unknown')
                                df_full[col] = df_full[col].fillna(constant)

                    elif transform_type == 'outlier_handling':
                        col = params.get('column')
                        strategy = params.get('strategy', 'cap')

                        if col and col in df_full.columns:
                            Q1 = df_full[col].quantile(0.25)
                            Q3 = df_full[col].quantile(0.75)
                            IQR = Q3 - Q1
                            lower = Q1 - 1.5 * IQR
                            upper = Q3 + 1.5 * IQR

                            if strategy == 'cap':
                                df_full[col] = df_full[col].clip(lower, upper)

                    elif transform_type == 'categorical_encoding':
                        col = params.get('column')
                        method = params.get('method', 'onehot')

                        if col and col in df_full.columns:
                            if method == 'onehot':
                                dummies = pd.get_dummies(df_full[col], prefix=col, drop_first=False)
                                df_full = pd.concat([df_full.drop(columns=[col]), dummies], axis=1)
                            elif method == 'label':
                                df_full[col] = pd.Categorical(df_full[col]).codes

                    elif transform_type == 'type_conversion':
                        col = params.get('column')
                        to_type = params.get('to_type')

                        if col and col in df_full.columns:
                            try:
                                if to_type == 'numeric':
                                    df_full[col] = pd.to_numeric(df_full[col], errors='coerce')
                                elif to_type == 'datetime':
                                    df_full[col] = pd.to_datetime(df_full[col], errors='coerce')
                                elif to_type == 'categorical':
                                    df_full[col] = df_full[col].astype('category')
                            except Exception:
                                pass

                    elif transform_type == 'scaling':
                        cols = params.get('columns', [])
                        method = params.get('method', 'standard')

                        for col in cols:
                            if col in df_full.columns and pd.api.types.is_numeric_dtype(df_full[col]):
                                if method == 'standard':
                                    mean = df_full[col].mean()
                                    std = df_full[col].std()
                                    if std > 0:
                                        df_full[col] = (df_full[col] - mean) / std
                                elif method == 'minmax':
                                    min_val = df_full[col].min()
                                    max_val = df_full[col].max()
                                    if max_val > min_val:
                                        df_full[col] = (df_full[col] - min_val) / (max_val - min_val)

                    elif transform_type == 'cardinality_reduction':
                        col = params.get('column')
                        action = params.get('suggested_action', 'review')

                        if col and col in df_full.columns and action == 'drop':
                            df_full = df_full.drop(columns=[col])

                # Save transformed dataset
                progress_bar.progress(0.8)
                status_text.text("💾 Saving transformed dataset...")

                st.session_state.transformed_dataset = df_full

                # Save to file for export
                output_dir = Path("data/exports")
                output_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_path = output_dir / f"transformed_dataset_{timestamp}.csv"
                df_full.to_csv(csv_path, index=False)
                st.session_state.transformed_data_path = str(csv_path)

                # Update transform results to include the path
                st.session_state.analysis_results['transform']['result']['transformed_data_path'] = str(csv_path)

                # Complete
                progress_bar.progress(1.0)
                status_text.text("✅ Complete!")

                st.success(f"""
                ✅ **Transformations applied successfully!**
                - Original shape: {st.session_state.dataset_handle.shape}
                - Transformed shape: {df_full.shape}
                - Saved to: {csv_path.name}
                - Ready for export in the **Export** section
                """)

                # Show preview of transformed data
                with st.expander("📊 Preview Transformed Dataset"):
                    st.dataframe(df_full.head(20), use_container_width=True)
                    st.caption(f"Showing first 20 rows of {len(df_full):,} total rows")

            except Exception as e:
                st.error(f"❌ Failed to apply transformations: {str(e)}")
                import traceback
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())

    st.divider()

    # Explainability
    if st.session_state.get("show_reasoning", True):
        with st.expander("🧠 Agent Reasoning"):
            st.markdown(f"**Reasoning:** {result['reasoning']}")
            st.markdown(f"**Impact:** {result['impact']}")
            st.markdown("**Recommendations:**")
            for rec in result['recommendations']:
                st.markdown(f"- {rec}")


def display_export_options():
    """Display export functionality"""
    st.header("💾 Export Analysis Results")

    if not st.session_state.analysis_results:
        st.warning("⚠️ Run analysis first to export results")
        return

    st.markdown("""
    Export your analysis results in various formats to share with stakeholders
    or for further processing.
    """)

    st.divider()

    # Export format selection
    st.subheader("🎯 Select Export Formats")

    col1, col2, col3 = st.columns(3)

    with col1:
        export_html = st.checkbox(
            "📄 HTML Report",
            value=True,
            help="Interactive HTML report with all visualizations and analysis"
        )

    with col2:
        export_json = st.checkbox(
            "📊 JSON Data",
            value=True,
            help="Raw analysis results in JSON format for programmatic access"
        )

    with col3:
        # Check if transformed dataset is available
        has_transformed = (
            'transformed_dataset' in st.session_state and
            st.session_state.transformed_dataset is not None
        )

        export_csv = st.checkbox(
            "📋 Transformed CSV",
            value=False,
            help="Export transformed dataset (click 'Apply to Full Dataset' in Transform section first)",
            disabled=not has_transformed
        )

        if not has_transformed and 'transform' in st.session_state.analysis_results:
            st.caption("⚠️ Apply transformations first in the Transform section")

    st.divider()

    # Export preview
    st.subheader("📦 Export Preview")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Analysis Results:**")
        completed_agents = list(st.session_state.analysis_results.keys())
        for agent in completed_agents:
            agent_name = agent.replace('_', ' ').title() + "Agent"
            st.markdown(f"- ✅ {agent_name}")

    with col2:
        st.markdown("**Dataset Information:**")
        if st.session_state.dataset_handle:
            info = st.session_state.dataset_handle.get_info()
            # Extract filename from path
            dataset_name = Path(info['path']).name if 'path' in info else 'Unknown'
            st.markdown(f"- **Name:** {dataset_name}")
            st.markdown(f"- **Rows:** {info['rows']:,}")
            st.markdown(f"- **Columns:** {info['columns']}")
            st.markdown(f"- **Size:** {info['file_size_formatted']}")

    st.divider()

    # Export action
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        export_name = st.text_input(
            "Custom Export Name (optional)",
            placeholder="my_analysis",
            help="Leave blank for auto-generated timestamp name"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Export Now", type="primary", use_container_width=True):
            perform_export(export_html, export_json, export_csv, export_name)

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📂 View Exports", use_container_width=True):
            st.session_state.show_exports_list = True
            st.rerun()

    # Show export list if requested
    if st.session_state.get("show_exports_list", False):
        st.divider()
        display_exports_list()


def perform_export(
    export_html: bool,
    export_json: bool,
    export_csv: bool,
    custom_name: str
):
    """Perform the export operation"""

    formats = []
    if export_html:
        formats.append('html')
    if export_json:
        formats.append('json')
    if export_csv and 'transform' in st.session_state.analysis_results:
        formats.append('csv')

    if not formats:
        st.warning("⚠️ Please select at least one export format")
        return

    # Get dataset info
    dataset_info = {}
    if st.session_state.dataset_handle:
        info = st.session_state.dataset_handle.get_info()
        # Extract filename from path
        dataset_name = Path(info['path']).name if 'path' in info else 'Unknown'
        dataset_info = {
            'name': dataset_name,
            'rows': info['rows'],
            'columns': info['columns'],
            'file_size_formatted': info['file_size_formatted']
        }

    with st.spinner("🔄 Exporting analysis results..."):
        try:
            # Use custom name if provided
            session_prefix = f"{custom_name}_" if custom_name else None

            exported_files = st.session_state.export_manager.export_all(
                st.session_state.analysis_results,
                dataset_info,
                formats,
                session_id=session_prefix
            )

            # Display success with download buttons
            st.success("✅ Export completed successfully!")

            st.markdown("### 📥 Download Files")

            for format_type, file_path in exported_files.items():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**{format_type.upper()}:** `{Path(file_path).name}`")

                with col2:
                    # Read file for download
                    with open(file_path, 'rb') as f:
                        file_data = f.read()

                    mime_types = {
                        'html': 'text/html',
                        'json': 'application/json',
                        'csv': 'text/csv'
                    }

                    st.download_button(
                        label="⬇️ Download",
                        data=file_data,
                        file_name=Path(file_path).name,
                        mime=mime_types.get(format_type, 'application/octet-stream'),
                        key=f"download_{format_type}"
                    )

            # Show file locations
            with st.expander("📂 File Locations"):
                for format_type, file_path in exported_files.items():
                    st.code(file_path)

        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
            st.exception(e)


def display_exports_list():
    """Display list of previously exported files"""
    st.subheader("📂 Previously Exported Files")

    export_dir = Path("data/exports")

    if not export_dir.exists():
        st.info("No exports found")
        return

    # Get all export files
    html_files = list(export_dir.glob("*.html"))
    json_files = list(export_dir.glob("*.json"))
    csv_files = list(export_dir.glob("*.csv"))

    if not html_files and not json_files and not csv_files:
        st.info("No exports found")
        return

    # Display by type
    tab1, tab2, tab3 = st.tabs(["HTML Reports", "JSON Data", "CSV Files"])

    with tab1:
        if html_files:
            for file_path in sorted(html_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**{file_path.name}**")
                    modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    st.caption(f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")

                with col2:
                    size_kb = file_path.stat().st_size / 1024
                    st.caption(f"Size: {size_kb:.1f} KB")

                with col3:
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download",
                            data=f.read(),
                            file_name=file_path.name,
                            mime='text/html',
                            key=f"dl_html_{file_path.name}"
                        )
        else:
            st.info("No HTML reports found")

    with tab2:
        if json_files:
            for file_path in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**{file_path.name}**")
                    modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    st.caption(f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")

                with col2:
                    size_kb = file_path.stat().st_size / 1024
                    st.caption(f"Size: {size_kb:.1f} KB")

                with col3:
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download",
                            data=f.read(),
                            file_name=file_path.name,
                            mime='application/json',
                            key=f"dl_json_{file_path.name}"
                        )
        else:
            st.info("No JSON files found")

    with tab3:
        if csv_files:
            for file_path in sorted(csv_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**{file_path.name}**")
                    modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    st.caption(f"Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")

                with col2:
                    size_kb = file_path.stat().st_size / 1024
                    st.caption(f"Size: {size_kb:.1f} KB")

                with col3:
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download",
                            data=f.read(),
                            file_name=file_path.name,
                            mime='text/csv',
                            key=f"dl_csv_{file_path.name}"
                        )
        else:
            st.info("No CSV files found")


def main():
    """Main application"""
    display_header()
    display_sidebar()

    # Handle approval gate workflows
    if st.session_state.workflow_running and st.session_state.workflow_mode:
        if st.session_state.workflow_mode in ["complete_with_approval", "deep_dive_with_approval", "ml_prep_with_approval"]:
            run_workflow_with_approval_gates()
            # Don't return - let it fall through to display_results() when complete
            if st.session_state.workflow_running:
                # Still running - don't show results yet
                return

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
