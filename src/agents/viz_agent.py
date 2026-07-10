from typing import Dict, Any, List
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from src.agents.base_agent import BaseAgent
from src.data.dataset_handle import DatasetHandle
from src.utils.types import AgentResponse
from src.utils.helpers import generate_id


class VisualizationAgent(BaseAgent):
    """
    Agent responsible for generating data visualizations.
    Creates distribution plots, correlation heatmaps, scatter plots, and box plots.
    """

    def __init__(self):
        super().__init__()
        self.artifacts_dir = Path("data/artifacts/plots")
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def get_agent_name(self) -> str:
        return "VisualizationAgent"

    def analyze(self, dataset_handle: DatasetHandle, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Generate visualizations and provide explainable insights

        Returns structured analysis with plot paths and interpretations
        """
        # Generate visualizations
        viz_results = self._generate_visualizations(dataset_handle, context)

        # Create context for LLM
        analysis_context = self._prepare_context(viz_results, context)

        # Get LLM interpretation with explainability
        llm_response = self._get_llm_interpretation(analysis_context)

        # Construct AgentResponse
        return AgentResponse(
            result=viz_results,
            reasoning=llm_response["reasoning"],
            impact=llm_response["impact"],
            recommendations=llm_response["recommendations"],
            confidence=llm_response["confidence"]
        )

    def _generate_visualizations(self, dataset_handle: DatasetHandle, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive visualizations"""

        # Get sample data
        sample_size = min(10000, dataset_handle.shape[0])
        df_sample = dataset_handle.sample(sample_size)

        viz_id = generate_id("viz")
        generated_plots = []

        # Get profile info for context
        profile = context.get('profile_results') if context else None
        quality = context.get('quality_results') if context else None

        # 1. Distribution plots for numeric columns
        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 0:
            dist_plots = self._create_distribution_plots(df_sample, numeric_cols, viz_id)
            generated_plots.extend(dist_plots)

        # 2. Correlation heatmap
        if len(numeric_cols) > 1:
            corr_plot = self._create_correlation_heatmap(df_sample, numeric_cols, viz_id)
            if corr_plot:
                generated_plots.append(corr_plot)

        # 3. Box plots for outlier detection
        if quality and quality.get('outliers', {}).get('has_outliers'):
            outlier_cols = list(quality['outliers']['outlier_details'].keys())[:5]
            box_plots = self._create_box_plots(df_sample, outlier_cols, viz_id)
            generated_plots.extend(box_plots)

        # 4. Categorical distribution plots
        categorical_cols = df_sample.select_dtypes(include=['object']).columns.tolist()
        if len(categorical_cols) > 0:
            cat_plots = self._create_categorical_plots(df_sample, categorical_cols, viz_id)
            generated_plots.extend(cat_plots)

        # 5. Missing value heatmap
        if profile and any(v['percentage'] > 0 for v in profile.get('missing_info', {}).values()):
            missing_plot = self._create_missing_heatmap(df_sample, viz_id)
            if missing_plot:
                generated_plots.append(missing_plot)

        return {
            "visualization_id": viz_id,
            "total_plots": len(generated_plots),
            "sample_size": len(df_sample),
            "plots": generated_plots,
            "summary": self._generate_summary(generated_plots)
        }

    def _create_distribution_plots(self, df: pd.DataFrame, numeric_cols: List[str], viz_id: str) -> List[Dict[str, Any]]:
        """Create distribution plots for numeric columns"""
        plots = []

        # Limit to top 6 numeric columns
        for col in numeric_cols[:6]:
            try:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

                # Histogram
                df[col].dropna().hist(bins=30, ax=ax1, edgecolor='black', alpha=0.7)
                ax1.set_title(f'Distribution: {col}')
                ax1.set_xlabel(col)
                ax1.set_ylabel('Frequency')
                ax1.grid(alpha=0.3)

                # Box plot
                df[col].dropna().plot(kind='box', ax=ax2, vert=True)
                ax2.set_title(f'Box Plot: {col}')
                ax2.set_ylabel(col)
                ax2.grid(alpha=0.3)

                plt.tight_layout()

                # Save plot
                plot_path = self.artifacts_dir / f"{viz_id}_dist_{col}.png"
                plt.savefig(plot_path, dpi=100, bbox_inches='tight')
                plt.close()

                # Calculate statistics
                stats = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "skewness": float(df[col].skew())
                }

                plots.append({
                    "type": "distribution",
                    "column": col,
                    "path": str(plot_path),
                    "statistics": stats,
                    "interpretation": self._interpret_distribution(stats)
                })

            except Exception as e:
                print(f"Warning: Failed to create distribution plot for {col}: {str(e)}")
                continue

        return plots

    def _interpret_distribution(self, stats: Dict[str, float]) -> str:
        """Interpret distribution statistics"""
        skew = stats['skewness']
        if abs(skew) < 0.5:
            return "Approximately symmetric distribution"
        elif skew > 0.5:
            return "Right-skewed (positive skew) - tail extends to higher values"
        else:
            return "Left-skewed (negative skew) - tail extends to lower values"

    def _create_correlation_heatmap(self, df: pd.DataFrame, numeric_cols: List[str], viz_id: str) -> Dict[str, Any]:
        """Create correlation heatmap"""
        try:
            # Calculate correlation matrix
            corr_matrix = df[numeric_cols].corr()

            # Create heatmap
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                corr_matrix,
                annot=True,
                fmt='.2f',
                cmap='coolwarm',
                center=0,
                square=True,
                linewidths=1,
                cbar_kws={"shrink": 0.8}
            )
            plt.title('Correlation Heatmap', fontsize=14, fontweight='bold')
            plt.tight_layout()

            # Save plot
            plot_path = self.artifacts_dir / f"{viz_id}_correlation_heatmap.png"
            plt.savefig(plot_path, dpi=100, bbox_inches='tight')
            plt.close()

            # Find strong correlations
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        strong_correlations.append({
                            "var1": corr_matrix.columns[i],
                            "var2": corr_matrix.columns[j],
                            "correlation": float(corr_val)
                        })

            return {
                "type": "correlation_heatmap",
                "path": str(plot_path),
                "num_variables": len(numeric_cols),
                "strong_correlations": strong_correlations,
                "interpretation": f"Found {len(strong_correlations)} pairs with |correlation| > 0.7"
            }

        except Exception as e:
            print(f"Warning: Failed to create correlation heatmap: {str(e)}")
            return None

    def _create_box_plots(self, df: pd.DataFrame, outlier_cols: List[str], viz_id: str) -> List[Dict[str, Any]]:
        """Create box plots for columns with outliers"""
        plots = []

        for col in outlier_cols[:4]:  # Top 4
            try:
                plt.figure(figsize=(10, 6))
                df[col].dropna().plot(kind='box', vert=False)
                plt.title(f'Box Plot: {col} (Outlier Detection)', fontsize=12, fontweight='bold')
                plt.xlabel(col)
                plt.grid(alpha=0.3)
                plt.tight_layout()

                # Save plot
                plot_path = self.artifacts_dir / f"{viz_id}_boxplot_{col}.png"
                plt.savefig(plot_path, dpi=100, bbox_inches='tight')
                plt.close()

                # Calculate quartiles
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1

                plots.append({
                    "type": "box_plot",
                    "column": col,
                    "path": str(plot_path),
                    "quartiles": {
                        "Q1": float(Q1),
                        "Q3": float(Q3),
                        "IQR": float(IQR)
                    }
                })

            except Exception as e:
                print(f"Warning: Failed to create box plot for {col}: {str(e)}")
                continue

        return plots

    def _create_categorical_plots(self, df: pd.DataFrame, categorical_cols: List[str], viz_id: str) -> List[Dict[str, Any]]:
        """Create bar plots for categorical columns"""
        plots = []

        for col in categorical_cols[:4]:  # Top 4
            try:
                # Get value counts
                value_counts = df[col].value_counts().head(10)  # Top 10 categories

                if len(value_counts) == 0:
                    continue

                # Create bar plot
                plt.figure(figsize=(10, 6))
                value_counts.plot(kind='bar', color='steelblue', edgecolor='black', alpha=0.7)
                plt.title(f'Top Categories: {col}', fontsize=12, fontweight='bold')
                plt.xlabel(col)
                plt.ylabel('Count')
                plt.xticks(rotation=45, ha='right')
                plt.grid(axis='y', alpha=0.3)
                plt.tight_layout()

                # Save plot
                plot_path = self.artifacts_dir / f"{viz_id}_categorical_{col}.png"
                plt.savefig(plot_path, dpi=100, bbox_inches='tight')
                plt.close()

                plots.append({
                    "type": "categorical_bar",
                    "column": col,
                    "path": str(plot_path),
                    "num_categories": len(df[col].unique()),
                    "top_category": str(value_counts.index[0]),
                    "top_count": int(value_counts.values[0])
                })

            except Exception as e:
                print(f"Warning: Failed to create categorical plot for {col}: {str(e)}")
                continue

        return plots

    def _create_missing_heatmap(self, df: pd.DataFrame, viz_id: str) -> Dict[str, Any]:
        """Create heatmap showing missing value patterns"""
        try:
            # Create missing data indicator
            missing_data = df.isnull()

            # Only include columns with missing values
            cols_with_missing = [col for col in missing_data.columns if missing_data[col].any()]

            if len(cols_with_missing) == 0:
                return None

            # Sample rows if too many
            if len(df) > 100:
                sample_indices = np.random.choice(len(df), min(100, len(df)), replace=False)
                missing_data = missing_data.iloc[sample_indices]

            # Create heatmap
            plt.figure(figsize=(12, 8))
            sns.heatmap(
                missing_data[cols_with_missing].T,
                cmap='RdYlGn_r',
                cbar_kws={'label': 'Missing'},
                yticklabels=cols_with_missing
            )
            plt.title('Missing Value Patterns', fontsize=14, fontweight='bold')
            plt.xlabel('Sample Rows')
            plt.ylabel('Columns')
            plt.tight_layout()

            # Save plot
            plot_path = self.artifacts_dir / f"{viz_id}_missing_heatmap.png"
            plt.savefig(plot_path, dpi=100, bbox_inches='tight')
            plt.close()

            return {
                "type": "missing_heatmap",
                "path": str(plot_path),
                "columns_with_missing": len(cols_with_missing),
                "interpretation": f"Visualizing missing patterns across {len(cols_with_missing)} columns"
            }

        except Exception as e:
            print(f"Warning: Failed to create missing heatmap: {str(e)}")
            return None

    def _generate_summary(self, plots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of visualizations"""
        plot_types = {}
        for plot in plots:
            plot_type = plot['type']
            plot_types[plot_type] = plot_types.get(plot_type, 0) + 1

        return {
            "by_type": plot_types,
            "total_plots": len(plots)
        }

    def _prepare_context(self, viz_results: Dict[str, Any], prior_context: Dict[str, Any]) -> str:
        """Prepare context string for LLM"""

        context = f"""
Visualization Analysis Results:

Total Plots Generated: {viz_results['total_plots']}
Sample Size: {viz_results['sample_size']:,} rows

Plot Summary:
"""

        for plot_type, count in viz_results['summary']['by_type'].items():
            context += f"- {plot_type.replace('_', ' ').title()}: {count} plots\n"

        context += "\n\nKey Findings:\n"

        # Add insights from plots
        for plot in viz_results['plots'][:10]:  # First 10
            if plot['type'] == 'distribution':
                context += f"\n- {plot['column']}: {plot['interpretation']}"
                context += f" (mean={plot['statistics']['mean']:.2f}, std={plot['statistics']['std']:.2f})"

            elif plot['type'] == 'correlation_heatmap':
                if plot['strong_correlations']:
                    context += f"\n- Strong correlations found:"
                    for corr in plot['strong_correlations'][:3]:
                        context += f"\n  * {corr['var1']} ↔ {corr['var2']}: {corr['correlation']:.2f}"

            elif plot['type'] == 'categorical_bar':
                context += f"\n- {plot['column']}: {plot['num_categories']} categories, most common is '{plot['top_category']}' ({plot['top_count']} occurrences)"

        return context

    def _get_llm_interpretation(self, analysis_context: str) -> Dict[str, Any]:
        """Get LLM interpretation with explainability"""

        system_message = """You are a data visualization expert analyzing generated plots and charts.
Your job is to interpret the visualizations and provide actionable insights.

You must respond in JSON format with these fields:
{{
    "reasoning": "Explain WHY these visualizations were generated and WHAT patterns they reveal",
    "impact": "Explain WHAT these visual insights mean for understanding the dataset",
    "recommendations": ["List of 3-5 specific actions based on the visualizations"],
    "confidence": 0.95
}}

Focus on:
1. Key patterns visible in the plots
2. Distribution characteristics (symmetry, skewness, outliers)
3. Relationships between variables (correlations)
4. Data quality issues visible in plots
5. Next steps for deeper analysis

Be specific and reference actual findings from the visualizations."""

        user_message = f"""Analyze these visualization results and provide insights:

{analysis_context}

Provide your analysis in the specified JSON format."""

        prompt = self.create_structured_prompt(system_message, user_message)
        chain = prompt | self.llm

        response = chain.invoke({})

        # Parse response
        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            parsed = json.loads(content)

            return {
                "reasoning": parsed.get("reasoning", "Visualizations generated to reveal data patterns"),
                "impact": parsed.get("impact", "Visual insights help understand data structure"),
                "recommendations": parsed.get("recommendations", ["Review distribution plots", "Check correlations"]),
                "confidence": parsed.get("confidence", 0.85)
            }
        except Exception as e:
            # Fallback response
            return {
                "reasoning": "Generated comprehensive visualizations including distributions, correlations, and categorical analyses to reveal data patterns",
                "impact": "Visual analysis reveals distribution shapes, relationships between variables, and data quality issues that numbers alone don't show",
                "recommendations": [
                    "Review distribution plots for skewness and outliers",
                    "Examine correlation heatmap for multicollinearity",
                    "Check categorical plots for imbalanced classes",
                    "Investigate any unusual patterns in missing data",
                    "Use visualizations to guide feature engineering decisions"
                ],
                "confidence": 0.80
            }
