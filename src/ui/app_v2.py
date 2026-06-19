"""
Enhanced Streamlit UI for EDA Pipeline - Phase 2
Supports QualityAgent, TransformAgent, and workflow orchestration with approval flow
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.dataset_handle import DatasetHandle
from src.graph.workflow import EDAWorkflow
from src.utils.types import WORKFLOWS, UserDecision
from src.utils.helpers import generate_id, get_timestamp
import os


# Page config
st.set_page_config(
    page_title="EDA Pipeline - Phase 2",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "dataset_handle" not in st.session_state:
    st.session_state.dataset_handle = None

if "session_id" not in st.session_state:
    st.session_state.session_id = generate_id("session")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "workflow" not in st.session_state:
    st.session_state.workflow = None

if "current_state" not in st.session_state:
    st.session_state.current_state = None

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None


def display_header():
    """Display app header"""
    st.title("🤖 EDA Pipeline - Phase 2")
    st.markdown("""
    **Workflow-Based Analysis with Human-in-the-Loop**
    - 🔍 **ProfileAgent**: Dataset structure and health
    - ✅ **QualityAgent**: Duplicates, outliers, inconsistencies
    - 🔧 **TransformAgent**: Data transformation proposals
    """)
    st.divider()


def display_sidebar():
    """Display sidebar with file upload and workflow controls"""
    with st.sidebar:
        st.header("📁 Dataset Upload")

        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload your dataset for analysis"
        )

        if uploaded_file is not None:
            # Save uploaded file
            upload_dir = Path("data/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)

            file_path = upload_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Create dataset handle
            if st.session_state.dataset_handle is None or st.session_state.dataset_handle.path != str(file_path):
                st.session_state.dataset_handle = DatasetHandle(str(file_path))
                st.success(f"✅ Loaded: {uploaded_file.name}")

                # Display dataset info
                info = st.session_state.dataset_handle.get_info()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows", f"{info['rows']:,}")
                    st.metric("File Size", info['file_size_formatted'])
                with col2:
                    st.metric("Columns", info['columns'])
                    st.metric("Mode", info['mode'].replace('_', ' ').title())

        st.divider()

        # Workflow selection
        st.header("🔄 Start Workflow")

        if st.session_state.dataset_handle is None:
            st.warning("⚠️ Upload a dataset first")
        else:
            # Quick Profile button
            if st.button("🚀 Start Quick Profile", use_container_width=True, type="primary"):
                start_workflow("quick_profile")
                st.rerun()

            st.caption("Quick Profile: Profile → Quality Check → Transform Proposals")

        st.divider()

        # Workflow status
        st.header("📊 Workflow Status")
        if st.session_state.current_state:
            state = st.session_state.current_state
            st.metric("Current Step", state.get('current_step', 'N/A'))
            st.write("**Completed Steps:**")
            for step in state.get('completed_steps', []):
                st.success(f"✓ {step}")

            if st.session_state.pending_approval:
                st.warning("⏸️ Awaiting approval")
        else:
            st.info("No active workflow")


def start_workflow(workflow_key: str):
    """Start a workflow"""
    if st.session_state.dataset_handle is None:
        st.error("Please upload a dataset first!")
        return

    # Initialize workflow
    st.session_state.workflow = EDAWorkflow()
    st.session_state.thread_id = generate_id("thread")

    # Create initial state
    initial_state = st.session_state.workflow.create_initial_state(
        dataset_path=st.session_state.dataset_handle.path,
        session_id=st.session_state.session_id,
        workflow_type=workflow_key
    )

    add_message("assistant", f"🚀 Starting **{WORKFLOWS[workflow_key]['name']}** workflow...")

    # Run workflow until first interrupt
    try:
        for event in st.session_state.workflow.run(initial_state, st.session_state.thread_id):
            for node_name, node_state in event.items():
                if node_state:
                    st.session_state.current_state = node_state

                    # Check for interrupt - only display on human_review nodes to avoid duplicates
                    if node_state.get('pending_approval') and node_name.startswith('human_review_'):
                        st.session_state.pending_approval = node_state.get('approval_context')
                        display_agent_results(node_state)
                        break
    except Exception as e:
        st.error(f"Error running workflow: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


def display_agent_results(state: dict):
    """Display agent results and request approval"""
    approval_ctx = state.get('approval_context', {})
    agent_name = approval_ctx.get('agent', 'Unknown')
    step = approval_ctx.get('step', 'unknown')

    # Display results based on agent type
    if step == "profile":
        display_profile_results(state.get('profile_results'), approval_ctx)
    elif step == "quality_check":
        display_quality_results(state.get('quality_results'), approval_ctx)
    elif step == "transform_proposal":
        display_transform_results(state.get('pending_transformations'), approval_ctx)


def display_profile_results(results: dict, approval_ctx: dict):
    """Display ProfileAgent results"""
    if not results:
        return

    basic_info = results['basic_info']

    message = f"""### 📊 ProfileAgent Results

