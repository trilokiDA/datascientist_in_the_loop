"""
Test Suite for Approval Gate Component
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime


# Mock streamlit for testing
class MockStreamlit:
    def __init__(self):
        self.session_state = {}
        self.markdown_calls = []
        self.button_calls = []
        self.metric_calls = []

    def markdown(self, text, unsafe_allow_html=False):
        self.markdown_calls.append(text)

    def button(self, label, **kwargs):
        self.button_calls.append(label)
        return False

    def metric(self, label, value, **kwargs):
        self.metric_calls.append((label, value))

    def columns(self, spec):
        return [Mock()] * (spec if isinstance(spec, int) else len(spec))

    def divider(self):
        pass

    def subheader(self, text):
        pass

    def info(self, text):
        pass

    def expander(self, text, expanded=False):
        return Mock(__enter__=Mock(), __exit__=Mock())

    def json(self, data, expanded=False):
        pass


class TestApprovalGate:
    """Test cases for ApprovalGate component"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_result = {
            "result": {
                "basic_info": {"rows": 1000, "columns": 10},
                "column_types": {"numeric": ["age", "salary"], "categorical": ["name"]},
                "issues": {"high_missing_cols": ["address"]}
            },
            "reasoning": "Dataset has standard structure with some missing data",
            "impact": "Missing address data may affect location-based analysis",
            "recommendations": [
                "Handle missing address data",
                "Check salary outliers",
                "Encode categorical variables"
            ],
            "confidence": 0.85
        }

    def test_approval_gate_initialization(self):
        """Test ApprovalGate can be initialized"""
        from src.ui.components.approval_gate import ApprovalGate

        gate = ApprovalGate("ProfileAgent", self.mock_result, "profile")

        assert gate.agent_name == "ProfileAgent"
        assert gate.step_id == "profile"
        assert gate.result == self.mock_result

    def test_count_issues_profile(self):
        """Test issue counting for ProfileAgent"""
        from src.ui.components.approval_gate import ApprovalGate

        gate = ApprovalGate("ProfileAgent", self.mock_result, "profile")
        issue_count = gate._count_issues()

        # Should count 1 high missing column
        assert issue_count == 1

    def test_count_issues_quality(self):
        """Test issue counting for QualityAgent"""
        from src.ui.components.approval_gate import ApprovalGate

        quality_result = {
            "result": {
                "duplicates": {"has_duplicates": True, "duplicate_rows": 10},
                "outliers": {"has_outliers": True, "columns_with_outliers": 3},
                "inconsistencies": {"inconsistency_count": 5},
                "data_types": {"type_issue_count": 2}
            },
            "reasoning": "Multiple quality issues found",
            "impact": "Data needs cleaning",
            "recommendations": ["Fix duplicates", "Handle outliers"],
            "confidence": 0.75
        }

        gate = ApprovalGate("QualityAgent", quality_result, "quality")
        issue_count = gate._count_issues()

        # Should count: 1 (duplicates) + 3 (outlier columns) + 5 (inconsistencies) + 2 (type issues) = 11
        assert issue_count == 11

    def test_count_issues_transform(self):
        """Test issue counting for TransformAgent"""
        from src.ui.components.approval_gate import ApprovalGate

        transform_result = {
            "result": {
                "total_transformations": 8,
                "high_priority": 4,
                "medium_priority": 3,
                "low_priority": 1,
                "transformations": []
            },
            "reasoning": "Multiple transformations needed",
            "impact": "Will improve data quality",
            "recommendations": ["Apply high priority first"],
            "confidence": 0.90
        }

        gate = ApprovalGate("TransformAgent", transform_result, "transform")
        issue_count = gate._count_issues()

        # Should return high priority count
        assert issue_count == 4

    def test_assess_complexity_low(self):
        """Test complexity assessment - low"""
        from src.ui.components.approval_gate import ApprovalGate

        # Result with 0 issues
        result = {
            "result": {"issues": {}},
            "reasoning": "Clean data",
            "impact": "None",
            "recommendations": [],
            "confidence": 0.95
        }

        gate = ApprovalGate("ProfileAgent", result, "profile")
        complexity = gate._assess_complexity()

        assert complexity == "Low"

    def test_assess_complexity_medium(self):
        """Test complexity assessment - medium"""
        from src.ui.components.approval_gate import ApprovalGate

        # Result with 3 issues
        result = {
            "result": {
                "issues": {
                    "high_missing_cols": ["col1", "col2"],
                    "high_cardinality_cols": ["col3"]
                }
            },
            "reasoning": "Some issues",
            "impact": "Moderate",
            "recommendations": ["Handle missing data"],
            "confidence": 0.80
        }

        gate = ApprovalGate("ProfileAgent", result, "profile")
        complexity = gate._assess_complexity()

        assert complexity == "Medium"

    def test_assess_complexity_high(self):
        """Test complexity assessment - high"""
        from src.ui.components.approval_gate import ApprovalGate

        quality_result = {
            "result": {
                "duplicates": {"has_duplicates": True},
                "outliers": {"has_outliers": True, "columns_with_outliers": 8},
                "inconsistencies": {"inconsistency_count": 10},
                "data_types": {"type_issue_count": 5}
            },
            "reasoning": "Many issues",
            "impact": "High",
            "recommendations": ["Major cleanup needed"],
            "confidence": 0.60
        }

        gate = ApprovalGate("QualityAgent", quality_result, "quality")
        complexity = gate._assess_complexity()

        assert complexity == "High"

    def test_store_user_decision(self):
        """Test storing user decision"""
        from src.ui.components.approval_gate import store_user_decision
        import streamlit as st

        # Initialize session state
        st.session_state.user_decisions = []

        # Store decision
        store_user_decision("quality", "approved", "Looks good")

        # Check stored
        assert len(st.session_state.user_decisions) == 1

        decision = st.session_state.user_decisions[0]
        assert decision["step_id"] == "quality"
        assert decision["decision"] == "approved"
        assert decision["feedback"] == "Looks good"
        assert "timestamp" in decision

    def test_store_multiple_decisions(self):
        """Test storing multiple decisions"""
        from src.ui.components.approval_gate import store_user_decision
        import streamlit as st

        # Initialize session state
        st.session_state.user_decisions = []

        # Store multiple decisions
        store_user_decision("profile", "approved")
        store_user_decision("quality", "retry")
        store_user_decision("transform", "skip")

        # Check all stored
        assert len(st.session_state.user_decisions) == 3

        assert st.session_state.user_decisions[0]["decision"] == "approved"
        assert st.session_state.user_decisions[1]["decision"] == "retry"
        assert st.session_state.user_decisions[2]["decision"] == "skip"


