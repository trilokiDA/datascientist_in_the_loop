"""
Approval Gate Component
Enables human-in-the-loop review between agent executions
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime


class ApprovalGate:
    """Human-in-the-loop approval component for agent results"""

    def __init__(self, agent_name: str, result: Dict[str, Any], step_id: str):
        """
        Initialize approval gate

        Args:
            agent_name: Display name of the agent (e.g., "ProfileAgent")
            result: Agent's result dictionary with reasoning, impact, etc.
            step_id: Unique identifier for this step (e.g., "profile", "quality")
        """
        self.agent_name = agent_name
        self.result = result
        self.step_id = step_id

    def render(self) -> Optional[str]:
        """
        Renders approval UI and returns user decision

        Returns:
            "approved" - Continue to next agent
            "retry" - Re-run this agent
            "stop" - Stop the workflow
            None - Still waiting for user decision
        """
        st.divider()

        # Header
        st.markdown(f"""
        <div style="background-color: #f0f7ff; padding: 1rem; border-radius: 8px; border-left: 5px solid #1f77b4;">
            <h3 style="margin: 0; color: #1f77b4;">🚦 Review {self.agent_name} Results</h3>
            <p style="margin: 0.5rem 0 0 0; color: #666;">Review the agent's findings before continuing to the next step</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")  # Spacing

        # Summary Metrics
        self._render_summary()

        # Key Findings
        self._render_key_findings()

        # Additional Details (collapsible)
        self._render_detailed_results()

        # Decision Prompt
        st.markdown("")  # Spacing
        st.markdown("---")

        return self._render_decision_buttons()

    def _render_summary(self):
        """Render summary metrics"""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            confidence = self.result.get('confidence', 0.0)
            confidence_color = "green" if confidence >= 0.8 else "orange" if confidence >= 0.6 else "red"
            st.metric(
                "Confidence Score",
                f"{confidence:.0%}",
                help="AI's confidence in its analysis"
            )

        with col2:
            metric_count = self._count_issues()
            metric_label = self._get_metric_label()
            metric_help = self._get_metric_help()
            st.metric(
                metric_label,
                metric_count,
                help=metric_help
            )

        with col3:
            rec_count = len(self.result.get('recommendations', []))
            st.metric(
                "Recommendations",
                rec_count,
                help="Number of actionable recommendations provided"
            )

        with col4:
            complexity = self._assess_complexity()
            complexity_emoji = "🟢" if complexity == "Low" else "🟡" if complexity == "Medium" else "🔴"
            st.metric(
                "Complexity",
                f"{complexity_emoji} {complexity}",
                help="Estimated complexity of findings"
            )

    def _render_key_findings(self):
        """Render key findings section"""
        st.subheader("📋 Key Findings")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🧠 Reasoning**")
            reasoning = self.result.get('reasoning', 'No reasoning provided')
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; min-height: 100px;">
                {reasoning}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("**💡 Impact**")
            impact = self.result.get('impact', 'No impact assessment provided')
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; min-height: 100px;">
                {impact}
            </div>
            """, unsafe_allow_html=True)

        # Recommendations
        recommendations = self.result.get('recommendations', [])
        if recommendations:
            st.markdown("**✅ Recommendations**")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")

    def _render_detailed_results(self):
        """Render detailed results in expandable section"""
        with st.expander("🔍 View Detailed Results", expanded=False):
            result_data = self.result.get('result', {})

            if not result_data:
                st.info("No detailed results available")
                return

            # Display based on agent type
            if self.step_id == "profile":
                self._render_profile_details(result_data)
            elif self.step_id == "quality":
                self._render_quality_details(result_data)
            elif self.step_id == "transform":
                self._render_transform_details(result_data)
            elif self.step_id == "visualization":
                self._render_visualization_details(result_data)
            elif self.step_id == "feature":
                self._render_feature_details(result_data)
            elif self.step_id == "stat":
                self._render_stat_details(result_data)
            else:
                # Generic display
                st.json(result_data, expanded=False)

    def _render_profile_details(self, data: Dict):
        """Render profile-specific details"""
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Dataset Info**")
            basic = data.get('basic_info', {})
            st.markdown(f"- Rows: {basic.get('rows', 'N/A'):,}")
            st.markdown(f"- Columns: {basic.get('columns', 'N/A')}")
            st.markdown(f"- Size: {basic.get('file_size', 'N/A')}")

        with col2:
            st.markdown("**Column Types**")
            types = data.get('column_types', {})
            st.markdown(f"- Numeric: {len(types.get('numeric', []))}")
            st.markdown(f"- Categorical: {len(types.get('categorical', []))}")
            st.markdown(f"- Datetime: {len(types.get('datetime', []))}")

        # Issues
        issues = data.get('issues', {})
        if issues:
            st.markdown("**⚠️ Issues**")
            if issues.get('high_missing_cols'):
                st.warning(f"High missing: {', '.join(issues['high_missing_cols'][:3])}")
            if issues.get('high_cardinality_cols'):
                st.info(f"High cardinality: {', '.join(issues['high_cardinality_cols'][:3])}")

    def _render_quality_details(self, data: Dict):
        """Render quality-specific details"""
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Data Quality Issues**")
            dup_pct = data.get('duplicates', {}).get('duplicate_percentage', 0)
            st.markdown(f"- Duplicates: {dup_pct:.1f}%")

            outlier_cols = data.get('outliers', {}).get('columns_with_outliers', 0)
            st.markdown(f"- Outlier Columns: {outlier_cols}")

        with col2:
            st.markdown("**Data Integrity**")
            inconsist = data.get('inconsistencies', {}).get('inconsistency_count', 0)
            st.markdown(f"- Inconsistencies: {inconsist}")

            type_issues = data.get('data_types', {}).get('type_issue_count', 0)
            st.markdown(f"- Type Issues: {type_issues}")

    def _render_transform_details(self, data: Dict):
        """Render transformation-specific details"""
        total = data.get('total_transformations', 0)
        high = data.get('high_priority', 0)
        medium = data.get('medium_priority', 0)
        low = data.get('low_priority', 0)

        st.markdown(f"**Proposed Transformations: {total}**")
        st.markdown(f"- 🔴 High Priority: {high}")
        st.markdown(f"- 🟡 Medium Priority: {medium}")
        st.markdown(f"- 🟢 Low Priority: {low}")

        # Show first few transformations
        transforms = data.get('transformations', [])[:3]
        if transforms:
            st.markdown("**Sample Transformations:**")
            for t in transforms:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t.get('priority', 'low'), "⚪")
                st.markdown(f"{priority_emoji} {t.get('description', 'N/A')}")

    def _render_visualization_details(self, data: Dict):
        """Render visualization-specific details with thumbnail gallery"""
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Visualization Overview**")
            st.markdown(f"- Total Plots: {data.get('total_plots', 0)}")
            st.markdown(f"- Sample Size: {data.get('sample_size', 0):,} rows")

        with col2:
            st.markdown("**Plot Types Generated**")
            plots = data.get('plots', [])
            plot_types = {}
            for plot in plots:
                plot_type = plot.get('type', 'unknown')
                plot_types[plot_type] = plot_types.get(plot_type, 0) + 1

            for plot_type, count in plot_types.items():
                type_label = plot_type.replace('_', ' ').title()
                st.markdown(f"- {type_label}: {count}")

        # Thumbnail Gallery
        if plots:
            st.markdown("---")
            st.markdown("**📊 Quick Preview (Thumbnail Gallery)**")
            st.caption("Click on any thumbnail to view full-size plot")

            # Show up to 5 thumbnails in a grid
            thumbnail_plots = plots[:5]

            # Create columns for thumbnails (3 per row)
            num_cols = 3
            rows = [thumbnail_plots[i:i + num_cols] for i in range(0, len(thumbnail_plots), num_cols)]

            for row_plots in rows:
                cols = st.columns(num_cols)
                for idx, plot in enumerate(row_plots):
                    with cols[idx]:
                        try:
                            from PIL import Image
                            import os

                            plot_path = plot.get('path')
                            if plot_path and os.path.exists(plot_path):
                                # Load and display thumbnail
                                image = Image.open(plot_path)

                                # Display thumbnail with caption
                                plot_type = plot.get('type', 'plot').replace('_', ' ').title()
                                col_name = plot.get('column', 'N/A')
                                caption = f"{plot_type} - {col_name}"

                                st.image(image, caption=caption, use_container_width=True)

                                # Add expand button
                                if st.button(f"🔍 View Full Size", key=f"expand_plot_{plot.get('path', idx)}", use_container_width=True):
                                    # Show in expander
                                    with st.expander(f"📈 {caption}", expanded=True):
                                        st.image(image, use_container_width=True)
                                        if 'statistics' in plot:
                                            stats = plot['statistics']
                                            st.caption(f"Mean: {stats.get('mean', 0):.2f} | Median: {stats.get('median', 0):.2f} | Std: {stats.get('std', 0):.2f}")
                            else:
                                st.info(f"Plot file not found")
                        except Exception as e:
                            st.warning(f"Could not load thumbnail: {str(e)}")

            if len(plots) > 5:
                st.info(f"💡 **{len(plots) - 5} more plots available** in the Visualizations tab after approval")

        # Show plot list (collapsed)
        if plots:
            with st.expander(f"📋 View Complete Plot List ({len(plots)} plots)"):
                for i, plot in enumerate(plots, 1):
                    plot_type = plot.get('type', 'plot').replace('_', ' ').title()
                    col_name = plot.get('column', 'N/A')
                    st.markdown(f"{i}. {plot_type} - {col_name}")

        # Summary
        summary = data.get('summary', {})
        if summary:
            st.markdown("**Summary Insights:**")
            for key, value in list(summary.items())[:3]:
                if isinstance(value, (int, float)):
                    st.markdown(f"- {key.replace('_', ' ').title()}: {value}")

    def _render_feature_details(self, data: Dict):
        """Render feature-specific details"""
        corr_data = data.get('correlations', {})
        st.markdown(f"**Correlations**")
        st.markdown(f"- Numeric Features: {corr_data.get('num_numeric_features', 0)}")
        st.markdown(f"- Strong Correlations: {len(corr_data.get('strong_correlations', []))}")

    def _render_stat_details(self, data: Dict):
        """Render statistics-specific details"""
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Statistical Tests**")

            # Count normality tests
            normality_tests = data.get('normality_tests', {})
            norm_results = normality_tests.get('results', [])
            st.markdown(f"- Normality Tests: {len(norm_results)} columns")

            # Count hypothesis tests
            hypothesis_tests = data.get('hypothesis_tests', {})
            hyp_results = hypothesis_tests.get('results', [])
            st.markdown(f"- Hypothesis Tests: {len(hyp_results)}")

        with col2:
            st.markdown("**Analysis Performed**")

            # Sample size
            sample_size = data.get('sample_size', 0)
            st.markdown(f"- Sample Size: {sample_size:,} rows")

            # Distribution analysis
            dist_analysis = data.get('distribution_analysis', {})
            if dist_analysis:
                st.markdown(f"- Distributions: {len(dist_analysis.get('numeric_distributions', []))}")

        # Show normality summary
        if norm_results:
            st.markdown("**Normality Test Summary:**")
            normal_count = sum(1 for r in norm_results if any(
                test.get('is_normal', False)
                for test in r.get('tests', {}).values()
            ))
            st.markdown(f"- {normal_count} of {len(norm_results)} columns appear normally distributed")

        # Show hypothesis tests summary
        if hyp_results:
            st.markdown("**Hypothesis Tests:**")
            for i, test in enumerate(hyp_results[:3], 1):  # Show first 3
                test_type = test.get('test_type', 'Unknown')
                significant = test.get('is_significant', False)
                status = "✅ Significant" if significant else "ℹ️ Not significant"
                st.markdown(f"{i}. {test_type}: {status}")

            if len(hyp_results) > 3:
                st.markdown(f"*...and {len(hyp_results) - 3} more tests*")

    def _render_decision_buttons(self) -> Optional[str]:
        """Render decision buttons and return user choice"""

        st.markdown("""
        <h4 style="color: #1f77b4; margin-bottom: 0.5rem;">📊 How would you like to proceed?</h4>
        <p style="color: #666; margin-bottom: 1rem;">Choose an action to continue the workflow</p>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

        with col1:
            if st.button(
                "✅ Approve & Continue to Next Agent",
                type="primary",
                use_container_width=True,
                key=f"approve_{self.step_id}",
                help="Results look good, proceed to the next analysis step"
            ):
                return "approved"

        with col2:
            if st.button(
                "🔄 Retry This Agent",
                use_container_width=True,
                key=f"retry_{self.step_id}",
                help="Re-run this agent (useful if you changed settings)"
            ):
                return "retry"

        with col3:
            if st.button(
                "⏩ Skip This Agent",
                use_container_width=True,
                key=f"skip_{self.step_id}",
                help="Skip this agent and continue (results won't be used)"
            ):
                return "skip"

        with col4:
            if st.button(
                "⏹️ Stop",
                use_container_width=True,
                key=f"stop_{self.step_id}",
                help="Stop the workflow completely"
            ):
                return "stop"

        return None

    def _count_issues(self) -> int:
        """Count total issues found by agent"""
        result_data = self.result.get('result', {})

        if self.step_id == "profile":
            issues = result_data.get('issues', {})
            count = 0
            count += len(issues.get('high_missing_cols', []))
            count += len(issues.get('high_cardinality_cols', []))
            count += len(issues.get('low_cardinality_cols', []))
            return count

        elif self.step_id == "quality":
            count = 0
            if result_data.get('duplicates', {}).get('has_duplicates'):
                count += 1
            if result_data.get('outliers', {}).get('has_outliers'):
                count += result_data['outliers'].get('columns_with_outliers', 0)
            count += result_data.get('inconsistencies', {}).get('inconsistency_count', 0)
            count += result_data.get('data_types', {}).get('type_issue_count', 0)
            return count

        elif self.step_id == "transform":
            return result_data.get('high_priority', 0)

        elif self.step_id == "visualization":
            # For visualization, return number of plots (not issues, but meaningful metric)
            return result_data.get('total_plots', 0)

        elif self.step_id == "feature":
            # For feature agent, return number of strong correlations
            corr_data = result_data.get('correlations', {})
            return len(corr_data.get('strong_correlations', []))

        elif self.step_id == "stat":
            # For stat agent, return number of tests performed
            normality_tests = result_data.get('normality_tests', {})
            hypothesis_tests = result_data.get('hypothesis_tests', {})

            norm_count = len(normality_tests.get('results', []))
            hyp_count = len(hypothesis_tests.get('results', []))

            return norm_count + hyp_count

        # Default
        return 0

    def _get_metric_label(self) -> str:
        """Get appropriate metric label based on agent type"""
        if self.step_id in ["profile", "quality", "transform"]:
            return "Issues Found"
        elif self.step_id == "visualization":
            return "Plots Generated"
        elif self.step_id == "feature":
            return "Key Findings"
        elif self.step_id == "stat":
            return "Tests Run"
        else:
            return "Findings"

    def _get_metric_help(self) -> str:
        """Get appropriate help text based on agent type"""
        if self.step_id in ["profile", "quality"]:
            return "Number of potential issues or concerns identified"
        elif self.step_id == "transform":
            return "Number of high-priority transformations proposed"
        elif self.step_id == "visualization":
            return "Number of visualization plots created"
        elif self.step_id == "feature":
            return "Number of strong correlations or key features found"
        elif self.step_id == "stat":
            return "Number of statistical tests performed"
        else:
            return "Number of findings from this agent"

    def _assess_complexity(self) -> str:
        """Assess complexity of findings"""
        metric_count = self._count_issues()

        # For visualization, stat, and feature agents, use different thresholds
        if self.step_id in ["visualization", "stat", "feature"]:
            # These agents don't have "issues" - higher numbers are good
            if metric_count == 0:
                return "Low"
            elif metric_count <= 10:
                return "Medium"
            else:
                return "High"
        else:
            # For profile, quality, transform - issues are problems
            if metric_count == 0:
                return "Low"
            elif metric_count <= 5:
                return "Medium"
            else:
                return "High"


def store_user_decision(step_id: str, decision: str, feedback: str = None):
    """
    Store user decision in session state

    Args:
        step_id: Agent step identifier
        decision: User's decision (approved/retry/skip/stop)
        feedback: Optional user feedback text
    """
    if "user_decisions" not in st.session_state:
        st.session_state.user_decisions = []

    decision_record = {
        "step_id": step_id,
        "decision": decision,
        "timestamp": datetime.now().isoformat(),
        "feedback": feedback
    }

    st.session_state.user_decisions.append(decision_record)
