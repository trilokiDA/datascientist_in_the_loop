from typing import Dict, Any, List, Optional, Tuple
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from scipy import stats
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import adfuller
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.agents.base_agent import BaseAgent
from src.data.dataset_handle import DatasetHandle
from src.utils.types import AgentResponse
from src.utils.helpers import generate_id


class TimeSeriesAgent(BaseAgent):
    """
    Agent responsible for time series analysis.
    Detects temporal patterns, trends, seasonality, and provides forecasting insights.
    """

    def __init__(self):
        super().__init__()
        self.artifacts_dir = Path("data/artifacts/timeseries")
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def get_agent_name(self) -> str:
        return "TimeSeriesAgent"

    def analyze(self, dataset_handle: DatasetHandle, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Analyze time series data and provide explainable insights

        Returns structured analysis with reasoning and impact
        """
        # Identify datetime columns
        time_columns = self._identify_datetime_columns(dataset_handle, context)

        if not time_columns:
            return self._create_no_timeseries_response()

        # Perform time series analysis
        ts_summary = self._perform_time_series_analysis(dataset_handle, time_columns)

        # Create context for LLM
        analysis_context = self._prepare_context(ts_summary, time_columns, context)

        # Get LLM interpretation with explainability
        llm_response = self._get_llm_interpretation(analysis_context)

        # Construct AgentResponse
        return AgentResponse(
            result=ts_summary,
            reasoning=llm_response["reasoning"],
            impact=llm_response["impact"],
            recommendations=llm_response["recommendations"],
            confidence=llm_response["confidence"]
        )

    def _identify_datetime_columns(
        self,
        dataset_handle: DatasetHandle,
        context: Dict[str, Any] = None
    ) -> List[str]:
        """Identify datetime columns from dataset"""
        datetime_cols = []

        # First, check from profile context if available
        if context and "profile_results" in context:
            profile = context["profile_results"]
            if profile and "column_types" in profile:
                datetime_cols = profile["column_types"].get("datetime", [])

        # If not found in context, detect from dtypes
        if not datetime_cols:
            for col, dtype in dataset_handle.dtypes.items():
                if 'datetime' in str(dtype).lower() or 'date' in str(dtype).lower():
                    datetime_cols.append(col)

        # Also try parsing potential date columns (only for string/object columns)
        sample_df = dataset_handle.head(100)
        for col in sample_df.columns:
            if col not in datetime_cols:
                # Only try to parse string/object columns
                if sample_df[col].dtype not in ['object', 'string']:
                    continue

                try:
                    # Try to parse as datetime
                    parsed = pd.to_datetime(sample_df[col], errors='coerce')
                    # Check if parsing was successful
                    non_null_before = sample_df[col].notna().sum()
                    non_null_after = parsed.notna().sum()

                    # If at least 80% of non-null values were successfully parsed
                    if non_null_before > 0 and (non_null_after / non_null_before) > 0.8:
                        datetime_cols.append(col)
                except:
                    pass

        return list(set(datetime_cols))  # Remove duplicates

    def _perform_time_series_analysis(
        self,
        dataset_handle: DatasetHandle,
        time_columns: List[str]
    ) -> Dict[str, Any]:
        """Perform comprehensive time series analysis"""

        # Get sample data for analysis
        sample_size = min(10000, dataset_handle.shape[0])
        df_sample = dataset_handle.sample(sample_size)

        ts_summary = {
            "sample_size": len(df_sample),
            "total_rows": dataset_handle.shape[0],
            "datetime_columns": time_columns,
            "temporal_profiles": {},
            "decompositions": {},
            "stationarity_tests": {},
            "visualizations": []
        }

        # Analyze each datetime column
        for col in time_columns:
            try:
                # Convert to datetime
                df_sample[col] = pd.to_datetime(df_sample[col], errors='coerce')
                df_work = df_sample.dropna(subset=[col]).copy()

                if len(df_work) < 10:  # Need minimum data points
                    continue

                # Sort by datetime
                df_work = df_work.sort_values(col)

                # Temporal profiling
                ts_summary["temporal_profiles"][col] = self._profile_temporal_column(df_work, col)

                # Find numeric columns for decomposition
                numeric_cols = df_work.select_dtypes(include=[np.number]).columns.tolist()

                if numeric_cols:
                    # Analyze first numeric column for decomposition
                    target_col = numeric_cols[0]

                    # Decomposition analysis
                    decomp_result = self._decompose_time_series(df_work, col, target_col)
                    if decomp_result:
                        ts_summary["decompositions"][f"{col}_{target_col}"] = decomp_result

                    # Stationarity test
                    stationarity = self._test_stationarity(df_work, target_col)
                    ts_summary["stationarity_tests"][target_col] = stationarity

            except Exception as e:
                ts_summary["temporal_profiles"][col] = {
                    "error": str(e),
                    "message": "Failed to analyze this datetime column"
                }

        return ts_summary

    def _profile_temporal_column(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Profile a datetime column"""

        date_series = df[col]

        # Basic stats
        profile = {
            "column": col,
            "count": len(date_series),
            "min_date": str(date_series.min()),
            "max_date": str(date_series.max()),
            "date_range_days": (date_series.max() - date_series.min()).days,
        }

        # Detect frequency
        if len(date_series) > 1:
            date_diffs = date_series.diff().dropna()

            # Most common difference
            mode_diff = date_diffs.mode()
            if len(mode_diff) > 0:
                profile["inferred_frequency"] = self._infer_frequency(mode_diff.iloc[0])

            # Gaps analysis
            median_diff = date_diffs.median()
            gaps = date_diffs[date_diffs > median_diff * 2]
            profile["gaps_detected"] = len(gaps)
            profile["gap_percentage"] = float(len(gaps) / len(date_diffs) * 100) if len(date_diffs) > 0 else 0.0

        # Duplicates
        duplicate_dates = date_series.duplicated().sum()
        profile["duplicate_timestamps"] = int(duplicate_dates)
        profile["duplicate_percentage"] = float(duplicate_dates / len(date_series) * 100) if len(date_series) > 0 else 0.0

        # Time span coverage
        if profile.get("date_range_days", 0) > 0:
            expected_points = self._estimate_expected_points(
                profile["date_range_days"],
                profile.get("inferred_frequency", "unknown")
            )
            if expected_points:
                profile["coverage_percentage"] = float(len(date_series) / expected_points * 100)

        return profile

    def _infer_frequency(self, timedelta_obj) -> str:
        """Infer frequency from timedelta"""
        seconds = timedelta_obj.total_seconds()

        if seconds < 60:
            return "sub-minute"
        elif seconds < 3600:
            return f"{int(seconds/60)}-minute"
        elif seconds < 86400:
            return f"{int(seconds/3600)}-hour"
        elif seconds < 604800:
            return "daily"
        elif seconds < 2592000:
            return "weekly"
        elif seconds < 31536000:
            return "monthly"
        else:
            return "yearly"

    def _estimate_expected_points(self, days: int, frequency: str) -> Optional[int]:
        """Estimate expected number of data points"""
        freq_map = {
            "daily": days,
            "weekly": days / 7,
            "monthly": days / 30,
            "yearly": days / 365
        }

        for freq_key, multiplier in freq_map.items():
            if freq_key in frequency.lower():
                return int(multiplier)

        return None

    def _decompose_time_series(
        self,
        df: pd.DataFrame,
        date_col: str,
        value_col: str
    ) -> Optional[Dict[str, Any]]:
        """Decompose time series into trend, seasonal, and residual components"""

        try:
            # Prepare data
            df_ts = df[[date_col, value_col]].copy()
            df_ts = df_ts.dropna()

            if len(df_ts) < 14:  # STL needs at least 2 seasonal periods
                return None

            # Set datetime index
            df_ts = df_ts.set_index(date_col)
            df_ts = df_ts.sort_index()

            # Remove duplicates in index
            df_ts = df_ts[~df_ts.index.duplicated(keep='first')]

            # Infer frequency and resample if needed
            df_ts = df_ts.asfreq('D', method='ffill')  # Assume daily for now

            # Perform STL decomposition
            # period = 7 for weekly seasonality (common default)
            period = min(7, len(df_ts) // 2)
            if period < 2:
                return None

            stl = STL(df_ts[value_col], period=period, robust=True)
            result = stl.fit()

            decomposition = {
                "trend": {
                    "mean": float(result.trend.mean()),
                    "std": float(result.trend.std()),
                    "direction": self._detect_trend_direction(result.trend)
                },
                "seasonal": {
                    "mean": float(result.seasonal.mean()),
                    "std": float(result.seasonal.std()),
                    "strength": float(np.abs(result.seasonal).mean() / np.abs(df_ts[value_col]).mean())
                },
                "residual": {
                    "mean": float(result.resid.mean()),
                    "std": float(result.resid.std())
                },
                "period_used": int(period)
            }

            return decomposition

        except Exception as e:
            return {
                "error": str(e),
                "message": "Decomposition failed - data may be too short or irregular"
            }

    def _detect_trend_direction(self, trend_series: pd.Series) -> str:
        """Detect if trend is upward, downward, or flat"""
        if len(trend_series) < 2:
            return "unknown"

        # Linear regression slope
        x = np.arange(len(trend_series))
        y = trend_series.values

        # Remove NaN
        mask = ~np.isnan(y)
        if mask.sum() < 2:
            return "unknown"

        x_clean = x[mask]
        y_clean = y[mask]

        slope, _ = np.polyfit(x_clean, y_clean, 1)

        # Threshold for "flat" (less than 1% change over period)
        relative_slope = slope / np.mean(np.abs(y_clean)) if np.mean(np.abs(y_clean)) > 0 else 0

        if abs(relative_slope) < 0.01:
            return "flat"
        elif slope > 0:
            return "upward"
        else:
            return "downward"

    def _test_stationarity(self, df: pd.DataFrame, col: str) -> Dict[str, Any]:
        """Test for stationarity using Augmented Dickey-Fuller test"""

        try:
            series = df[col].dropna()

            if len(series) < 10:
                return {"error": "Insufficient data for stationarity test"}

            # ADF test
            result = adfuller(series, autolag='AIC')

            return {
                "test": "Augmented Dickey-Fuller",
                "adf_statistic": float(result[0]),
                "p_value": float(result[1]),
                "critical_values": {k: float(v) for k, v in result[4].items()},
                "is_stationary": bool(result[1] < 0.05),  # p-value < 0.05 means stationary
                "interpretation": "Stationary" if result[1] < 0.05 else "Non-stationary"
            }

        except Exception as e:
            return {
                "error": str(e),
                "message": "Stationarity test failed"
            }

    def _create_no_timeseries_response(self) -> AgentResponse:
        """Response when no datetime columns are detected"""
        return AgentResponse(
            result={
                "datetime_columns": [],
                "message": "No datetime columns detected in dataset",
                "suggestion": "Ensure date columns are properly formatted or convert string dates to datetime"
            },
            reasoning="Scanned all columns for datetime types and attempted to parse potential date strings, but no temporal data was found.",
            impact="Time series analysis cannot be performed without temporal data. The dataset appears to be cross-sectional rather than time-indexed.",
            recommendations=[
                "Check if any columns contain date/time information in string format",
                "Convert date strings to datetime format before analysis",
                "If this is not time series data, skip this agent and proceed with standard EDA"
            ],
            confidence=0.95
        )

    def _prepare_context(
        self,
        ts_summary: Dict[str, Any],
        time_columns: List[str],
        context: Dict[str, Any] = None
    ) -> str:
        """Prepare context string for LLM"""

        if not time_columns:
            return "No datetime columns detected."

        ctx_parts = [f"Time Series Analysis Summary:\n"]
        ctx_parts.append(f"- Total Rows: {ts_summary['total_rows']:,}")
        ctx_parts.append(f"- Sample Size: {ts_summary['sample_size']:,}")
        ctx_parts.append(f"- Datetime Columns: {len(time_columns)}\n")

        # Temporal profiles
        if ts_summary.get("temporal_profiles"):
            ctx_parts.append("Temporal Profiles:")
            for col, profile in ts_summary["temporal_profiles"].items():
                if "error" not in profile:
                    ctx_parts.append(f"\n  {col}:")
                    ctx_parts.append(f"    - Date Range: {profile.get('min_date', 'N/A')} to {profile.get('max_date', 'N/A')}")
                    ctx_parts.append(f"    - Span: {profile.get('date_range_days', 0)} days")
                    ctx_parts.append(f"    - Frequency: {profile.get('inferred_frequency', 'unknown')}")
                    ctx_parts.append(f"    - Gaps: {profile.get('gaps_detected', 0)} ({profile.get('gap_percentage', 0):.1f}%)")
                    ctx_parts.append(f"    - Duplicates: {profile.get('duplicate_timestamps', 0)} ({profile.get('duplicate_percentage', 0):.1f}%)")

        # Decompositions
        if ts_summary.get("decompositions"):
            ctx_parts.append("\n\nTrend & Seasonality Analysis:")
            for key, decomp in ts_summary["decompositions"].items():
                if "error" not in decomp:
                    ctx_parts.append(f"\n  {key}:")
                    ctx_parts.append(f"    - Trend: {decomp['trend']['direction']}")
                    ctx_parts.append(f"    - Seasonal Strength: {decomp['seasonal']['strength']:.3f}")
                    ctx_parts.append(f"    - Period: {decomp['period_used']} observations")

        # Stationarity
        if ts_summary.get("stationarity_tests"):
            ctx_parts.append("\n\nStationarity Tests:")
            for col, test in ts_summary["stationarity_tests"].items():
                if "error" not in test:
                    ctx_parts.append(f"\n  {col}: {test['interpretation']} (p-value: {test['p_value']:.4f})")

        return "\n".join(ctx_parts)

    def _get_llm_interpretation(self, analysis_context: str) -> Dict[str, Any]:
        """Get LLM interpretation with explainability"""

        system_message = """You are a time series analysis expert interpreting temporal data patterns.
Your job is to interpret the time series analysis results and provide actionable insights.

You must respond in JSON format with these fields:
{{
    "reasoning": "Explain WHY you performed this time series analysis and WHAT methodology you used",
    "impact": "Explain WHAT this analysis reveals about temporal patterns and implications",
    "recommendations": ["List of 3-5 specific next steps based on findings"],
    "confidence": 0.95
}}

Focus on:
1. Temporal data quality (gaps, duplicates, frequency consistency)
2. Trend direction and strength
3. Seasonal patterns and their business implications
4. Stationarity and what it means for forecasting
5. Suggested time-based features for modeling

Be specific and actionable. Reference actual findings from the analysis."""

        user_message = f"""Analyze this time series data and provide insights:

{analysis_context}

Provide your analysis in the specified JSON format."""

        prompt = self.create_structured_prompt(system_message, user_message)
        chain = prompt | self.llm

        response = chain.invoke({})

        # Parse response
        try:
            # Extract JSON from response
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            parsed = json.loads(content)

            return {
                "reasoning": parsed.get("reasoning", "Time series analysis performed to understand temporal patterns"),
                "impact": parsed.get("impact", "Analysis reveals temporal characteristics of the dataset"),
                "recommendations": parsed.get("recommendations", ["Review temporal patterns", "Check data quality", "Consider forecasting models"]),
                "confidence": parsed.get("confidence", 0.80)
            }
        except Exception as e:
            # Fallback response
            return {
                "reasoning": "Performed time series analysis including temporal profiling, trend/seasonality decomposition, and stationarity testing",
                "impact": "Dataset contains temporal patterns that should be considered for modeling and feature engineering",
                "recommendations": [
                    "Address any gaps or duplicate timestamps found",
                    "Consider the detected trend direction for forecasting",
                    "Extract time-based features (hour, day_of_week, etc.)",
                    "Use appropriate time series models based on stationarity findings"
                ],
                "confidence": 0.75
            }

    def generate_visualizations(
        self,
        dataset_handle: DatasetHandle,
        ts_summary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate time series visualizations"""

        viz_id = generate_id("ts_viz")
        plots = []

        # Get sample data
        sample_size = min(10000, dataset_handle.shape[0])
        df_sample = dataset_handle.sample(sample_size)

        time_columns = ts_summary.get("datetime_columns", [])

        for time_col in time_columns:
            try:
                # Convert to datetime
                df_sample[time_col] = pd.to_datetime(df_sample[time_col], errors='coerce')
                df_work = df_sample.dropna(subset=[time_col]).copy()

                if len(df_work) < 2:
                    continue

                # Sort by time
                df_work = df_work.sort_values(time_col)

                # Get numeric columns
                numeric_cols = df_work.select_dtypes(include=[np.number]).columns.tolist()

                if not numeric_cols:
                    continue

                # Visualize first numeric column
                value_col = numeric_cols[0]

                # 1. Time series line plot
                line_plot = self._create_time_series_plot(df_work, time_col, value_col, viz_id)
                if line_plot:
                    plots.append(line_plot)

                # 2. Decomposition plot (if available)
                decomp_key = f"{time_col}_{value_col}"
                if decomp_key in ts_summary.get("decompositions", {}):
                    decomp_data = ts_summary["decompositions"][decomp_key]
                    if "error" not in decomp_data:
                        decomp_plot = self._create_decomposition_plot(
                            df_work, time_col, value_col, viz_id
                        )
                        if decomp_plot:
                            plots.append(decomp_plot)

            except Exception as e:
                continue

        return plots

    def _create_time_series_plot(
        self,
        df: pd.DataFrame,
        time_col: str,
        value_col: str,
        viz_id: str
    ) -> Optional[Dict[str, Any]]:
        """Create interactive time series line plot"""

        try:
            fig = go.Figure()

            # Main time series line
            fig.add_trace(go.Scatter(
                x=df[time_col],
                y=df[value_col],
                mode='lines+markers',
                name=value_col,
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=4)
            ))

            # Add trend line
            x_numeric = np.arange(len(df))
            y = df[value_col].values
            mask = ~np.isnan(y)

            if mask.sum() > 1:
                z = np.polyfit(x_numeric[mask], y[mask], 1)
                p = np.poly1d(z)
                trend_y = p(x_numeric)

                fig.add_trace(go.Scatter(
                    x=df[time_col],
                    y=trend_y,
                    mode='lines',
                    name='Trend',
                    line=dict(color='red', width=2, dash='dash')
                ))

            fig.update_layout(
                title=f"Time Series: {value_col} over {time_col}",
                xaxis_title=time_col,
                yaxis_title=value_col,
                hovermode='x unified',
                template='plotly_white',
                height=500
            )

            # Save as HTML
            plot_path = self.artifacts_dir / f"{viz_id}_timeseries_{time_col}_{value_col}.html"
            fig.write_html(str(plot_path))

            return {
                "type": "time_series_plot",
                "columns": [time_col, value_col],
                "path": str(plot_path),
                "description": f"Time series visualization of {value_col} with trend line"
            }

        except Exception as e:
            return None

    def _create_decomposition_plot(
        self,
        df: pd.DataFrame,
        time_col: str,
        value_col: str,
        viz_id: str
    ) -> Optional[Dict[str, Any]]:
        """Create STL decomposition visualization"""

        try:
            # Prepare data
            df_ts = df[[time_col, value_col]].copy()
            df_ts = df_ts.dropna()

            if len(df_ts) < 14:
                return None

            # Set datetime index
            df_ts = df_ts.set_index(time_col)
            df_ts = df_ts.sort_index()
            df_ts = df_ts[~df_ts.index.duplicated(keep='first')]

            # Resample to daily
            df_ts = df_ts.asfreq('D', method='ffill')

            # STL decomposition
            period = min(7, len(df_ts) // 2)
            if period < 2:
                return None

            stl = STL(df_ts[value_col], period=period, robust=True)
            result = stl.fit()

            # Create subplots
            fig = make_subplots(
                rows=4, cols=1,
                subplot_titles=['Original', 'Trend', 'Seasonal', 'Residual'],
                vertical_spacing=0.08
            )

            # Original
            fig.add_trace(
                go.Scatter(x=df_ts.index, y=df_ts[value_col], mode='lines', name='Original', line=dict(color='blue')),
                row=1, col=1
            )

            # Trend
            fig.add_trace(
                go.Scatter(x=df_ts.index, y=result.trend, mode='lines', name='Trend', line=dict(color='red')),
                row=2, col=1
            )

            # Seasonal
            fig.add_trace(
                go.Scatter(x=df_ts.index, y=result.seasonal, mode='lines', name='Seasonal', line=dict(color='green')),
                row=3, col=1
            )

            # Residual
            fig.add_trace(
                go.Scatter(x=df_ts.index, y=result.resid, mode='lines', name='Residual', line=dict(color='purple')),
                row=4, col=1
            )

            fig.update_layout(
                height=800,
                title_text=f"STL Decomposition: {value_col}",
                showlegend=False,
                template='plotly_white'
            )

            # Save as HTML
            plot_path = self.artifacts_dir / f"{viz_id}_decomposition_{time_col}_{value_col}.html"
            fig.write_html(str(plot_path))

            return {
                "type": "decomposition",
                "columns": [time_col, value_col],
                "path": str(plot_path),
                "description": f"STL decomposition showing trend, seasonality, and residuals",
                "period": period
            }

        except Exception as e:
            return None
