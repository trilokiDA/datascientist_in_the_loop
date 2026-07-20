"""
Export utilities for generating reports in various formats
Supports: HTML, PDF, JSON, CSV
"""

import json
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


class ExportManager:
    """Manages export functionality for analysis results"""

    def __init__(self, output_dir: str = "data/exports"):
        """
        Initialize ExportManager

        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_get(data: Dict[str, Any], *keys: str, default: Any = "N/A") -> Any:
        """
        Safely access nested dictionary keys

        Args:
            data: Dictionary to access
            *keys: Keys to traverse
            default: Default value if key not found

        Returns:
            Value at nested key or default
        """
        try:
            result = data
            for key in keys:
                result = result[key]
            return result if result is not None else default
        except (KeyError, TypeError, IndexError):
            return default

    def export_all(
        self,
        analysis_results: Dict[str, Any],
        dataset_info: Dict[str, Any],
        formats: List[str] = ['html', 'json'],
        session_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Export analysis results in multiple formats

        Args:
            analysis_results: Dictionary of agent results
            dataset_info: Dataset metadata
            formats: List of formats to export ('html', 'json', 'csv')
            session_id: Optional session identifier

        Returns:
            Dictionary mapping format to file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_prefix = f"{session_id}_" if session_id else ""

        exported_files = {}

        if 'html' in formats:
            html_path = self.export_html(
                analysis_results,
                dataset_info,
                f"{session_prefix}report_{timestamp}.html"
            )
            exported_files['html'] = html_path

        if 'json' in formats:
            json_path = self.export_json(
                analysis_results,
                dataset_info,
                f"{session_prefix}results_{timestamp}.json"
            )
            exported_files['json'] = json_path

        if 'csv' in formats and 'transform' in analysis_results:
            csv_path = self.export_transformed_csv(
                analysis_results.get('transform'),
                f"{session_prefix}transformed_{timestamp}.csv"
            )
            if csv_path:
                exported_files['csv'] = csv_path

        return exported_files

    def export_html(
        self,
        analysis_results: Dict[str, Any],
        dataset_info: Dict[str, Any],
        filename: str
    ) -> str:
        """
        Generate comprehensive HTML report with interactive Plotly charts

        Args:
            analysis_results: Dictionary of agent results
            dataset_info: Dataset metadata
            filename: Output filename

        Returns:
            Path to generated HTML file
        """
        output_path = self.output_dir / filename

        html_content = self._generate_html_report(analysis_results, dataset_info)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_path)

    def export_json(
        self,
        analysis_results: Dict[str, Any],
        dataset_info: Dict[str, Any],
        filename: str
    ) -> str:
        """
        Export analysis results as JSON

        Args:
            analysis_results: Dictionary of agent results
            dataset_info: Dataset metadata
            filename: Output filename

        Returns:
            Path to generated JSON file
        """
        output_path = self.output_dir / filename

        export_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'dataset_info': dataset_info
            },
            'analysis_results': analysis_results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)

        return str(output_path)

    def export_transformed_csv(
        self,
        transform_result: Dict[str, Any],
        filename: str
    ) -> Optional[str]:
        """
        Export transformed dataset as CSV

        Args:
            transform_result: TransformAgent result containing transformed data
            filename: Output filename

        Returns:
            Path to generated CSV file or None if no transformed data
        """
        if not transform_result or 'result' not in transform_result:
            return None

        # Check if there's a transformed dataframe saved
        result = transform_result['result']
        if 'transformed_data_path' in result:
            # Copy the transformed data to exports
            import shutil
            source_path = Path(result['transformed_data_path'])
            if source_path.exists():
                output_path = self.output_dir / filename
                # Copy the file if it's not already in exports directory
                if str(source_path.resolve()) != str(output_path.resolve()):
                    shutil.copy(source_path, output_path)
                    return str(output_path)
                else:
                    # File is already in exports directory
                    return str(source_path)

        return None

    def _generate_html_report(
        self,
        analysis_results: Dict[str, Any],
        dataset_info: Dict[str, Any]
    ) -> str:
        """Generate HTML report content"""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDA Analysis Report</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        {self._get_html_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 EDA Analysis Report</h1>
            <div class="metadata">
                <p><strong>Generated:</strong> {timestamp}</p>
                <p><strong>Dataset:</strong> {dataset_info.get('name', 'Unknown')}</p>
                <p><strong>Rows:</strong> {dataset_info.get('rows', 0):,} | <strong>Columns:</strong> {dataset_info.get('columns', 0)}</p>
            </div>
        </header>

        <nav class="toc">
            <h2>Table of Contents</h2>
            <ul>
                <li><a href="#overview">Overview</a></li>
                {'<li><a href="#profile">Dataset Profile</a></li>' if 'profile' in analysis_results else ''}
                {'<li><a href="#quality">Quality Assessment</a></li>' if 'quality' in analysis_results else ''}
                {'<li><a href="#visualizations">Visualizations</a></li>' if 'visualization' in analysis_results else ''}
                {'<li><a href="#features">Feature Analysis</a></li>' if 'feature' in analysis_results else ''}
                {'<li><a href="#statistics">Statistical Analysis</a></li>' if 'stat' in analysis_results else ''}
                {'<li><a href="#transformations">Transformations</a></li>' if 'transform' in analysis_results else ''}
            </ul>
        </nav>

        <section id="overview" class="section">
            <h2>📊 Overview</h2>
            {self._generate_overview_section(analysis_results, dataset_info)}
        </section>

        {''.join([self._generate_agent_section(agent_name, result)
                  for agent_name, result in analysis_results.items()])}

        <footer>
            <p>Generated by EDA Pipeline - Phase 3</p>
            <p>Powered by 6 Specialized AI Agents | Built with Streamlit & LangGraph</p>
        </footer>
    </div>
</body>
</html>
"""
        return html

    def _get_html_styles(self) -> str:
        """Return CSS styles for HTML report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }

        header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 3px solid #1f77b4;
            margin-bottom: 30px;
        }

        header h1 {
            font-size: 2.5rem;
            color: #1f77b4;
            margin-bottom: 20px;
        }

        .metadata {
            color: #666;
            font-size: 0.95rem;
        }

        .toc {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        .toc h2 {
            color: #1f77b4;
            margin-bottom: 15px;
        }

        .toc ul {
            list-style: none;
        }

        .toc li {
            margin: 8px 0;
        }

        .toc a {
            color: #333;
            text-decoration: none;
            font-weight: 500;
        }

        .toc a:hover {
            color: #1f77b4;
            text-decoration: underline;
        }

        .section {
            margin-bottom: 50px;
            scroll-margin-top: 20px;
        }

        .section h2 {
            color: #1f77b4;
            font-size: 2rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }

        .section h3 {
            color: #333;
            font-size: 1.5rem;
            margin: 25px 0 15px 0;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .metric-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #1f77b4;
        }

        .metric-card .label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
        }

        .metric-card .value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #1f77b4;
        }

        .info-box {
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }

        .warning-box {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }

        .success-box {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }

        .table-container {
            overflow-x: auto;
            margin: 20px 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #333;
        }

        tr:hover {
            background-color: #f8f9fa;
        }

        .chart-container {
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }

        .recommendations {
            list-style: none;
            margin: 15px 0;
        }

        .recommendations li {
            padding: 10px;
            margin: 8px 0;
            background-color: #f8f9fa;
            border-left: 3px solid #1f77b4;
            border-radius: 3px;
        }

        footer {
            text-align: center;
            padding: 30px 0;
            margin-top: 50px;
            border-top: 2px solid #e0e0e0;
            color: #666;
        }

        .agent-card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 5px solid #1f77b4;
        }

        .confidence-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 600;
            background-color: #28a745;
            color: white;
        }
        """

    def _generate_overview_section(
        self,
        analysis_results: Dict[str, Any],
        dataset_info: Dict[str, Any]
    ) -> str:
        """Generate overview section HTML"""

        completed = len(analysis_results)
        total = 6

        html = f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="label">Completed Agents</div>
                <div class="value">{completed}/{total}</div>
            </div>
            <div class="metric-card">
                <div class="label">Dataset Rows</div>
                <div class="value">{dataset_info.get('rows', 0):,}</div>
            </div>
            <div class="metric-card">
                <div class="label">Dataset Columns</div>
                <div class="value">{dataset_info.get('columns', 0)}</div>
            </div>
            <div class="metric-card">
                <div class="label">File Size</div>
                <div class="value">{dataset_info.get('file_size_formatted', 'N/A')}</div>
            </div>
        </div>

        <h3>Agent Status</h3>
        <div class="agent-card">
        """

        agents = {
            'profile': 'ProfileAgent',
            'quality': 'QualityAgent',
            'transform': 'TransformAgent',
            'visualization': 'VisualizationAgent',
            'feature': 'FeatureAgent',
            'stat': 'StatAgent'
        }

        for key, name in agents.items():
            status = "✅ Completed" if key in analysis_results else "⏳ Pending"
            confidence = ""
            if key in analysis_results:
                conf = analysis_results[key].get('confidence', 0)
                confidence = f" | Confidence: {conf:.0%}"
            html += f"<p><strong>{name}:</strong> {status}{confidence}</p>\n"

        html += "</div>"

        return html

    def _generate_agent_section(self, agent_name: str, result: Dict[str, Any]) -> str:
        """Generate section for a specific agent's results"""

        section_map = {
            'profile': ('profile', 'Dataset Profile', '📈', self._generate_profile_html),
            'quality': ('quality', 'Quality Assessment', '✅', self._generate_quality_html),
            'visualization': ('visualizations', 'Visualizations', '🎨', self._generate_visualization_html),
            'feature': ('features', 'Feature Analysis', '🔍', self._generate_feature_html),
            'stat': ('statistics', 'Statistical Analysis', '📉', self._generate_stat_html),
            'transform': ('transformations', 'Transformations', '🔧', self._generate_transform_html)
        }

        if agent_name not in section_map:
            return ""

        section_id, title, emoji, generator = section_map[agent_name]

        html = f"""
        <section id="{section_id}" class="section">
            <h2>{emoji} {title}</h2>
            <div class="confidence-badge">Confidence: {result.get('confidence', 0):.0%}</div>
            {generator(result)}

            <div class="info-box">
                <h4>💡 Reasoning</h4>
                <p>{result.get('reasoning', 'N/A')}</p>
            </div>

            <div class="success-box">
                <h4>🎯 Impact</h4>
                <p>{result.get('impact', 'N/A')}</p>
            </div>

            <div class="info-box">
                <h4>📋 Recommendations</h4>
                <ul class="recommendations">
                    {''.join([f'<li>{rec}</li>' for rec in result.get('recommendations', [])])}
                </ul>
            </div>
        </section>
        """

        return html

    def _generate_profile_html(self, result: Dict[str, Any]) -> str:
        """Generate profile section HTML"""
        data = result.get('result', {})

        html = """
        <h3>Basic Information</h3>
        <div class="metrics-grid">
        """

        basic = data.get('basic_info', {})
        rows = self._safe_get(basic, 'rows', default=0)
        cols = self._safe_get(basic, 'columns', default=0)
        memory = self._safe_get(basic, 'memory_usage', default='N/A')
        file_size = self._safe_get(basic, 'file_size', default='N/A')

        html += f"""
            <div class="metric-card">
                <div class="label">Rows</div>
                <div class="value">{rows:,}</div>
            </div>
            <div class="metric-card">
                <div class="label">Columns</div>
                <div class="value">{cols}</div>
            </div>
            <div class="metric-card">
                <div class="label">File Size</div>
                <div class="value">{file_size}</div>
            </div>
        """

        if memory != 'N/A':
            html += f"""
            <div class="metric-card">
                <div class="label">Memory Usage</div>
                <div class="value">{memory}</div>
            </div>
            """

        html += "</div>"

        # Column types
        html += """
        <h3>Column Types</h3>
        <div class="metrics-grid">
        """

        col_types = data.get('column_types', {})
        html += f"""
            <div class="metric-card">
                <div class="label">Numeric</div>
                <div class="value">{len(col_types.get('numeric', []))}</div>
            </div>
            <div class="metric-card">
                <div class="label">Categorical</div>
                <div class="value">{len(col_types.get('categorical', []))}</div>
            </div>
            <div class="metric-card">
                <div class="label">Datetime</div>
                <div class="value">{len(col_types.get('datetime', []))}</div>
            </div>
        """

        html += "</div>"

        return html

    def _generate_quality_html(self, result: Dict[str, Any]) -> str:
        """Generate quality section HTML"""
        data = result.get('result', {})

        html = """
        <h3>Quality Metrics</h3>
        <div class="metrics-grid">
        """

        dup_pct = self._safe_get(data, 'duplicates', 'duplicate_percentage', default=0)
        outlier_cols = self._safe_get(data, 'outliers', 'columns_with_outliers', default=0)
        inconsistencies = self._safe_get(data, 'inconsistencies', 'inconsistency_count', default=0)
        type_issues = self._safe_get(data, 'data_types', 'type_issue_count', default=0)

        html += f"""
            <div class="metric-card">
                <div class="label">Duplicates</div>
                <div class="value">{dup_pct:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="label">Outlier Columns</div>
                <div class="value">{outlier_cols}</div>
            </div>
            <div class="metric-card">
                <div class="label">Inconsistencies</div>
                <div class="value">{inconsistencies}</div>
            </div>
            <div class="metric-card">
                <div class="label">Type Issues</div>
                <div class="value">{type_issues}</div>
            </div>
        """

        html += "</div>"

        # Outlier details table
        outliers = data.get('outliers', {})
        has_outliers = outliers.get('has_outliers', False)
        outlier_details = outliers.get('outlier_details', {})

        if has_outliers and outlier_details:
            html += """
            <h3>Outlier Details</h3>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Column</th>
                            <th>IQR Outliers</th>
                            <th>Percentage</th>
                            <th>Range</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for col, details in list(outlier_details.items())[:10]:
                iqr_outliers = details.get('iqr_outliers', 0)
                iqr_pct = details.get('iqr_percentage', 0)
                min_val = details.get('min', 0)
                max_val = details.get('max', 0)

                html += f"""
                    <tr>
                        <td>{col}</td>
                        <td>{iqr_outliers}</td>
                        <td>{iqr_pct:.1f}%</td>
                        <td>[{min_val:.2f}, {max_val:.2f}]</td>
                    </tr>
                """

            html += """
                    </tbody>
                </table>
            </div>
            """

        return html

    def _generate_visualization_html(self, result: Dict[str, Any]) -> str:
        """Generate visualization section HTML"""
        data = result.get('result', {})
        total_plots = data.get('total_plots', 0)

        html = f"""
        <p>Total plots generated: <strong>{total_plots}</strong></p>
        <div class="info-box">
            <p>Visualization artifacts are saved separately. Please refer to the <code>data/artifacts/plots/</code> directory for all generated charts.</p>
        </div>
        """

        return html

    def _generate_feature_html(self, result: Dict[str, Any]) -> str:
        """Generate feature analysis section HTML"""
        data = result.get('result', {})

        html = """
        <h3>Correlation Analysis</h3>
        <div class="metrics-grid">
        """

        corr = data.get('correlations', {})
        num_features = corr.get('num_numeric_features', 0)
        strong_corr = len(corr.get('strong_correlations', []))
        moderate_corr = len(corr.get('moderate_correlations', []))

        html += f"""
            <div class="metric-card">
                <div class="label">Numeric Features</div>
                <div class="value">{num_features}</div>
            </div>
            <div class="metric-card">
                <div class="label">Strong Correlations</div>
                <div class="value">{strong_corr}</div>
            </div>
            <div class="metric-card">
                <div class="label">Moderate Correlations</div>
                <div class="value">{moderate_corr}</div>
            </div>
        """

        html += "</div>"

        # Multicollinearity
        multi = data.get('multicollinearity', {})
        severity = multi.get('severity', 'none')
        severity_color = {"none": "#28a745", "moderate": "#ffc107", "high": "#dc3545"}
        color = severity_color.get(severity, "#6c757d")

        html += f"""
        <h3>Multicollinearity</h3>
        <div class="info-box" style="border-color: {color}">
            <p><strong>Severity:</strong> {severity.title()}</p>
        </div>
        """

        # Engineering suggestions
        eng = data.get('engineering_suggestions', {})
        by_priority = eng.get('by_priority', {})

        html += """
        <h3>Engineering Suggestions</h3>
        <div class="metrics-grid">
        """

        html += f"""
            <div class="metric-card">
                <div class="label">High Priority</div>
                <div class="value">{by_priority.get('high', 0)}</div>
            </div>
            <div class="metric-card">
                <div class="label">Medium Priority</div>
                <div class="value">{by_priority.get('medium', 0)}</div>
            </div>
            <div class="metric-card">
                <div class="label">Low Priority</div>
                <div class="value">{by_priority.get('low', 0)}</div>
            </div>
        """

        html += "</div>"

        return html

    def _generate_stat_html(self, result: Dict[str, Any]) -> str:
        """Generate statistics section HTML"""
        data = result.get('result', {})

        html = """
        <h3>Normality Tests</h3>
        <div class="metrics-grid">
        """

        norm = data.get('normality_tests', {})
        total_tested = norm.get('total_tested', 0)
        normal_features = norm.get('normal_features', 0)
        non_normal = norm.get('non_normal_features', 0)

        html += f"""
            <div class="metric-card">
                <div class="label">Features Tested</div>
                <div class="value">{total_tested}</div>
            </div>
            <div class="metric-card">
                <div class="label">Normal</div>
                <div class="value">{normal_features}</div>
            </div>
            <div class="metric-card">
                <div class="label">Non-Normal</div>
                <div class="value">{non_normal}</div>
            </div>
        """

        html += "</div>"

        # Hypothesis tests
        hyp = data.get('hypothesis_tests', {})
        total_tests = hyp.get('total_tests', 0)

        html += f"""
        <h3>Hypothesis Tests</h3>
        <div class="metric-card">
            <div class="label">Tests Performed</div>
            <div class="value">{total_tests}</div>
        </div>
        """

        return html

    def _generate_transform_html(self, result: Dict[str, Any]) -> str:
        """Generate transformations section HTML"""
        data = result.get('result', {})

        html = """
        <h3>Transformation Summary</h3>
        <div class="metrics-grid">
        """

        total = data.get('total_transformations', 0)
        high = data.get('high_priority', 0)
        medium = data.get('medium_priority', 0)
        low = data.get('low_priority', 0)

        html += f"""
            <div class="metric-card">
                <div class="label">Total</div>
                <div class="value">{total}</div>
            </div>
            <div class="metric-card">
                <div class="label">High Priority</div>
                <div class="value">{high}</div>
            </div>
            <div class="metric-card">
                <div class="label">Medium Priority</div>
                <div class="value">{medium}</div>
            </div>
            <div class="metric-card">
                <div class="label">Low Priority</div>
                <div class="value">{low}</div>
            </div>
        """

        html += "</div>"

        # List transformations
        html += """
        <h3>Proposed Transformations</h3>
        """

        transformations = data.get('transformations', [])

        for priority in ['high', 'medium', 'low']:
            transforms = [t for t in transformations if t.get('priority') == priority]

            if transforms:
                html += f"<h4>{priority.title()} Priority</h4>"
                html += "<ul class='recommendations'>"

                for t in transforms[:5]:  # Limit to 5 per priority
                    t_type = t.get('type', 'unknown').replace('_', ' ').title()
                    t_desc = t.get('description', 'No description')
                    t_reason = t.get('reasoning', 'No reasoning provided')

                    html += f"""
                    <li>
                        <strong>{t_type}:</strong> {t_desc}<br>
                        <small><em>{t_reason}</em></small>
                    </li>
                    """

                html += "</ul>"

        return html


# Convenience functions
def export_to_html(
    analysis_results: Dict[str, Any],
    dataset_info: Dict[str, Any],
    output_path: Optional[str] = None
) -> str:
    """
    Quick function to export analysis results to HTML

    Args:
        analysis_results: Dictionary of agent results
        dataset_info: Dataset metadata
        output_path: Optional custom output path

    Returns:
        Path to generated HTML file
    """
    manager = ExportManager()

    if output_path:
        filename = Path(output_path).name
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.html"

    return manager.export_html(analysis_results, dataset_info, filename)


def export_to_json(
    analysis_results: Dict[str, Any],
    dataset_info: Dict[str, Any],
    output_path: Optional[str] = None
) -> str:
    """
    Quick function to export analysis results to JSON

    Args:
        analysis_results: Dictionary of agent results
        dataset_info: Dataset metadata
        output_path: Optional custom output path

    Returns:
        Path to generated JSON file
    """
    manager = ExportManager()

    if output_path:
        filename = Path(output_path).name
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{timestamp}.json"

    return manager.export_json(analysis_results, dataset_info, filename)
