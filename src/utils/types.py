from typing import TypedDict, List, Dict, Literal, Optional, Any
from datetime import datetime


class AgentResponse(TypedDict):
    """Standard response structure for all agents"""
    result: Dict[str, Any]
    reasoning: str
    impact: str
    recommendations: List[str]
    confidence: float


class ReasoningLog(TypedDict):
    """Log entry for agent reasoning"""
    timestamp: str
    agent: str
    action: str
    reasoning: str
    impact: str
    confidence: float


class Transformation(TypedDict):
    """Data transformation metadata"""
    id: str
    type: str
    description: str
    params: Dict[str, Any]
    reasoning: str
    impact: str
    approved: bool


class UserDecision(TypedDict):
    """User decision at approval gate"""
    step_id: str
    decision: Literal["approved", "rejected", "modified"]
    timestamp: str
    feedback: Optional[str]


class EDAState(TypedDict):
    """Main state object for LangGraph"""
    # Data references
    dataset_id: str
    dataset_path: str
    dataset_mode: Literal["in_memory", "sampled"]
    dataset_size_bytes: int
    dataset_rows: int
    dataset_cols: int

    # Workflow control
    workflow_type: Literal["quick_profile", "deep_clean", "feature_engineering", "custom"]
    current_step: str
    completed_steps: List[str]
    pending_approval: bool
    approval_context: Optional[Dict[str, Any]]

    # Analysis artifacts
    profile_results: Optional[Dict[str, Any]]
    quality_results: Optional[Dict[str, Any]]
    feature_results: Optional[Dict[str, Any]]
    stat_results: Optional[Dict[str, Any]]
    visualizations: List[str]

    # Explainability
    reasoning_log: List[ReasoningLog]

    # Human feedback
    user_messages: List[str]
    user_decisions: List[UserDecision]

    # Transformations
    pending_transformations: List[Transformation]
    applied_transformations: List[Transformation]

    # Session metadata
    session_id: str
    created_at: str
    updated_at: str


class WorkflowConfig(TypedDict):
    """Configuration for pre-defined workflows"""
    name: str
    description: str
    steps: List[str]
    interrupts: List[str]
    estimated_time_mins: int


# Pre-defined workflow configurations
WORKFLOWS: Dict[str, WorkflowConfig] = {
    "quick_profile": {
        "name": "Quick Profile",
        "description": "Fast 5-min overview of dataset health",
        "steps": ["profile", "quality_check", "basic_viz"],
        "interrupts": ["after_profile"],
        "estimated_time_mins": 5
    },
    "deep_clean": {
        "name": "Deep Clean",
        "description": "Thorough cleaning pipeline with multiple checkpoints",
        "steps": [
            "profile",
            "quality_check",
            "outlier_analysis",
            "missing_value_analysis",
            "human_review",
            "transform"
        ],
        "interrupts": ["after_quality", "before_transform"],
        "estimated_time_mins": 15
    },
    "feature_engineering": {
        "name": "Feature Engineering",
        "description": "ML prep: find relationships, suggest new features",
        "steps": [
            "profile",
            "correlation_analysis",
            "feature_importance",
            "interaction_detection",
            "human_review",
            "engineer_features"
        ],
        "interrupts": ["after_correlation", "before_engineer"],
        "estimated_time_mins": 20
    }
}


# Constants
MEMORY_THRESHOLD = 500_000_000  # 500MB
SAMPLE_SIZE_PROFILING = 100_000
SAMPLE_SIZE_VISUALIZATION = 10_000
