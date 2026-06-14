from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from pathlib import Path

from src.utils.types import EDAState
from src.data.dataset_handle import DatasetHandle
from src.agents.profile_agent import ProfileAgent
from src.utils.helpers import get_timestamp, create_reasoning_log


class EDAWorkflow:
    """
    LangGraph-based workflow orchestration for EDA pipeline
    """

    def __init__(self, checkpoint_dir: str = "data/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Initialize checkpoint saver
        db_path = self.checkpoint_dir / "checkpoints.db"
        self.checkpointer = SqliteSaver.from_conn_string(str(db_path))

        # Initialize agents
        self.profile_agent = ProfileAgent()

        # Build graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""

        # Create state graph
        workflow = StateGraph(EDAState)

        # Add nodes
        workflow.add_node("profile", self._profile_node)
        workflow.add_node("human_review", self._human_review_node)

        # Add edges
        workflow.set_entry_point("profile")
        workflow.add_edge("profile", "human_review")

        # Conditional edge after human review
        workflow.add_conditional_edges(
            "human_review",
            self._route_after_review,
            {
                "continue": END,  # For now, end after profile
                "retry": "profile"
            }
        )

        return workflow.compile(checkpointer=self.checkpointer)

    def _profile_node(self, state: EDAState) -> Dict[str, Any]:
        """Profile node - runs ProfileAgent"""

        # Get dataset handle (in real implementation, this would be loaded from state)
        dataset_handle = DatasetHandle(state["dataset_path"])

        # Run profile agent
        response = self.profile_agent.analyze(dataset_handle)

        # Update state
        reasoning_log = create_reasoning_log(
            agent="ProfileAgent",
            action="dataset_profiling",
            reasoning=response["reasoning"],
            impact=response["impact"],
            confidence=response["confidence"]
        )

        return {
            **state,
            "profile_results": response["result"],
            "reasoning_log": state.get("reasoning_log", []) + [reasoning_log],
            "current_step": "profile",
            "completed_steps": state.get("completed_steps", []) + ["profile"],
            "pending_approval": True,
            "approval_context": {
                "agent": "ProfileAgent",
                "recommendations": response["recommendations"],
                "reasoning": response["reasoning"],
                "impact": response["impact"]
            },
            "updated_at": get_timestamp()
        }

    def _human_review_node(self, state: EDAState) -> Dict[str, Any]:
        """Human review node - interrupts for human input"""

        # This node causes an interrupt
        # The workflow will pause here until resumed with user decision

        return {
            **state,
            "current_step": "human_review",
            "updated_at": get_timestamp()
        }

    def _route_after_review(self, state: EDAState) -> Literal["continue", "retry"]:
        """Route based on user decision"""

        # Check if user approved
        user_decisions = state.get("user_decisions", [])

        if not user_decisions:
            return "continue"

        last_decision = user_decisions[-1]

        if last_decision["decision"] == "approved":
            return "continue"
        elif last_decision["decision"] == "rejected":
            return "retry"
        else:
            return "continue"

    def create_initial_state(
        self,
        dataset_path: str,
        session_id: str,
        workflow_type: Literal["quick_profile", "deep_clean", "feature_engineering", "custom"]
    ) -> EDAState:
        """Create initial state for workflow"""

        # Get dataset info
        dataset_handle = DatasetHandle(dataset_path)
        info = dataset_handle.get_info()

        return EDAState(
            dataset_id=session_id,
            dataset_path=dataset_path,
            dataset_mode=info["mode"],
            dataset_size_bytes=info["file_size"],
            dataset_rows=info["rows"],
            dataset_cols=info["columns"],
            workflow_type=workflow_type,
            current_step="",
            completed_steps=[],
            pending_approval=False,
            approval_context=None,
            profile_results=None,
            quality_results=None,
            feature_results=None,
            stat_results=None,
            visualizations=[],
            reasoning_log=[],
            user_messages=[],
            user_decisions=[],
            pending_transformations=[],
            applied_transformations=[],
            session_id=session_id,
            created_at=get_timestamp(),
            updated_at=get_timestamp()
        )

    def run(self, initial_state: EDAState, thread_id: str):
        """
        Run the workflow

        Args:
            initial_state: Initial EDAState
            thread_id: Thread ID for checkpointing

        Returns:
            Generator of state updates
        """
        config = {"configurable": {"thread_id": thread_id}}

        for event in self.graph.stream(initial_state, config):
            yield event

    def get_state(self, thread_id: str) -> EDAState:
        """Get current state for a thread"""
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.get_state(config)

    def update_state(self, thread_id: str, updates: Dict[str, Any]):
        """Update state and resume workflow"""
        config = {"configurable": {"thread_id": thread_id}}
        self.graph.update_state(config, updates)
