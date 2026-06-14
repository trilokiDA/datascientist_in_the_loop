from typing import Dict, Any, List
import json
from src.agents.base_agent import BaseAgent
from src.data.dataset_handle import DatasetHandle
from src.utils.types import AgentResponse


class ProfileAgent(BaseAgent):
    """
    Agent responsible for initial dataset profiling.
    Analyzes structure, data types, missing values, cardinality.
    """

    def get_agent_name(self) -> str:
        return "ProfileAgent"

    def analyze(self, dataset_handle: DatasetHandle, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Profile the dataset and provide explainable insights

        Returns structured analysis with reasoning and impact
        """
        # Get comprehensive profile from dataset handle
        profile_summary = dataset_handle.get_profile_summary()

        # Create context for LLM
        analysis_context = self._prepare_context(profile_summary, dataset_handle.mode)

        # Get LLM interpretation with explainability
        llm_response = self._get_llm_interpretation(analysis_context)

        # Construct AgentResponse
        return AgentResponse(
            result=profile_summary,
            reasoning=llm_response["reasoning"],
            impact=llm_response["impact"],
            recommendations=llm_response["recommendations"],
            confidence=llm_response["confidence"]
        )

    def _prepare_context(self, profile_summary: Dict[str, Any], mode: str) -> str:
        """Prepare context string for LLM"""
        basic_info = profile_summary["basic_info"]
        column_types = profile_summary["column_types"]
        issues = profile_summary["issues"]

        context = f"""
Dataset Profile:
- Rows: {basic_info['rows']:,}
- Columns: {basic_info['columns']}
- File Size: {basic_info['file_size']}
- Processing Mode: {mode}

Column Types:
- Numeric: {len(column_types['numeric'])} columns
- Categorical: {len(column_types['categorical'])} columns
- Datetime: {len(column_types['datetime'])} columns
- Other: {len(column_types['other'])} columns

Detected Issues:
- High missing value columns (>40%): {len(issues['high_missing_cols'])} columns
  {issues['high_missing_cols'][:3] if issues['high_missing_cols'] else 'None'}
- High cardinality columns (>90% unique): {len(issues['high_cardinality_cols'])} columns
  {issues['high_cardinality_cols'][:3] if issues['high_cardinality_cols'] else 'None'}

Missing Value Summary:
{self._format_missing_summary(profile_summary['missing_info'])}

Cardinality Summary:
{self._format_cardinality_summary(profile_summary['cardinality_info'])}
"""
        return context

    def _format_missing_summary(self, missing_info: Dict[str, Any]) -> str:
        """Format missing value information"""
        if not missing_info:
            return "No missing values detected"

        lines = []
        for col, data in list(missing_info.items())[:5]:  # Top 5
            if data['count'] > 0:
                lines.append(f"  - {col}: {data['count']:,} ({data['percentage']:.2f}%)")

        return "\n".join(lines) if lines else "No missing values detected"

    def _format_cardinality_summary(self, cardinality_info: Dict[str, Any]) -> str:
        """Format cardinality information"""
        if not cardinality_info:
            return "No cardinality information"

        lines = []
        for col, data in list(cardinality_info.items())[:5]:  # Top 5
            lines.append(
                f"  - {col}: {data['unique_count']:,} unique ({data['unique_percentage']:.2f}%)"
            )

        return "\n".join(lines) if lines else "No cardinality information"

    def _get_llm_interpretation(self, analysis_context: str) -> Dict[str, Any]:
        """Get LLM interpretation with explainability"""

        system_message = """You are a data profiling expert analyzing a dataset.
Your job is to interpret the profiling results and provide actionable insights.

You must respond in JSON format with these fields:
{{
    "reasoning": "Explain WHY you performed this profiling and WHAT methodology you used",
    "impact": "Explain WHAT this profile reveals about the dataset and its implications for analysis",
    "recommendations": ["List of 3-5 specific next steps based on findings"],
    "confidence": 0.95
}}

Focus on:
1. Data quality issues that need attention
2. Potential challenges for modeling/analysis
3. Columns that may need special treatment
4. Overall dataset health assessment

Be specific and actionable. Reference actual column names and statistics."""

        user_message = f"""Analyze this dataset profile and provide insights:

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
                "reasoning": parsed.get("reasoning", "Profiling performed to understand dataset structure"),
                "impact": parsed.get("impact", "Profile reveals dataset characteristics"),
                "recommendations": parsed.get("recommendations", ["Review findings", "Proceed to quality check"]),
                "confidence": parsed.get("confidence", 0.85)
            }
        except Exception as e:
            # Fallback response
            return {
                "reasoning": "Automated profiling to understand dataset structure, types, missing values, and cardinality",
                "impact": f"Dataset contains {analysis_context.split('Rows: ')[1].split()[0]} rows with potential data quality issues detected",
                "recommendations": [
                    "Review columns with high missing values",
                    "Check high cardinality columns for encoding strategy",
                    "Proceed to quality analysis for deeper inspection"
                ],
                "confidence": 0.80
            }
