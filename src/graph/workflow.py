from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pathlib import Path

from src.utils.types import EDAState
from src.data.dataset_handle import DatasetHandle
from src.agents.profile_agent import ProfileAgent
from src.agents.quality_agent import QualityAgent
from src.agents.transform_agent import TransformAgent
from src.agents.viz_agent import VisualizationAgent
from src.agents.feature_agent import FeatureAgent
from src.agents.stat_agent import StatAgent
from src.utils.helpers import get_timestamp, create_reasoning_log


class EDAWorkflow:
    """
    LangGraph-based workflow orchestration for EDA pipeline
    """

    def __init__(self, checkpoint_dir: str = "data/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Initialize checkpoint saver (MemorySaver for now, can use SqliteSaver with langgraph-checkpoint-sqlite package)
        self.checkpointer = MemorySaver()

        # Initialize agents
        self.profile_agent = ProfileAgent()
        self.quality_agent = QualityAgent()
        self.transform_agent = TransformAgent()
        self.viz_agent = VisualizationAgent()
        self.feature_agent = FeatureAgent()
        self.stat_agent = StatAgent()

        # Build graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""

        # Create state graph
        workflow = StateGraph(EDAState)

        # Add nodes
        workflow.add_node("profile", self._profile_node)
        workflow.add_node("quality_check", self._quality_node)
        workflow.add_node("transform_proposal", self._transform_node)
        workflow.add_node("human_review_profile", self._human_review_node)
        workflow.add_node("human_review_quality", self._human_review_node)
        workflow.add_node("human_review_transforms", self._human_review_node)

        # Quick Profile Workflow
        # profile → human_review_profile → quality_check → human_review_quality → END

        # Set entry point
        workflow.set_entry_point("profile")

        # Profile → Human Review
        workflow.add_edge("profile", "human_review_profile")

        # Human Review Profile → Conditional
        workflow.add_conditional_edges(
            "human_review_profile",
            self._route_after_profile_review,
            {
                "quality": "quality_check",
                "retry": "profile",
                "end": END
            }
        )

        # Quality → Human Review
        workflow.add_edge("quality_check", "human_review_quality")

        # Human Review Quality → Conditional
        workflow.add_conditional_edges(
            "human_review_quality",
            self._route_after_quality_review,
            {
                "transform": "transform_proposal",
                "retry": "quality_check",
                "end": END
            }
        )

        # Transform → Human Review
        workflow.add_edge("transform_proposal", "human_review_transforms")

        # Human Review Transforms → Conditional
        workflow.add_conditional_edges(
            "human_review_transforms",
            self._route_after_transform_review,
            {
                "apply": END,  # In production, would go to apply_transforms node
                "retry": "transform_proposal",
                "end": END
            }
        )

        return workflow.compile(checkpointer=self.checkpointer)

    def _profile_node(self, state: EDAState) -> Dict[str, Any]:
        """Profile node - runs ProfileAgent"""

        # Get dataset handle
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
                "step": "profile",
                "agent": "ProfileAgent",
                "recommendations": response["recommendations"],
                "reasoning": response["reasoning"],
                "impact": response["impact"],
                "confidence": response["confidence"]
            },
            "updated_at": get_timestamp()
        }

    def _quality_node(self, state: EDAState) -> Dict[str, Any]:
        """Quality node - runs QualityAgent"""

        # Get dataset handle
        dataset_handle = DatasetHandle(state["dataset_path"])

        # Prepare context from previous steps
        context = {
            "profile_results": state.get("profile_results")
        }

        # Run quality agent
        response = self.quality_agent.analyze(dataset_handle, context)

        # Update state
        reasoning_log = create_reasoning_log(
            agent="QualityAgent",
            action="quality_assessment",
            reasoning=response["reasoning"],
            impact=response["impact"],
            confidence=response["confidence"]
        )

        return {
            **state,
            "quality_results": response["result"],
            "reasoning_log": state.get("reasoning_log", []) + [reasoning_log],
            "current_step": "quality_check",
            "completed_steps": state.get("completed_steps", []) + ["quality_check"],
            "pending_approval": True,
            "approval_context": {
                "step": "quality_check",
                "agent": "QualityAgent",
                "recommendations": response["recommendations"],
                "reasoning": response["reasoning"],
                "impact": response["impact"],
                "confidence": response["confidence"]
            },
            "updated_at": get_timestamp()
        }

    def _transform_node(self, state: EDAState) -> Dict[str, Any]:
        """Transform node - runs TransformAgent to propose transformations"""

        # Get dataset handle
        dataset_handle = DatasetHandle(state["dataset_path"])

        # Prepare context from previous steps
        context = {
            "profile_results": state.get("profile_results"),
            "quality_results": state.get("quality_results")
        }

        # Run transform agent
        response = self.transform_agent.analyze(dataset_handle, context)

        # Update state with proposed transformations
        reasoning_log = create_reasoning_log(
            agent="TransformAgent",
            action="transformation_proposal",
            reasoning=response["reasoning"],
            impact=response["impact"],
            confidence=response["confidence"]
        )

        # Store transformations as pending
        pending_transformations = response["result"].get("transformations", [])

        return {
            **state,
            "pending_transformations": pending_transformations,
            "reasoning_log": state.get("reasoning_log", []) + [reasoning_log],
            "current_step": "transform_proposal",
            "completed_steps": state.get("completed_steps", []) + ["transform_proposal"],
            "pending_approval": True,
            "approval_context": {
                "step": "transform_proposal",
                "agent": "TransformAgent",
                "recommendations": response["recommendations"],
                "reasoning": response["reasoning"],
                "impact": response["impact"],
                "confidence": response["confidence"],
                "transformations": pending_transformations
            },
            "updated_at": get_timestamp()
        }

    def _visualization_node(self, state: EDAState) -> Dict[str, Any]:
        """Visualization node - runs VisualizationAgent"""

        # Get dataset handle
        dataset_handle = DatasetHandle(state["dataset_path"])

        # Prepare context from previous steps
        context = {
            "profile_results": state.get("profile_results"),
            "quality_results": state.get("quality_results")
        }

        # Run visualization agent
        response = self.viz_agent.analyze(dataset_handle, context)

        # Update state
        reasoning_log = create_reasoning_log(
            agent="VisualizationAgent",
            action="visualization_generation",
            reasoning=response["reasoning"],
            impact=response["impact"],
            confidence=response["confidence"]
        )

        # Store visualization results
        viz_results = response["result"]

        return {
            **state,
            "visualizations": viz_results.get("plots", []),
            "viz_results": viz_results,
            "reasoning_log": state.get("reasoning_log", []) + [reasoning_log],
            "current_step": "visualization",
            "completed_steps": state.get("completed_steps", []) + ["visualization"],
            "pending_approval": True,
            "approval_context": {
                "step": "visualization",
                "agent": "VisualizationAgent",
                "recommendations": response["recommendations"],
                "reasoning": response["reasoning"],
                "impact": response["impact"],
                "confidence": response["confidence"],
                "viz_summary": viz_results.get("summary", {})
            },
            "updated_at": get_timestamp()
        }

    def _feature_analysis_node(self, state: EDAState) -> Dict[str, Any]:
        """Feature analysis node - runs FeatureAgent"""

        # Get dataset handle
        dataset_handle = DatasetHandle(state["dataset_path"])

        # Prepare context from previous steps
        context = {
            "profile_results": state.get("profile_results"),
            "quality_results": state.get("quality_results")
        }

        # Run feature agent
        response = self.feature_agent.analyze(dataset_handle, context)

        # Update state
        reasoning_log = create_reasoning_log(
            agent="FeatureAgent",
            action="feature_analysis",
            reasoning=response["reasoning"],
            impact=response["impact"],
            confidence=response["confidence"]
        )

        return {
            **state,
            "feature_results": response["result"],
            "reasoning_log": state.get("reasoning_log", []) + [reasoning_log],
            "current_step": "feature_analysis",
            "completed_steps": state.get("completed_steps", []) + ["feature_analysis"],
            "pending_approval": True,
            "approval_context": {
                "step": "feature_analysis",
                "agent": "FeatureAgent",
                "recommendations": response["recommendations"],
                "reasoning": response["reasoning"],
                "impact": response["impact"],
                "confidence": response["confidence"]
            },
            "updated_at": get_timestamp()
        }

    def _statistical_analysis_node(self, state: EDAState) -> Dict[str, Any]:
        """Statistical analysis node - runs StatAgent"""

        # Get dataset handle
        dataset_handle = DatasetHandle(state["dataset_path"])

        # Prepare context from previous steps
        context = {
            "profile_results": state.get("profile_results"),
            "quality_results": state.get("quality_results"),
            "feature_results": state.get("feature_results")
        }

        # Run stat agent
        response = self.stat_agent.analyze(dataset_handle, context)

        # Update state
        reasoning_log = create_reasoning_log(
            agent="StatAgent",
            action="statistical_analysis",
            reasoning=response["reasoning"],
            impact=response["impact"],
            confidence=response["confidence"]
        )

        return {
            **state,
            "stat_results": response["result"],
            "reasoning_log": state.get("reasoning_log", []) + [reasoning_log],
            "current_step": "statistical_analysis",
            "completed_steps": state.get("completed_steps", []) + ["statistical_analysis"],
            "pending_approval": True,
            "approval_context": {
                "step": "statistical_analysis",
                "agent": "StatAgent",
                "recommendations": response["recommendations"],
                "reasoning": response["reasoning"],
                "impact": response["impact"],
                "confidence": response["confidence"]
            },
            "updated_at": get_timestamp()
        }

    def _human_review_node(self, state: EDAState) -> Dict[str, Any]:
        """Human review node - interrupts for human input"""

        # This node causes an interrupt
        # The workflow will pause here until resumed with user decision

        return {
            **state,
            "current_step": f"human_review_{state['current_step']}",
            "updated_at": get_timestamp()
        }

    def _route_after_profile_review(self, state: EDAState) -> Literal["quality", "retry", "end"]:
        """Route based on user decision after profile review"""

        user_decisions = state.get("user_decisions", [])

        if not user_decisions:
            return "quality"  # Default: continue to quality

        last_decision = user_decisions[-1]

        if last_decision["decision"] == "approved":
            return "quality"
        elif last_decision["decision"] == "rejected":
            return "retry"
        else:
            return "end"

    def _route_after_quality_review(self, state: EDAState) -> Literal["transform", "retry", "end"]:
        """Route based on user decision after quality review"""

        user_decisions = state.get("user_decisions", [])

        if not user_decisions:
            return "transform"  # Default: continue to transform

        last_decision = user_decisions[-1]

        if last_decision["decision"] == "approved":
            return "transform"
        elif last_decision["decision"] == "rejected":
            return "retry"
        else:
            return "end"

    def _route_after_transform_review(self, state: EDAState) -> Literal["apply", "retry", "end"]:
        """Route based on user decision after transform review"""

        user_decisions = state.get("user_decisions", [])

        if not user_decisions:
            return "end"  # Default: end (wait for explicit approval)

        last_decision = user_decisions[-1]

        if last_decision["decision"] == "approved":
            return "apply"
        elif last_decision["decision"] == "rejected":
            return "retry"
        else:
            return "end"

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
        state_snapshot = self.graph.get_state(config)
        return state_snapshot.values if state_snapshot else None

    def update_state(self, thread_id: str, updates: Dict[str, Any]):
        """Update state and resume workflow"""
        config = {"configurable": {"thread_id": thread_id}}
        self.graph.update_state(config, updates)

    def resume(self, thread_id: str):
        """
        Resume workflow from checkpoint

        Args:
            thread_id: Thread ID to resume

        Returns:
            Generator of state updates
        """
        config = {"configurable": {"thread_id": thread_id}}

        for event in self.graph.stream(None, config):
            yield event
