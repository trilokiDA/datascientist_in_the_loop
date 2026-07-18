"""
Quality Visualization Component
Creates interactive visualizations for data quality issues
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


class QualityVisualizer:
    """Generates visualizations for data quality analysis"""

    def __init__(self):
        self.artifacts_dir = Path("data/artifacts/quality_viz")
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def create_missing_value_heatmap(
        self,
        df: pd.DataFrame,
        missing_info: Dict[str, Any]
    ) -> go.Figure:
        """Create interactive heatmap showing missing value patterns"""

        # Get columns with missing values
        cols_with_missing = [
            col for col, info in missing_info.items()
            if info['percentage'] > 0
        ]

        if not cols_with_missing:
            return None

        # Limit to top 20 columns with most missing values
        sorted_cols = sorted(
            cols_with_missing,
            key=lambda x: missing_info[x]['percentage'],
            reverse=True
        )[:20]

        # Sample data for visualization (max 1000 rows for performance)
        sample_size = min(1000, len(df))
        df_sample = df[sorted_cols].head(sample_size)

        # Create binary matrix: 1 = missing, 0 = present
        missing_matrix = df_sample.isnull().astype(int)

        fig = go.Figure(data=go.Heatmap(
            z=missing_matrix.T.values,
            x=list(range(len(missing_matrix))),
            y=sorted_cols,
            colorscale=[[0, '#10B981'], [1, '#EF4444']],  # Green to Red
            showscale=True,
            colorbar=dict(
                title="Missing",
                ticktext=["Present", "Missing"],
                tickvals=[0, 1]
            ),
            hovertemplate='Row: %{x}<br>Column: %{y}<br>Status: %{z}<extra></extra>'
        ))

        fig.update_layout(
            title="Missing Value Pattern Heatmap",
            xaxis_title=f"Row Index (showing first {sample_size} rows)",
            yaxis_title="Columns",
            height=max(400, len(sorted_cols) * 25),
            width=800,
            font=dict(size=10)
        )

        return fig

    def create_missing_value_bar_chart(
        self,
        missing_info: Dict[str, Any]
    ) -> go.Figure:
        """Create bar chart of missing value percentages"""

        # Get columns with missing values
        missing_data = [
            {
                'column': col,
                'percentage': info['percentage'],
                'count': info['count']
            }
            for col, info in missing_info.items()
            if info['percentage'] > 0
        ]

        if not missing_data:
            return None

        # Sort by percentage
        missing_data.sort(key=lambda x: x['percentage'], reverse=True)

        # Limit to top 20
        missing_data = missing_data[:20]

        # Create color scale based on severity
        colors = [
            '#EF4444' if d['percentage'] > 40 else  # Red for high
            '#F59E0B' if d['percentage'] > 20 else  # Orange for medium
            '#10B981'  # Green for low
            for d in missing_data
        ]

        fig = go.Figure(data=[
            go.Bar(
                x=[d['percentage'] for d in missing_data],
                y=[d['column'] for d in missing_data],
                orientation='h',
                marker=dict(color=colors),
                text=[f"{d['percentage']:.1f}%" for d in missing_data],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Missing: %{x:.1f}%<br>Count: %{customdata}<extra></extra>',
                customdata=[d['count'] for d in missing_data]
            )
        ])

        fig.update_layout(
            title="Missing Values by Column",
            xaxis_title="Missing Percentage (%)",
            yaxis_title="Column",
            height=max(400, len(missing_data) * 30),
            width=700,
            showlegend=False
        )

        return fig

    def create_outlier_box_plots(
        self,
        df: pd.DataFrame,
        outlier_details: Dict[str, Any]
    ) -> go.Figure:
        """Create box plots showing outlier distributions"""

        if not outlier_details:
            return None

        # Get top 6 columns with outliers
        cols_with_outliers = list(outlier_details.keys())[:6]

        # Create subplots
        n_cols = min(2, len(cols_with_outliers))
        n_rows = (len(cols_with_outliers) + 1) // 2

        fig = make_subplots(
            rows=n_rows,
            cols=n_cols,
            subplot_titles=cols_with_outliers,
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )

        for idx, col in enumerate(cols_with_outliers):
            row = (idx // n_cols) + 1
            col_pos = (idx % n_cols) + 1

            # Get data
            data = df[col].dropna()

            fig.add_trace(
                go.Box(
                    y=data,
                    name=col,
                    marker_color='#3B82F6',
                    boxmean='sd',  # Show mean and std dev
                    hovertemplate='<b>%{y}</b><extra></extra>'
                ),
                row=row,
                col=col_pos
            )

        fig.update_layout(
            title="Outlier Distribution (Box Plots)",
            height=n_rows * 300,
            width=800,
            showlegend=False
        )

        return fig

    def create_outlier_scatter_plot(
        self,
        df: pd.DataFrame,
        outlier_details: Dict[str, Any]
    ) -> Optional[go.Figure]:
        """Create scatter plot highlighting outliers using z-scores"""

        if not outlier_details or len(outlier_details) < 2:
            return None

        # Get top 2 columns with outliers
        cols = list(outlier_details.keys())[:2]

        # Calculate z-scores
        df_subset = df[cols].dropna()
        z_scores = np.abs((df_subset - df_subset.mean()) / df_subset.std())

        # Mark outliers (z-score > 3)
        is_outlier = (z_scores > 3).any(axis=1)

        fig = go.Figure()

        # Plot normal points
        fig.add_trace(go.Scatter(
            x=df_subset[~is_outlier][cols[0]],
            y=df_subset[~is_outlier][cols[1]],
            mode='markers',
            name='Normal',
            marker=dict(color='#10B981', size=6, opacity=0.6),
            hovertemplate=f'<b>{cols[0]}</b>: %{{x}}<br><b>{cols[1]}</b>: %{{y}}<extra></extra>'
        ))

        # Plot outliers
        fig.add_trace(go.Scatter(
            x=df_subset[is_outlier][cols[0]],
            y=df_subset[is_outlier][cols[1]],
            mode='markers',
            name='Outliers',
            marker=dict(color='#EF4444', size=10, symbol='x'),
            hovertemplate=f'<b>{cols[0]}</b>: %{{x}}<br><b>{cols[1]}</b>: %{{y}}<extra></extra>'
        ))

        fig.update_layout(
            title=f"Outlier Detection: {cols[0]} vs {cols[1]}",
            xaxis_title=cols[0],
            yaxis_title=cols[1],
            height=500,
            width=700,
            hovermode='closest'
        )

        return fig

    def create_duplicate_visualization(
        self,
        duplicate_info: Dict[str, Any]
    ) -> Optional[go.Figure]:
        """Create visualization for duplicate analysis"""

        if not duplicate_info.get('has_duplicates'):
            return None

        # Create gauge chart for duplicate percentage
        duplicate_pct = duplicate_info['duplicate_percentage']

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=duplicate_pct,
            title={'text': "Duplicate Rows"},
            delta={'reference': 5, 'suffix': '%'},  # Reference threshold
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 5], 'color': "#D1FAE5"},     # Light green
                    {'range': [5, 15], 'color': "#FEF3C7"},    # Light yellow
                    {'range': [15, 100], 'color': "#FEE2E2"}   # Light red
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 10
                }
            },
            number={'suffix': '%'}
        ))

        fig.update_layout(
            height=300,
            width=400,
            title="Duplicate Row Percentage"
        )

        return fig

    def create_data_type_consistency_chart(
        self,
        data_type_issues: Dict[str, Any]
    ) -> Optional[go.Figure]:
        """Create chart showing data type consistency issues"""

        if not data_type_issues or not data_type_issues.get('issues'):
            return None

        issues = data_type_issues['issues']

        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=[issue['column'] for issue in issues],
                y=[issue['inconsistent_count'] for issue in issues],
                marker=dict(
                    color=[issue['severity_score'] for issue in issues],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Severity")
                ),
                text=[f"{issue['inconsistent_percentage']:.1f}%" for issue in issues],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Inconsistent: %{y}<br>Percentage: %{text}<extra></extra>'
            )
        ])

        fig.update_layout(
            title="Data Type Consistency Issues",
            xaxis_title="Column",
            yaxis_title="Inconsistent Values",
            height=400,
            width=700
        )

        return fig

    def create_value_range_chart(
        self,
        value_ranges: Dict[str, Any]
    ) -> Optional[go.Figure]:
        """Create chart showing value ranges and potential issues"""

        if not value_ranges:
            return None

        # Get numeric columns with range info
        range_data = []
        for col, info in value_ranges.items():
            if 'min' in info and 'max' in info:
                range_data.append({
                    'column': col,
                    'min': info['min'],
                    'max': info['max'],
                    'range': info['max'] - info['min']
                })

        if not range_data:
            return None

        # Limit to top 10 by range
        range_data.sort(key=lambda x: x['range'], reverse=True)
        range_data = range_data[:10]

        fig = go.Figure()

        # Add range bars
        for item in range_data:
            fig.add_trace(go.Bar(
                name=item['column'],
                x=[item['column']],
                y=[item['range']],
                text=[f"Min: {item['min']:.2f}<br>Max: {item['max']:.2f}"],
                hovertemplate='<b>%{x}</b><br>Range: %{y:.2f}<br>%{text}<extra></extra>'
            ))

        fig.update_layout(
            title="Value Ranges by Column",
            xaxis_title="Column",
            yaxis_title="Range (Max - Min)",
            height=400,
            width=700,
            showlegend=False
        )

        return fig

    def create_quality_summary_dashboard(
        self,
        quality_results: Dict[str, Any]
    ) -> go.Figure:
        """Create comprehensive quality summary dashboard"""

        # Extract metrics
        duplicates = quality_results.get('duplicates', {})
        outliers = quality_results.get('outliers', {})
        inconsistencies = quality_results.get('inconsistencies', {})

        # Create subplots without subplot_titles to avoid overlap
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{'type': 'indicator'}, {'type': 'indicator'}],
                [{'type': 'indicator'}, {'type': 'indicator'}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )

        # Duplicate indicator
        dup_pct = duplicates.get('duplicate_percentage', 0)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=dup_pct,
                title={'text': "Duplicates (%)", 'font': {'size': 16}},
                gauge={
                    'axis': {'range': [None, 20]},
                    'bar': {'color': "#3B82F6"},
                    'steps': [
                        {'range': [0, 5], 'color': "#D1FAE5"},
                        {'range': [5, 10], 'color': "#FEF3C7"},
                        {'range': [10, 20], 'color': "#FEE2E2"}
                    ]
                },
                domain={'x': [0, 1], 'y': [0, 1]},
                number={'suffix': '%', 'font': {'size': 24}}
            ),
            row=1, col=1
        )

        # Outlier indicator
        outlier_cols = len(outliers.get('outlier_details', {}))
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=outlier_cols,
                title={'text': "Outlier Columns", 'font': {'size': 16}},
                delta={'reference': 0},
                domain={'x': [0, 1], 'y': [0, 1]},
                number={'font': {'size': 32, 'color': "#F59E0B" if outlier_cols > 5 else "#10B981"}}
            ),
            row=1, col=2
        )

        # Data type issues
        type_issues = len(inconsistencies.get('type_mismatches', []))
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=type_issues,
                title={'text': "Type Issues", 'font': {'size': 16}},
                domain={'x': [0, 1], 'y': [0, 1]},
                number={'font': {'size': 32, 'color': "#EF4444" if type_issues > 0 else "#10B981"}}
            ),
            row=2, col=1
        )

        # Overall quality score (calculated)
        quality_score = self._calculate_quality_score(quality_results)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=quality_score,
                title={'text': "Quality Score", 'font': {'size': 16}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "#FEE2E2"},
                        {'range': [50, 80], 'color': "#FEF3C7"},
                        {'range': [80, 100], 'color': "#D1FAE5"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 80
                    }
                },
                domain={'x': [0, 1], 'y': [0, 1]},
                number={'suffix': '/100', 'font': {'size': 24}}
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=500,
            width=800,
            title_text="Data Quality Summary",
            title_font_size=20,
            showlegend=False
        )

        return fig

    def _calculate_quality_score(self, quality_results: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)"""

        score = 100.0

        # Penalize for duplicates
        dup_pct = quality_results.get('duplicates', {}).get('duplicate_percentage', 0)
        score -= min(dup_pct * 2, 20)  # Max 20 point penalty

        # Penalize for outliers
        outlier_count = len(quality_results.get('outliers', {}).get('outlier_details', {}))
        score -= min(outlier_count * 3, 30)  # Max 30 point penalty

        # Penalize for inconsistencies
        inconsistency_count = len(quality_results.get('inconsistencies', {}).get('type_mismatches', []))
        score -= min(inconsistency_count * 5, 25)  # Max 25 point penalty

        return max(0.0, score)