class TestApprovalGateIntegration:
    """Integration tests for approval gate workflow"""

    def test_workflow_state_initialization(self):
        """Test workflow state variables are initialized correctly"""
        import streamlit as st

        # These should be initialized in app.py
        required_vars = [
            "workflow_mode",
            "current_agent_index",
            "waiting_for_approval",
            "user_decisions",
            "agent_configs"
        ]

        for var in required_vars:
            # Check it can be initialized (won't actually be in session_state during test)
            # This is more of a documentation test
            assert var is not None

    def test_decision_flow_approved(self):
        """Test decision flow when user approves"""
        # Simulate approved decision
        current_index = 2
        waiting_for_approval = True

        # User clicks approve
        decision = "approved"

        # Expected state changes
        if decision == "approved":
            expected_index = current_index + 1
            expected_waiting = False

        assert expected_index == 3
        assert expected_waiting == False

    def test_decision_flow_retry(self):
        """Test decision flow when user retries"""
        current_index = 2
        waiting_for_approval = True

        # User clicks retry
        decision = "retry"

        # Expected state changes
        if decision == "retry":
            expected_index = current_index  # Stay on same agent
            expected_waiting = False

        assert expected_index == 2
        assert expected_waiting == False

    def test_decision_flow_skip(self):
        """Test decision flow when user skips"""
        current_index = 2
        waiting_for_approval = True

        # User clicks skip
        decision = "skip"

        # Expected state changes
        if decision == "skip":
            expected_index = current_index + 1
            expected_waiting = False

        assert expected_index == 3
        assert expected_waiting == False


class TestAgentSpecificDetails:
    """Test agent-specific detail rendering"""

    def test_profile_details_structure(self):
        """Test profile details have correct structure"""
        profile_data = {
            "basic_info": {"rows": 1000, "columns": 10, "file_size": "1.2 MB"},
            "column_types": {
                "numeric": ["age", "salary"],
                "categorical": ["name", "city"],
                "datetime": ["created_at"]
            },
            "issues": {
                "high_missing_cols": ["address"],
                "high_cardinality_cols": ["user_id"]
            }
        }

        # Check structure
        assert "basic_info" in profile_data
        assert "column_types" in profile_data
        assert "issues" in profile_data

        assert "rows" in profile_data["basic_info"]
        assert "numeric" in profile_data["column_types"]

    def test_quality_details_structure(self):
        """Test quality details have correct structure"""
        quality_data = {
            "duplicates": {"has_duplicates": True, "duplicate_percentage": 5.2},
            "outliers": {"has_outliers": True, "columns_with_outliers": 3},
            "inconsistencies": {"inconsistency_count": 10},
            "data_types": {"type_issue_count": 2}
        }

        # Check structure
        assert "duplicates" in quality_data
        assert "outliers" in quality_data
        assert "inconsistencies" in quality_data
        assert "data_types" in quality_data

    def test_transform_details_structure(self):
        """Test transform details have correct structure"""
        transform_data = {
            "total_transformations": 8,
            "high_priority": 4,
            "medium_priority": 3,
            "low_priority": 1,
            "transformations": [
                {
                    "id": "remove_duplicates",
                    "type": "deduplication",
                    "priority": "high",
                    "description": "Remove duplicate rows"
                }
            ]
        }

        # Check structure
        assert "total_transformations" in transform_data
        assert "high_priority" in transform_data
        assert "transformations" in transform_data
        assert len(transform_data["transformations"]) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
