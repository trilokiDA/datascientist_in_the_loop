from typing import Dict, Any, List
import json
import numpy as np
import pandas as pd
from scipy import stats
from src.agents.base_agent import BaseAgent
from src.data.dataset_handle import DatasetHandle
from src.utils.types import AgentResponse


class QualityAgent(BaseAgent):
    """
    Agent responsible for data quality assessment.
    Detects duplicates, outliers, and inconsistencies.
    """

    def get_agent_name(self) -> str:
        return "QualityAgent"

    def analyze(self, dataset_handle: DatasetHandle, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Analyze data quality and provide explainable insights

        Returns structured analysis with reasoning and impact
        """
        # Perform quality checks
        quality_summary = self._perform_quality_checks(dataset_handle)

        # Create context for LLM
        analysis_context = self._prepare_context(quality_summary, context)

        # Get LLM interpretation with explainability
        llm_response = self._get_llm_interpretation(analysis_context)

        # Construct AgentResponse
        return AgentResponse(
            result=quality_summary,
            reasoning=llm_response["reasoning"],
            impact=llm_response["impact"],
            recommendations=llm_response["recommendations"],
            confidence=llm_response["confidence"]
        )

    def _perform_quality_checks(self, dataset_handle: DatasetHandle) -> Dict[str, Any]:
        """Perform comprehensive quality checks"""

        # Get sample data for analysis
        sample_size = min(10000, dataset_handle.shape[0])
        df_sample = dataset_handle.sample(sample_size)

        quality_summary = {
            "sample_size": len(df_sample),
            "total_rows": dataset_handle.shape[0],
            "duplicates": self._check_duplicates(df_sample, dataset_handle.shape[0]),
            "outliers": self._detect_outliers(df_sample),
            "inconsistencies": self._check_inconsistencies(df_sample),
            "data_types": self._validate_data_types(df_sample),
            "value_ranges": self._check_value_ranges(df_sample)
        }

        return quality_summary

    def _check_duplicates(self, df: pd.DataFrame, total_rows: int) -> Dict[str, Any]:
        """Check for duplicate rows"""
        duplicate_count = df.duplicated().sum()

        # Extrapolate to full dataset
        ratio = total_rows / len(df)
        estimated_duplicates = int(duplicate_count * ratio)

        return {
            "duplicate_rows": int(duplicate_count),
            "estimated_total_duplicates": int(estimated_duplicates),
            "duplicate_percentage": float(duplicate_count / len(df) * 100) if len(df) > 0 else 0.0,
            "has_duplicates": bool(duplicate_count > 0)
        }

    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers using IQR and Z-score methods"""
        outliers = {}

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if df[col].notna().sum() == 0:
                continue

            # IQR method
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            iqr_outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()

            # Z-score method
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            z_outliers = (z_scores > 3).sum()

            if iqr_outliers > 0 or z_outliers > 0:
                outliers[col] = {
                    "iqr_outliers": int(iqr_outliers),
                    "iqr_percentage": float(iqr_outliers / len(df) * 100),
                    "z_score_outliers": int(z_outliers),
                    "z_score_percentage": float(z_outliers / len(df) * 100),
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }

        return {
            "columns_with_outliers": len(outliers),
            "outlier_details": outliers,
            "has_outliers": len(outliers) > 0
        }

    def _check_inconsistencies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for data inconsistencies"""
        inconsistencies = []

        # Check for mixed types in object columns
        object_cols = df.select_dtypes(include=['object']).columns

        for col in object_cols:
            if df[col].notna().sum() == 0:
                continue

            # Check for numeric strings mixed with text
            try:
                numeric_mask = df[col].dropna().apply(lambda x: str(x).replace('.', '').replace('-', '').isdigit())
                if 0 < numeric_mask.sum() < len(df[col].dropna()):
                    inconsistencies.append({
                        "column": col,
                        "type": "mixed_numeric_text",
                        "description": f"Column contains both numeric and text values",
                        "affected_rows": int(numeric_mask.sum())
                    })
            except:
                pass

            # Check for inconsistent formatting (e.g., dates, phone numbers)
            if df[col].notna().sum() > 0:
                value_lengths = df[col].dropna().astype(str).str.len()
                if value_lengths.std() > value_lengths.mean() * 0.5:  # High variance in length
                    inconsistencies.append({
                        "column": col,
                        "type": "inconsistent_format",
                        "description": f"Column has inconsistent value lengths",
                        "length_range": f"{int(value_lengths.min())}-{int(value_lengths.max())}"
                    })

        return {
            "inconsistency_count": len(inconsistencies),
            "inconsistencies": inconsistencies,
            "has_inconsistencies": len(inconsistencies) > 0
        }

    def _validate_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate if data types are appropriate"""
        type_issues = []

        for col in df.columns:
            dtype = str(df[col].dtype)

            # Check if numeric column stored as object
            if dtype == 'object':
                try:
                    pd.to_numeric(df[col].dropna(), errors='raise')
                    type_issues.append({
                        "column": col,
                        "current_type": dtype,
                        "suggested_type": "numeric",
                        "reason": "Column contains only numeric values but stored as text"
                    })
                except:
                    pass

            # Check if datetime column stored as object
            if dtype == 'object':
                try:
                    sample_values = df[col].dropna().head(100)
                    if len(sample_values) > 0:
                        pd.to_datetime(sample_values, errors='raise')
                        type_issues.append({
                            "column": col,
                            "current_type": dtype,
                            "suggested_type": "datetime",
                            "reason": "Column contains datetime values but stored as text"
                        })
                except:
                    pass

        return {
            "type_issue_count": len(type_issues),
            "type_issues": type_issues,
            "has_type_issues": len(type_issues) > 0
        }

    def _check_value_ranges(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for unrealistic value ranges"""
        range_issues = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if df[col].notna().sum() == 0:
                continue

            min_val = df[col].min()
            max_val = df[col].max()

            # Check for negative values in potentially positive-only columns
            if 'age' in col.lower() or 'count' in col.lower() or 'quantity' in col.lower():
                if min_val < 0:
                    range_issues.append({
                        "column": col,
                        "issue": "negative_values",
                        "description": f"Column likely should be positive but has negative values",
                        "min": float(min_val),
                        "max": float(max_val)
                    })

            # Check for unrealistic age values
            if 'age' in col.lower():
                if max_val > 120 or min_val < 0:
                    range_issues.append({
                        "column": col,
                        "issue": "unrealistic_age",
                        "description": f"Age values outside realistic range (0-120)",
                        "min": float(min_val),
                        "max": float(max_val)
                    })

        return {
            "range_issue_count": len(range_issues),
            "range_issues": range_issues,
            "has_range_issues": len(range_issues) > 0
        }

    def _prepare_context(self, quality_summary: Dict[str, Any], prior_context: Dict[str, Any]) -> str:
        """Prepare context string for LLM"""

        context = f"""
Quality Assessment Results:

Dataset: {quality_summary['total_rows']:,} rows (analyzed {quality_summary['sample_size']:,} sample)

1. Duplicate Detection:
   - Duplicate rows found: {quality_summary['duplicates']['duplicate_rows']}
   - Estimated total duplicates: {quality_summary['duplicates']['estimated_total_duplicates']}
   - Percentage: {quality_summary['duplicates']['duplicate_percentage']:.2f}%

2. Outlier Detection:
   - Columns with outliers: {quality_summary['outliers']['columns_with_outliers']}
   - Details: {self._format_outliers(quality_summary['outliers']['outlier_details'])}

3. Data Inconsistencies:
   - Issues found: {quality_summary['inconsistencies']['inconsistency_count']}
   - Details: {self._format_inconsistencies(quality_summary['inconsistencies']['inconsistencies'])}

4. Data Type Validation:
   - Type issues: {quality_summary['data_types']['type_issue_count']}
   - Details: {self._format_type_issues(quality_summary['data_types']['type_issues'])}

5. Value Range Validation:
   - Range issues: {quality_summary['value_ranges']['range_issue_count']}
   - Details: {self._format_range_issues(quality_summary['value_ranges']['range_issues'])}
"""

        # Add profile context if available
        if prior_context and 'profile_results' in prior_context:
            profile = prior_context['profile_results']
            context += f"\n\nProfile Context:\n"
            context += f"- Columns: {profile['basic_info']['columns']}\n"
            context += f"- High missing columns: {len(profile['issues']['high_missing_cols'])}\n"

        return context

    def _format_outliers(self, outliers: Dict[str, Any]) -> str:
        """Format outlier information"""
        if not outliers:
            return "No outliers detected"

        lines = []
        for col, data in list(outliers.items())[:5]:  # Top 5
            lines.append(f"\n     - {col}: {data['iqr_outliers']} outliers ({data['iqr_percentage']:.1f}%)")

        return "".join(lines) if lines else "No outliers detected"

    def _format_inconsistencies(self, inconsistencies: List[Dict]) -> str:
        """Format inconsistency information"""
        if not inconsistencies:
            return "No inconsistencies detected"

        lines = []
        for inc in inconsistencies[:5]:  # Top 5
            lines.append(f"\n     - {inc['column']}: {inc['description']}")

        return "".join(lines)

    def _format_type_issues(self, type_issues: List[Dict]) -> str:
        """Format type issue information"""
        if not type_issues:
            return "No type issues detected"

        lines = []
        for issue in type_issues[:5]:  # Top 5
            lines.append(f"\n     - {issue['column']}: {issue['reason']}")

        return "".join(lines)

    def _format_range_issues(self, range_issues: List[Dict]) -> str:
        """Format range issue information"""
        if not range_issues:
            return "No range issues detected"

        lines = []
        for issue in range_issues[:5]:  # Top 5
            lines.append(f"\n     - {issue['column']}: {issue['description']}")

        return "".join(lines)

    def _get_llm_interpretation(self, analysis_context: str) -> Dict[str, Any]:
        """Get LLM interpretation with explainability"""

        system_message = """You are a data quality expert analyzing dataset quality issues.
Your job is to interpret the quality assessment results and provide actionable insights.

You must respond in JSON format with these fields:
{{
    "reasoning": "Explain WHY these quality checks were performed and WHAT methodology was used",
    "impact": "Explain WHAT these quality issues mean for the dataset and downstream analysis",
    "recommendations": ["List of 3-5 specific actions to address quality issues"],
    "confidence": 0.95
}}

Focus on:
1. Severity of quality issues
2. Priority of fixes
3. Potential causes of issues
4. Impact on modeling/analysis
5. Recommended remediation steps

Be specific and actionable. Reference actual findings from the analysis."""

        user_message = f"""Analyze these data quality findings and provide insights:

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
                "reasoning": parsed.get("reasoning", "Quality checks performed to identify data issues"),
                "impact": parsed.get("impact", "Quality issues may affect analysis reliability"),
                "recommendations": parsed.get("recommendations", ["Review quality issues", "Consider data cleaning"]),
                "confidence": parsed.get("confidence", 0.85)
            }
        except Exception as e:
            # Fallback response
            return {
                "reasoning": "Systematic quality checks performed including duplicate detection, outlier analysis, inconsistency checks, and data type validation",
                "impact": "Quality issues detected may impact analysis accuracy and require cleaning before modeling",
                "recommendations": [
                    "Address duplicate rows if present",
                    "Investigate outliers for validity",
                    "Fix data type inconsistencies",
                    "Validate value ranges for domain correctness",
                    "Consider data cleaning transformations"
                ],
                "confidence": 0.80
            }