**Dataset Overview:**
- Rows: {basic_info['rows']:,}
- Columns: {basic_info['columns']}
- File Size: {basic_info['file_size']}
- Mode: {basic_info['mode'].replace('_', ' ').title()}

**Column Types:**
- Numeric: {len(results['column_types']['numeric'])}
- Categorical: {len(results['column_types']['categorical'])}
- Datetime: {len(results['column_types']['datetime'])}

**Issues Detected:**
- High missing value columns: {len(results['issues']['high_missing_cols'])}
- High cardinality columns: {len(results['issues']['high_cardinality_cols'])}

---

### 🧠 Explainability

**💡 Reasoning:**
{approval_ctx['reasoning']}

**⚡ Impact:**
{approval_ctx['impact']}

**📝 Recommendations:**
"""

    for i, rec in enumerate(approval_ctx.get('recommendations', []), 1):
        message += f"\n{i}. {rec}"

    message += f"\n\n**🎯 Confidence:** {approval_ctx.get('confidence', 0):.0%}"

    add_message("assistant", message)


def display_quality_results(results: dict, approval_ctx: dict):
    """Display QualityAgent results"""
    if not results:
        return

    message = f"""### ✅ QualityAgent Results

**Quality Assessment:**
- Sample Analyzed: {results.get('sample_size', 0):,} / {results.get('total_rows', 0):,} rows

**Duplicates:**
- Duplicate rows: {results.get('duplicates', {}).get('duplicate_rows', 0)}
- Estimated total: {results.get('duplicates', {}).get('estimated_total_duplicates', 0)}

**Outliers:**
- Columns with outliers: {results.get('outliers', {}).get('columns_with_outliers', 0)}

**Inconsistencies:**
- Issues found: {results.get('inconsistencies', {}).get('inconsistency_count', 0)}

**Data Type Issues:**
- Type mismatches: {results.get('data_types', {}).get('type_issue_count', 0)}

**Value Range Issues:**
- Range violations: {results.get('value_ranges', {}).get('range_issue_count', 0)}

---

### 🧠 Explainability

**💡 Reasoning:**
{approval_ctx['reasoning']}

**⚡ Impact:**
{approval_ctx['impact']}

**📝 Recommendations:**
"""

    for i, rec in enumerate(approval_ctx.get('recommendations', []), 1):
        message += f"\n{i}. {rec}"

    message += f"\n\n**🎯 Confidence:** {approval_ctx.get('confidence', 0):.0%}"

    add_message("assistant", message)


def display_transform_results(transformations: list, approval_ctx: dict):
    """Display TransformAgent results"""
    if not transformations:
        return

    high_priority = [t for t in transformations if t.get('priority') == 'high']
    medium_priority = [t for t in transformations if t.get('priority') == 'medium']
    low_priority = [t for t in transformations if t.get('priority') == 'low']

    message = f"""### 🔧 TransformAgent Results

