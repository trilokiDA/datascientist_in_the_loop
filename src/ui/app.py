import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.dataset_handle import DatasetHandle
from src.agents.profile_agent import ProfileAgent
from src.utils.types import WORKFLOWS
from src.utils.helpers import generate_id, get_timestamp
import os


# Page config
st.set_page_config(
    page_title="EDA Pipeline - Agentic Analysis",
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

if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = None

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None


def display_header():
    """Display app header"""
    st.title("🤖 EDA Pipeline - Agentic Analysis")
    st.markdown("""
    Upload a dataset and let specialized AI agents analyze it with explainability.
    - 🔍 **ProfileAgent**: Understands your data structure
    - ✅ **QualityAgent**: Finds data quality issues (coming soon)
    - 📊 **FeatureAgent**: Discovers relationships (coming soon)
    """)
    st.divider()


def display_sidebar():
    """Display sidebar with file upload and workflow selection"""
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
                st.metric("Rows", f"{info['rows']:,}")
                st.metric("Columns", info['columns'])
                st.metric("File Size", info['file_size_formatted'])
                st.metric("Mode", info['mode'].replace('_', ' ').title())

        st.divider()

        # Workflow selection
        st.header("🔄 Workflows")
        st.markdown("**Available Workflows:**")

        for workflow_key, workflow_config in WORKFLOWS.items():
            with st.expander(f"📋 {workflow_config['name']}"):
                st.write(workflow_config['description'])
                st.write(f"⏱️ Est. time: {workflow_config['estimated_time_mins']} min")
                st.write(f"Steps: {', '.join(workflow_config['steps'])}")

                if st.button(f"Start {workflow_config['name']}", key=f"start_{workflow_key}"):
                    if st.session_state.dataset_handle is None:
                        st.error("Please upload a dataset first!")
                    else:
                        start_workflow(workflow_key)
                        st.rerun()

        st.divider()

        # Quick actions
        st.header("⚡ Quick Actions")
        if st.button("🔍 Profile Dataset", use_container_width=True):
            if st.session_state.dataset_handle is None:
                st.error("Please upload a dataset first!")
            else:
                run_profile_agent()
                st.rerun()


def start_workflow(workflow_key: str):
    """Start a workflow"""
    st.session_state.workflow_state = {
        "workflow_key": workflow_key,
        "config": WORKFLOWS[workflow_key],
        "current_step": 0,
        "completed_steps": []
    }

    add_message("assistant", f"🚀 Starting **{WORKFLOWS[workflow_key]['name']}** workflow...")

    # For now, just run profile step
    run_profile_agent()


def run_profile_agent():
    """Run ProfileAgent analysis"""
    if st.session_state.dataset_handle is None:
        st.error("No dataset loaded!")
        return

    add_message("assistant", "🔍 **ProfileAgent** is analyzing your dataset...")

    # Run agent
    with st.spinner("Analyzing..."):
        agent = ProfileAgent()
        result = agent.analyze(st.session_state.dataset_handle)

    # Create and add the full response message
    create_agent_message("ProfileAgent", result)

    # Store in session for later use
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = {}
    st.session_state.analysis_results['profile'] = result


def create_agent_message(agent_name: str, response: dict):
    """Create a complete agent message with results and explainability"""

    # Main findings
    result = response['result']
    basic_info = result['basic_info']

    # Build complete message with all information
    message = f"""### 📊 {agent_name} Results

**Dataset Overview:**
- Rows: {basic_info['rows']:,}
- Columns: {basic_info['columns']}
- File Size: {basic_info['file_size']}
- Mode: {basic_info['mode'].replace('_', ' ').title()}

**Column Types:**
- Numeric: {len(result['column_types']['numeric'])}
- Categorical: {len(result['column_types']['categorical'])}
- Datetime: {len(result['column_types']['datetime'])}
- Other: {len(result['column_types']['other'])}

**Issues Detected:**
- High missing value columns (>40%): {len(result['issues']['high_missing_cols'])}
- High cardinality columns: {len(result['issues']['high_cardinality_cols'])}

---

### 🧠 Explainability

**💡 Reasoning (Why):**
{response['reasoning']}

**⚡ Impact (What it means):**
{response['impact']}

**📝 Recommendations:**
"""

    # Add recommendations
    for i, rec in enumerate(response['recommendations'], 1):
        message += f"\n{i}. {rec}"

    message += f"\n\n**🎯 Confidence:** {response['confidence']:.0%}"

    # Add message to chat
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


def main():
    """Main app function"""
    display_header()
    display_sidebar()

    # Chat interface
    st.header("💬 Analysis Chat")

    # Display chat history
    display_chat()

    # Chat input
    if prompt := st.chat_input("Ask about your data or request analysis..."):
        # Add user message
        add_message("user", prompt)

        # Process input (basic for now)
        if "profile" in prompt.lower():
            if st.session_state.dataset_handle is None:
                add_message("assistant", "⚠️ Please upload a dataset first!")
            else:
                run_profile_agent()
        else:
            response = "I can help you analyze your dataset! Try:\n- Upload a CSV file\n- Click 'Profile Dataset' in the sidebar\n- Or ask me to profile your data"
            add_message("assistant", response)

        # Rerun to display new messages
        st.rerun()


if __name__ == "__main__":
    main()
