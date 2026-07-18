"""
Progress Tracker Component
Provides visual workflow progress indicators with status, timing, and stage details
"""

import streamlit as st
from typing import List, Dict, Optional, Literal
from datetime import datetime
from pathlib import Path


class WorkflowStep:
    """Represents a single step in the workflow"""

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        icon: str,
        status: Literal["pending", "running", "completed", "failed", "skipped"] = "pending"
    ):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.status = status
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.substeps: List[str] = []

    def start(self):
        """Mark step as started"""
        self.status = "running"
        self.start_time = datetime.now()

    def complete(self):
        """Mark step as completed"""
        self.status = "completed"
        self.end_time = datetime.now()

    def fail(self, error: str):
        """Mark step as failed"""
        self.status = "failed"
        self.end_time = datetime.now()
        self.error_message = error

    def skip(self):
        """Mark step as skipped"""
        self.status = "skipped"

    @property
    def duration(self) -> Optional[float]:
        """Get duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def status_emoji(self) -> str:
        """Get emoji for current status"""
        emoji_map = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "skipped": "⏭️"
        }
        return emoji_map.get(self.status, "❓")

    @property
    def status_color(self) -> str:
        """Get color for current status"""
        color_map = {
            "pending": "#9CA3AF",  # Gray
            "running": "#3B82F6",  # Blue
            "completed": "#10B981", # Green
            "failed": "#EF4444",    # Red
            "skipped": "#6B7280"    # Dark Gray
        }
        return color_map.get(self.status, "#6B7280")


class WorkflowProgressTracker:
    """Manages and displays workflow progress"""

    def __init__(self, workflow_name: str, steps: List[WorkflowStep]):
        self.workflow_name = workflow_name
        self.steps = steps
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None

    @property
    def current_step(self) -> Optional[WorkflowStep]:
        """Get currently running step"""
        for step in self.steps:
            if step.status == "running":
                return step
        return None

    @property
    def completed_count(self) -> int:
        """Count completed steps"""
        return sum(1 for step in self.steps if step.status == "completed")

    @property
    def total_steps(self) -> int:
        """Total number of steps"""
        return len(self.steps)

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_steps == 0:
            return 0.0
        return (self.completed_count / self.total_steps) * 100

    @property
    def estimated_time_remaining(self) -> Optional[str]:
        """Estimate time remaining based on completed steps"""
        completed = [s for s in self.steps if s.status == "completed" and s.duration]

        if not completed:
            return None

        avg_duration = sum(s.duration for s in completed) / len(completed)
        remaining_steps = self.total_steps - self.completed_count
        estimated_seconds = avg_duration * remaining_steps

        if estimated_seconds < 60:
            return f"~{int(estimated_seconds)}s"
        elif estimated_seconds < 3600:
            return f"~{int(estimated_seconds / 60)}m"
        else:
            return f"~{int(estimated_seconds / 3600)}h {int((estimated_seconds % 3600) / 60)}m"

    def render(self, container=None):
        """Render the progress tracker UI"""
        target = container if container else st

        # Main progress header
        target.markdown(f"### 🎯 {self.workflow_name}")

        # Overall progress bar
        progress_col1, progress_col2 = target.columns([4, 1])

        with progress_col1:
            target.progress(
                self.progress_percentage / 100,
                text=f"Progress: {self.completed_count}/{self.total_steps} steps completed"
            )

        with progress_col2:
            if self.estimated_time_remaining:
                target.metric("ETA", self.estimated_time_remaining)

        target.markdown("---")

        # Step-by-step breakdown
        for i, step in enumerate(self.steps):
            self._render_step(step, i + 1, target)

    def _render_step(self, step: WorkflowStep, step_number: int, target):
        """Render a single step"""

        # Determine if this is the active step
        is_active = step.status == "running"

        # Create step container with conditional styling
        step_container = target.container()

        with step_container:
            col1, col2, col3 = st.columns([0.5, 6, 2])

            with col1:
                # Status indicator
                st.markdown(
                    f"<div style='font-size: 1.5em; text-align: center;'>{step.status_emoji}</div>",
                    unsafe_allow_html=True
                )

            with col2:
                # Step name and description
                step_style = "font-weight: bold; font-size: 1.1em;" if is_active else ""
                st.markdown(
                    f"<div style='{step_style}'>{step.icon} {step.name}</div>",
                    unsafe_allow_html=True
                )

                # Show description for running step
                if is_active or step.status == "failed":
                    st.caption(step.description)

                # Show error message if failed
                if step.status == "failed" and step.error_message:
                    st.error(f"Error: {step.error_message}")

                # Show substeps if running
                if is_active and step.substeps:
                    with st.expander("Details", expanded=True):
                        for substep in step.substeps:
                            st.markdown(f"• {substep}")

            with col3:
                # Duration or status
                if step.duration:
                    st.caption(f"⏱️ {step.duration:.1f}s")
                elif step.status == "running":
                    st.caption("In progress...")
                elif step.status == "pending":
                    st.caption("Waiting...")

        # Add connector line (except for last step)
        if step_number < len(self.steps):
            target.markdown(
                f"<div style='margin-left: 20px; border-left: 2px dashed {step.status_color}; height: 20px;'></div>",
                unsafe_allow_html=True
            )

    def render_compact(self, container=None):
        """Render a compact horizontal progress indicator"""
        target = container if container else st

        # Header
        cols = target.columns([3, 1])
        with cols[0]:
            target.markdown(f"**{self.workflow_name}**")
        with cols[1]:
            target.caption(f"{self.completed_count}/{self.total_steps}")

        # Horizontal step indicators
        step_cols = target.columns(len(self.steps))

        for i, step in enumerate(self.steps):
            with step_cols[i]:
                # Color-coded progress indicator
                if step.status == "completed":
                    target.markdown(f"<div style='text-align: center; color: {step.status_color};'>{step.status_emoji}<br/><small>{step.name}</small></div>", unsafe_allow_html=True)
                elif step.status == "running":
                    target.markdown(f"<div style='text-align: center; color: {step.status_color}; animation: pulse 2s infinite;'>{step.status_emoji}<br/><small>{step.name}</small></div>", unsafe_allow_html=True)
                else:
                    target.markdown(f"<div style='text-align: center; color: {step.status_color};'>{step.status_emoji}<br/><small>{step.name}</small></div>", unsafe_allow_html=True)

        # Overall progress bar
        target.progress(self.progress_percentage / 100)


# Pre-defined agent steps
AGENT_STEPS = {
    "profile": WorkflowStep(
        id="profile",
        name="Profile Dataset",
        description="Analyzing dataset structure, types, and basic statistics",
        icon="📊"
    ),
    "quality": WorkflowStep(
        id="quality",
        name="Quality Check",
        description="Detecting duplicates, outliers, and inconsistencies",
        icon="✅"
    ),
    "transform": WorkflowStep(
        id="transform",
        name="Transform Data",
        description="Applying cleaning and transformation operations",
        icon="🔧"
    ),
    "visualization": WorkflowStep(
        id="visualization",
        name="Generate Visualizations",
        description="Creating distribution plots, heatmaps, and charts",
        icon="🎨"
    ),
    "feature": WorkflowStep(
        id="feature",
        name="Feature Analysis",
        description="Analyzing correlations and feature importance",
        icon="🔍"
    ),
    "stat": WorkflowStep(
        id="stat",
        name="Statistical Tests",
        description="Running statistical tests and hypothesis testing",
        icon="📈"
    )
}


def create_workflow_tracker(workflow_type: str) -> WorkflowProgressTracker:
    """Factory function to create workflow tracker"""

    workflow_configs = {
        "quick_analysis": {
            "name": "Quick Analysis",
            "steps": ["profile", "quality", "visualization"]
        },
        "complete_analysis": {
            "name": "Complete Analysis",
            "steps": ["profile", "quality", "visualization", "feature", "stat", "transform"]
        },
        "deep_dive": {
            "name": "Deep Dive Analysis",
            "steps": ["profile", "quality", "visualization", "feature", "stat"]
        },
        "ml_prep": {
            "name": "ML Preparation",
            "steps": ["profile", "quality", "feature", "transform"]
        }
    }

    config = workflow_configs.get(workflow_type, workflow_configs["complete_analysis"])

    # Create step instances
    steps = [AGENT_STEPS[step_id] for step_id in config["steps"]]

    return WorkflowProgressTracker(config["name"], steps)


# CSS for animations
PROGRESS_TRACKER_CSS = """
<style>
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.step-container {
    transition: all 0.3s ease;
}

.step-container:hover {
    background-color: #f3f4f6;
    border-radius: 8px;
}

.progress-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.85em;
    font-weight: 600;
}

.badge-completed {
    background-color: #d1fae5;
    color: #065f46;
}

.badge-running {
    background-color: #dbeafe;
    color: #1e40af;
}

.badge-pending {
    background-color: #f3f4f6;
    color: #4b5563;
}

.badge-failed {
    background-color: #fee2e2;
    color: #991b1b;
}
</style>
"""