**Transformation Proposals:**
- Total: {len(transformations)}
- High Priority: {len(high_priority)}
- Medium Priority: {len(medium_priority)}
- Low Priority: {len(low_priority)}

**Top Transformations:**
"""

    for i, transform in enumerate(transformations[:5], 1):
        priority_emoji = "🔴" if transform['priority'] == 'high' else "🟡" if transform['priority'] == 'medium' else "🟢"
        message += f"\n{i}. {priority_emoji} **{transform['description']}**"
        message += f"\n   - Type: {transform['type']}"
        message += f"\n   - Impact: {transform['impact']}\n"

    message += f"""
---

### 🧠 Explainability

**💡 Reasoning:**
{approval_ctx['reasoning']}

**⚡ Impact:**
{approval_ctx['impact']}

**📝 Recommendations:**
"""

    for i, rec in enumerate(approval_ctx.get('recommendations', []), 1):
        message += f"\n{i}. {rec}"

    message += f"\n\n**🎯 Confidence:** {approval_ctx.get('confidence', 0):.0%}"

    add_message("assistant", message)


def add_message(role: str, content: str):
    """Add message to chat history"""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": get_timestamp()
    })


def display_chat():
    """Display chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_approval(decision: str):
    """Handle user approval decision"""
    if not st.session_state.current_state or not st.session_state.pending_approval:
        return

    # Create user decision
    step = st.session_state.current_state.get('current_step', 'unknown')
    user_decision = UserDecision(
        step_id=step,
        decision=decision,
        timestamp=get_timestamp(),
        feedback=None
    )

    # Update state
    updates = {
        "user_decisions": st.session_state.current_state.get("user_decisions", []) + [user_decision],
        "pending_approval": False
    }

    st.session_state.workflow.update_state(st.session_state.thread_id, updates)

    # Clear pending approval
    st.session_state.pending_approval = None

    # Add message
    decision_emoji = "✅" if decision == "approved" else "❌" if decision == "rejected" else "⏭️"
    add_message("user", f"{decision_emoji} Decision: **{decision.upper()}**")

    # Resume workflow
    try:
        for event in st.session_state.workflow.resume(st.session_state.thread_id):
            for node_name, node_state in event.items():
                if node_state:
                    st.session_state.current_state = node_state

                    # Check for next interrupt - only display on human_review nodes to avoid duplicates
                    if node_state.get('pending_approval') and node_name.startswith('human_review_'):
                        st.session_state.pending_approval = node_state.get('approval_context')
                        display_agent_results(node_state)
                        break

        # Check if workflow completed
        if not st.session_state.pending_approval:
            add_message("assistant", "✅ **Workflow completed!**")

    except Exception as e:
        st.error(f"Error resuming workflow: {str(e)}")


def main():
    """Main app function"""
    display_header()
    display_sidebar()

    # Chat interface
    st.header("💬 Analysis Chat")

    # Display chat history
    display_chat()

    # Approval buttons if pending
    if st.session_state.pending_approval:
        st.divider()
        st.subheader("⏸️ Approval Required")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✅ Approve & Continue", type="primary", use_container_width=True):
                handle_approval("approved")
                st.rerun()

        with col2:
            if st.button("❌ Reject & Retry", use_container_width=True):
                handle_approval("rejected")
                st.rerun()

        with col3:
            if st.button("⏭️ Skip & End", use_container_width=True):
                handle_approval("modified")
                st.rerun()

    # Chat input (disabled during approval)
    if prompt := st.chat_input("Ask about your data...", disabled=st.session_state.pending_approval is not None):
        add_message("user", prompt)

        # Simple response for now
        add_message("assistant", "💡 Use the sidebar to start a workflow, or upload a dataset to begin.")

        st.rerun()


if __name__ == "__main__":
    main()
