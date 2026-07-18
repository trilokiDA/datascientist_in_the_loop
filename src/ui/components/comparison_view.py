"""
Before/After Comparison View Component
Displays side-by-side comparisons of data transformations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TransformationComparison:
    """Data class for storing before/after comparison metrics"""
    transformation_id: str
    transformation_type: str
    column: str
    before_stats: Dict[str, Any]
    after_stats: Dict[str, Any]
    rows_affected: int
    impact_score: float


class ComparisonView:
    """Creates before/after comparison visualizations"""

    def __init__(self):
        pass

    def create_side_by_side_preview(
        self,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame,
        columns: List[str] = None,
        max_rows: int = 10
    ) -> None:
        """
        Display side-by-side data preview with highlighting

        Args:
            df_before: DataFrame before transformation
            df_after: DataFrame after transformation
            columns: Specific columns to show (None = all)
            max_rows: Maximum rows to display
        """

        if columns:
            df_before = df_before[columns]
            df_after = df_after[columns]

        # Limit rows
        df_before_preview = df_before.head(max_rows)
        df_after_preview = df_after.head(max_rows)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📤 Before Transformation")
            st.dataframe(
                df_before_preview,
                use_container_width=True,
                height=400
            )

        with col2:
            st.markdown("### 📥 After Transformation")

            # Highlight changes
            def highlight_changes(row):
                if row.name < len(df_before_preview):
                    before_row = df_before_preview.iloc[row.name]
                    styles = []
                    for col in df_after_preview.columns:
                        if col in before_row.index:
                            # Compare values
                            before_val = before_row[col]
                            after_val = row[col]

                            # Check if changed
                            try:
                                if pd.isna(before_val) and pd.isna(after_val):
                                    styles.append('')
                                elif pd.isna(before_val) or pd.isna(after_val):
                                    styles.append('background-color: #D1FAE5')  # Green for filled
                                elif before_val != after_val:
                                    styles.append('background-color: #DBEAFE')  # Blue for changed
                                else:
                                    styles.append('')
                            except:
                                styles.append('')
                        else:
                            styles.append('')
                    return styles
                return [''] * len(row)

            styled_df = df_after_preview.style.apply(highlight_changes, axis=1)
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=400
            )

        # Legend
        st.markdown("""
        <div style='padding: 10px; background-color: #F3F4F6; border-radius: 5px; margin-top: 10px;'>
            <small>
                <span style='background-color: #D1FAE5; padding: 2px 8px; border-radius: 3px;'>Green</span> = Filled missing value &nbsp;|&nbsp;
                <span style='background-color: #DBEAFE; padding: 2px 8px; border-radius: 3px;'>Blue</span> = Value changed &nbsp;|&nbsp;
                <span style='background-color: white; padding: 2px 8px; border-radius: 3px; border: 1px solid #E5E7EB;'>White</span> = Unchanged
            </small>
        </div>
        """, unsafe_allow_html=True)

    def create_delta_metrics(
        self,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame
    ) -> go.Figure:
        """
        Create delta metrics comparison chart

        Args:
            df_before: DataFrame before transformation
            df_after: DataFrame after transformation
        """

        metrics = []

        # Missing values
        missing_before = df_before.isnull().sum().sum()
        missing_after = df_after.isnull().sum().sum()
        metrics.append({
            'metric': 'Missing Values',
            'before': missing_before,
            'after': missing_after,
            'delta': missing_after - missing_before,
            'delta_pct': ((missing_after - missing_before) / missing_before * 100) if missing_before > 0 else 0
        })

        # Duplicates
        dup_before = df_before.duplicated().sum()
        dup_after = df_after.duplicated().sum()
        metrics.append({
            'metric': 'Duplicates',
            'before': dup_before,
            'after': dup_after,
            'delta': dup_after - dup_before,
            'delta_pct': ((dup_after - dup_before) / dup_before * 100) if dup_before > 0 else 0
        })

        # Data points
        points_before = df_before.shape[0] * df_before.shape[1]
        points_after = df_after.shape[0] * df_after.shape[1]
        metrics.append({
            'metric': 'Total Data Points',
            'before': points_before,
            'after': points_after,
            'delta': points_after - points_before,
            'delta_pct': ((points_after - points_before) / points_before * 100) if points_before > 0 else 0
        })

        # Numeric columns - check for outliers
        numeric_before = df_before.select_dtypes(include=[np.number])
        numeric_after = df_after.select_dtypes(include=[np.number])

        if len(numeric_before.columns) > 0:
            outliers_before = 0
            outliers_after = 0

            for col in numeric_before.columns:
                if col in numeric_after.columns:
                    # Calculate outliers using IQR method
                    Q1_before = numeric_before[col].quantile(0.25)
                    Q3_before = numeric_before[col].quantile(0.75)
                    IQR_before = Q3_before - Q1_before
                    outliers_before += ((numeric_before[col] < Q1_before - 1.5 * IQR_before) |
                                       (numeric_before[col] > Q3_before + 1.5 * IQR_before)).sum()

                    Q1_after = numeric_after[col].quantile(0.25)
                    Q3_after = numeric_after[col].quantile(0.75)
                    IQR_after = Q3_after - Q1_after
                    outliers_after += ((numeric_after[col] < Q1_after - 1.5 * IQR_after) |
                                      (numeric_after[col] > Q3_after + 1.5 * IQR_after)).sum()

            metrics.append({
                'metric': 'Outliers',
                'before': outliers_before,
                'after': outliers_after,
                'delta': outliers_after - outliers_before,
                'delta_pct': ((outliers_after - outliers_before) / outliers_before * 100) if outliers_before > 0 else 0
            })

        # Create visualization
        fig = go.Figure()

        metric_names = [m['metric'] for m in metrics]
        before_values = [m['before'] for m in metrics]
        after_values = [m['after'] for m in metrics]
        deltas = [m['delta'] for m in metrics]

        # Before bars
        fig.add_trace(go.Bar(
            name='Before',
            x=metric_names,
            y=before_values,
            marker_color='#EF4444',
            text=[f"{v:,}" for v in before_values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Before: %{y:,}<extra></extra>'
        ))

        # After bars
        fig.add_trace(go.Bar(
            name='After',
            x=metric_names,
            y=after_values,
            marker_color='#10B981',
            text=[f"{v:,}" for v in after_values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>After: %{y:,}<extra></extra>'
        ))

        fig.update_layout(
            title='Metric Comparison: Before vs After',
            xaxis_title='Metrics',
            yaxis_title='Count',
            barmode='group',
            height=400,
            width=800,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    def create_column_distribution_comparison(
        self,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame,
        column: str
    ) -> go.Figure:
        """
        Create distribution comparison for a specific column

        Args:
            df_before: DataFrame before transformation
            df_after: DataFrame after transformation
            column: Column name to compare
        """

        if column not in df_before.columns or column not in df_after.columns:
            return None

        # Check if numeric or categorical
        if pd.api.types.is_numeric_dtype(df_before[column]):
            # Numeric - histogram
            fig = go.Figure()

            fig.add_trace(go.Histogram(
                x=df_before[column].dropna(),
                name='Before',
                marker_color='#EF4444',
                opacity=0.6,
                nbinsx=30
            ))

            fig.add_trace(go.Histogram(
                x=df_after[column].dropna(),
                name='After',
                marker_color='#10B981',
                opacity=0.6,
                nbinsx=30
            ))

            fig.update_layout(
                title=f'Distribution Comparison: {column}',
                xaxis_title=column,
                yaxis_title='Frequency',
                barmode='overlay',
                height=400,
                width=700,
                legend=dict(x=0.8, y=1)
            )

        else:
            # Categorical - bar chart
            before_counts = df_before[column].value_counts().head(10)
            after_counts = df_after[column].value_counts().head(10)

            # Combine categories
            all_categories = list(set(before_counts.index) | set(after_counts.index))

            fig = go.Figure()

            fig.add_trace(go.Bar(
                name='Before',
                x=all_categories,
                y=[before_counts.get(cat, 0) for cat in all_categories],
                marker_color='#EF4444'
            ))

            fig.add_trace(go.Bar(
                name='After',
                x=all_categories,
                y=[after_counts.get(cat, 0) for cat in all_categories],
                marker_color='#10B981'
            ))

            fig.update_layout(
                title=f'Value Distribution Comparison: {column}',
                xaxis_title=column,
                yaxis_title='Count',
                barmode='group',
                height=400,
                width=700
            )

        return fig

    def create_statistical_comparison_table(
        self,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame,
        columns: List[str] = None
    ) -> pd.DataFrame:
        """
        Create statistical comparison table for numeric columns

        Args:
            df_before: DataFrame before transformation
            df_after: DataFrame after transformation
            columns: Specific columns to compare (None = all numeric)
        """

        if columns is None:
            columns = df_before.select_dtypes(include=[np.number]).columns.tolist()

        comparison_data = []

        for col in columns:
            if col not in df_before.columns or col not in df_after.columns:
                continue

            if not pd.api.types.is_numeric_dtype(df_before[col]):
                continue

            before_stats = df_before[col].describe()
            after_stats = df_after[col].describe()

            comparison_data.append({
                'Column': col,
                'Metric': 'Mean',
                'Before': f"{before_stats['mean']:.2f}",
                'After': f"{after_stats['mean']:.2f}",
                'Change': f"{after_stats['mean'] - before_stats['mean']:+.2f}",
                'Change %': f"{((after_stats['mean'] - before_stats['mean']) / before_stats['mean'] * 100):+.1f}%" if before_stats['mean'] != 0 else "N/A"
            })

            comparison_data.append({
                'Column': col,
                'Metric': 'Median',
                'Before': f"{before_stats['50%']:.2f}",
                'After': f"{after_stats['50%']:.2f}",
                'Change': f"{after_stats['50%'] - before_stats['50%']:+.2f}",
                'Change %': f"{((after_stats['50%'] - before_stats['50%']) / before_stats['50%'] * 100):+.1f}%" if before_stats['50%'] != 0 else "N/A"
            })

            comparison_data.append({
                'Column': col,
                'Metric': 'Std Dev',
                'Before': f"{before_stats['std']:.2f}",
                'After': f"{after_stats['std']:.2f}",
                'Change': f"{after_stats['std'] - before_stats['std']:+.2f}",
                'Change %': f"{((after_stats['std'] - before_stats['std']) / before_stats['std'] * 100):+.1f}%" if before_stats['std'] != 0 else "N/A"
            })

        return pd.DataFrame(comparison_data)

    def create_impact_summary(
        self,
        df_before: pd.DataFrame,
        df_after: pd.DataFrame,
        transformation_description: str
    ) -> Dict[str, Any]:
        """
        Create impact summary of transformations

        Args:
            df_before: DataFrame before transformation
            df_after: DataFrame after transformation
            transformation_description: Description of what was transformed
        """

        summary = {
            'description': transformation_description,
            'rows_before': len(df_before),
            'rows_after': len(df_after),
            'cols_before': len(df_before.columns),
            'cols_after': len(df_after.columns),
            'changes': []
        }

        # Rows changed
        rows_changed = summary['rows_after'] - summary['rows_before']
        if rows_changed != 0:
            summary['changes'].append({
                'type': 'rows',
                'description': f"{'Added' if rows_changed > 0 else 'Removed'} {abs(rows_changed):,} rows",
                'impact': 'high' if abs(rows_changed) > len(df_before) * 0.1 else 'medium'
            })

        # Missing values changed
        missing_before = df_before.isnull().sum().sum()
        missing_after = df_after.isnull().sum().sum()
        missing_changed = missing_after - missing_before

        if missing_changed != 0:
            pct_change = (abs(missing_changed) / missing_before * 100) if missing_before > 0 else 0
            summary['changes'].append({
                'type': 'missing_values',
                'description': f"{'Filled' if missing_changed < 0 else 'Created'} {abs(missing_changed):,} missing values",
                'impact': 'high' if pct_change > 20 else 'medium' if pct_change > 5 else 'low'
            })

        # Duplicates changed
        dup_before = df_before.duplicated().sum()
        dup_after = df_after.duplicated().sum()
        dup_changed = dup_after - dup_before

        if dup_changed != 0:
            summary['changes'].append({
                'type': 'duplicates',
                'description': f"{'Removed' if dup_changed < 0 else 'Created'} {abs(dup_changed):,} duplicate rows",
                'impact': 'high' if abs(dup_changed) > 10 else 'medium'
            })

        # Column-level changes
        common_cols = set(df_before.columns) & set(df_after.columns)
        for col in common_cols:
            # Check if values changed
            if len(df_before) == len(df_after):
                try:
                    values_changed = (df_before[col] != df_after[col]).sum()
                    if values_changed > 0:
                        pct_changed = (values_changed / len(df_before)) * 100
                        summary['changes'].append({
                            'type': 'column_values',
                            'description': f"Modified {values_changed:,} values in '{col}' ({pct_changed:.1f}%)",
                            'impact': 'high' if pct_changed > 50 else 'medium' if pct_changed > 10 else 'low'
                        })
                except:
                    pass

        return summary


def display_transformation_comparison(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    transformation_info: Dict[str, Any],
    show_details: bool = True
):
    """
    Main function to display complete before/after comparison in Streamlit

    Args:
        df_before: DataFrame before transformation
        df_after: DataFrame after transformation
        transformation_info: Dictionary with transformation details
        show_details: Whether to show detailed comparisons
    """

    comparator = ComparisonView()

    st.header("🔄 Transformation Impact Analysis")

    # Transformation description
    if 'description' in transformation_info:
        st.info(f"**Transformation:** {transformation_info['description']}")

    st.divider()

    # Impact Summary
    st.subheader("📊 Impact Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        rows_delta = len(df_after) - len(df_before)
        st.metric(
            "Rows",
            f"{len(df_after):,}",
            delta=f"{rows_delta:+,}" if rows_delta != 0 else "No change"
        )

    with col2:
        missing_before = df_before.isnull().sum().sum()
        missing_after = df_after.isnull().sum().sum()
        st.metric(
            "Missing Values",
            f"{missing_after:,}",
            delta=f"{missing_after - missing_before:+,}",
            delta_color="inverse"
        )

    with col3:
        dup_before = df_before.duplicated().sum()
        dup_after = df_after.duplicated().sum()
        st.metric(
            "Duplicates",
            f"{dup_after:,}",
            delta=f"{dup_after - dup_before:+,}",
            delta_color="inverse"
        )

    with col4:
        # Calculate overall improvement score
        improvement = 0
        if missing_before > 0:
            improvement += ((missing_before - missing_after) / missing_before) * 50
        if dup_before > 0:
            improvement += ((dup_before - dup_after) / dup_before) * 50

        st.metric(
            "Improvement",
            f"{max(0, min(100, improvement)):.0f}%",
            delta="Quality increased" if improvement > 0 else "No change"
        )

    st.divider()

    # Detailed comparison tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Data Preview",
        "📊 Metrics Comparison",
        "📈 Distribution Changes",
        "📉 Statistical Summary"
    ])

    with tab1:
        st.subheader("Side-by-Side Data Preview")

        # Column selector
        if show_details:
            selected_cols = st.multiselect(
                "Select columns to compare",
                options=list(df_before.columns),
                default=list(df_before.columns)[:5]
            )
        else:
            selected_cols = list(df_before.columns)[:5]

        if selected_cols:
            comparator.create_side_by_side_preview(
                df_before,
                df_after,
                columns=selected_cols,
                max_rows=15
            )

    with tab2:
        st.subheader("Key Metrics Before vs After")

        delta_fig = comparator.create_delta_metrics(df_before, df_after)
        st.plotly_chart(delta_fig, use_container_width=True)

    with tab3:
        st.subheader("Distribution Changes by Column")

        # Select column for distribution comparison
        numeric_cols = df_before.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df_before.select_dtypes(exclude=[np.number]).columns.tolist()

        all_cols = numeric_cols + categorical_cols[:5]  # Limit categorical

        if all_cols:
            selected_col = st.selectbox(
                "Select column to compare",
                options=all_cols
            )

            if selected_col:
                dist_fig = comparator.create_column_distribution_comparison(
                    df_before,
                    df_after,
                    selected_col
                )
                if dist_fig:
                    st.plotly_chart(dist_fig, use_container_width=True)

    with tab4:
        st.subheader("Statistical Comparison")

        # Show statistical comparison for numeric columns
        numeric_cols = df_before.select_dtypes(include=[np.number]).columns.tolist()[:5]

        if numeric_cols:
            stats_df = comparator.create_statistical_comparison_table(
                df_before,
                df_after,
                columns=numeric_cols
            )

            # Style the dataframe
            def highlight_changes(row):
                styles = [''] * len(row)
                if 'Change %' in row.index:
                    try:
                        change_str = row['Change %']
                        if change_str != 'N/A':
                            change_val = float(change_str.replace('%', '').replace('+', ''))
                            if abs(change_val) > 10:
                                styles[-1] = 'background-color: #FEE2E2'  # Red for large change
                            elif abs(change_val) > 5:
                                styles[-1] = 'background-color: #FEF3C7'  # Yellow for medium
                    except:
                        pass
                return styles

            styled_stats = stats_df.style.apply(highlight_changes, axis=1)
            st.dataframe(styled_stats, use_container_width=True, height=400)
        else:
            st.info("No numeric columns to compare")

    st.divider()

    # Detailed impact analysis
    with st.expander("🔍 Detailed Impact Analysis", expanded=False):
        impact = comparator.create_impact_summary(
            df_before,
            df_after,
            transformation_info.get('description', 'Transformation applied')
        )

        if impact['changes']:
            for change in impact['changes']:
                impact_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(change['impact'], '⚪')

                st.markdown(f"{impact_emoji} **{change['type'].replace('_', ' ').title()}**: {change['description']}")
        else:
            st.success("✅ No significant changes detected")