def display_quality_visualizations(quality_results: Dict[str, Any], dataset_handle):
    """
    Main function to display all quality visualizations in Streamlit

    Args:
        quality_results: Results from QualityAgent
        dataset_handle: DatasetHandle instance for accessing data
    """

    visualizer = QualityVisualizer()

    # Get sample data
    sample_size = min(10000, dataset_handle.shape[0])
    df_sample = dataset_handle.sample(sample_size)

    st.header("📊 Quality Visualizations")

    # Quality Summary Dashboard
    st.subheader("Overall Quality Dashboard")
    dashboard_fig = visualizer.create_quality_summary_dashboard(quality_results['result'])
    st.plotly_chart(dashboard_fig, use_container_width=True)

    st.divider()

    # Missing Values Section
    st.subheader("🔍 Missing Values Analysis")

    # Calculate missing info from the sample data
    missing_info = {}
    for col in df_sample.columns:
        missing_count = df_sample[col].isnull().sum()
        if missing_count > 0:
            missing_info[col] = {
                'count': int(missing_count),
                'percentage': float(missing_count / len(df_sample) * 100)
            }

    if missing_info:
        col1, col2 = st.columns(2)

        with col1:
            # Missing value bar chart
            bar_fig = visualizer.create_missing_value_bar_chart(missing_info)
            if bar_fig:
                st.plotly_chart(bar_fig, use_container_width=True)

        with col2:
            # Missing value heatmap
            heatmap_fig = visualizer.create_missing_value_heatmap(df_sample, missing_info)
            if heatmap_fig:
                st.plotly_chart(heatmap_fig, use_container_width=True)
    else:
        st.success("✅ No missing values detected!")

    st.divider()

    # Outliers Section
    st.subheader("⚠️ Outlier Analysis")

    outliers = quality_results['result'].get('outliers', {})
    outlier_details = outliers.get('outlier_details', {})

    if outlier_details:
        col1, col2 = st.columns(2)

        with col1:
            # Box plots
            box_fig = visualizer.create_outlier_box_plots(df_sample, outlier_details)
            if box_fig:
                st.plotly_chart(box_fig, use_container_width=True)

        with col2:
            # Scatter plot
            scatter_fig = visualizer.create_outlier_scatter_plot(df_sample, outlier_details)
            if scatter_fig:
                st.plotly_chart(scatter_fig, use_container_width=True)
    else:
        st.success("✅ No significant outliers detected!")

    st.divider()

    # Duplicates Section
    st.subheader("🔄 Duplicate Analysis")

    duplicates = quality_results['result'].get('duplicates', {})
    dup_fig = visualizer.create_duplicate_visualization(duplicates)
    if dup_fig:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.plotly_chart(dup_fig, use_container_width=True)

        # Show details
        if duplicates.get('has_duplicates'):
            st.warning(f"⚠️ Found {duplicates['duplicate_rows']:,} duplicate rows "
                      f"({duplicates['duplicate_percentage']:.2f}% of sample)")
    else:
        st.success("✅ No duplicate rows detected!")

    st.divider()

    # Data Type Consistency
    st.subheader("🔤 Data Type Consistency")

    data_types = quality_results['result'].get('data_types', {})
    type_fig = visualizer.create_data_type_consistency_chart(data_types)
    if type_fig:
        st.plotly_chart(type_fig, use_container_width=True)
    else:
        st.success("✅ All data types are consistent!")
