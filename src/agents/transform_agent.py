from typing import Dict, Any, List
import json
import pandas as pd
import numpy as np
from src.agents.base_agent import BaseAgent
from src.data.dataset_handle import DatasetHandle
from src.utils.types import AgentResponse, Transformation


class TransformAgent(BaseAgent):
    """
    Agent responsible for proposing and applying data transformations.
    Handles missing values, encoding, scaling, and other transformations.
    """

    def get_agent_name(self) -> str:
        return "TransformAgent"

    def analyze(self, dataset_handle: DatasetHandle, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Propose transformations based on quality and profile analysis

        Returns structured transformation proposals with reasoning
        """
        # Analyze what transformations are needed
        transformation_proposals = self._propose_transformations(dataset_handle, context)

        # Create context for LLM
        analysis_context = self._prepare_context(transformation_proposals, context)

        # Get LLM interpretation with explainability
        llm_response = self._get_llm_interpretation(analysis_context)

        # Construct AgentResponse
        return AgentResponse(
            result=transformation_proposals,
            reasoning=llm_response["reasoning"],
            impact=llm_response["impact"],
            recommendations=llm_response["recommendations"],
            confidence=llm_response["confidence"]
        )

    def _propose_transformations(self, dataset_handle: DatasetHandle, context: Dict[str, Any]) -> Dict[str, Any]:
        """Propose transformations based on data analysis"""

        transformations = []

        # Get dataset info
        profile = context.get('profile_results') if context else None
        quality = context.get('quality_results') if context else None

        # Get sample for analysis
        sample_size = min(1000, dataset_handle.shape[0])
        df_sample = dataset_handle.sample(sample_size)

        # 1. Handle duplicates
        if quality and quality.get('duplicates', {}).get('has_duplicates'):
            transformations.append({
                "id": "remove_duplicates",
                "type": "deduplication",
                "priority": "high",
                "description": "Remove duplicate rows from dataset",
                "params": {
                    "keep": "first",
                    "estimated_removals": quality['duplicates']['estimated_total_duplicates']
                },
                "reasoning": "Duplicate rows can skew analysis and modeling results",
                "impact": f"Will remove approximately {quality['duplicates']['estimated_total_duplicates']} rows",
                "approved": False
            })

        # 2. Handle missing values
        if profile:
            missing_info = profile.get('missing_info', {})
            for col, data in missing_info.items():
                if data['percentage'] > 5:  # More than 5% missing
                    # Determine strategy based on column type and missing percentage
                    if data['percentage'] > 50:
                        strategy = "drop_column"
                        desc = f"Drop column '{col}' due to high missing rate ({data['percentage']:.1f}%)"
                    else:
                        col_type = self._get_column_type(col, profile)
                        if col_type == "numeric":
                            strategy = "impute_median"
                            desc = f"Impute missing values in '{col}' with median"
                        elif col_type == "categorical":
                            strategy = "impute_mode"
                            desc = f"Impute missing values in '{col}' with mode"
                        else:
                            strategy = "impute_constant"
                            desc = f"Impute missing values in '{col}' with constant"

                    transformations.append({
                        "id": f"handle_missing_{col}",
                        "type": "missing_value_handling",
                        "priority": "high" if data['percentage'] > 20 else "medium",
                        "description": desc,
                        "params": {
                            "column": col,
                            "strategy": strategy,
                            "missing_count": data['count'],
                            "missing_percentage": data['percentage']
                        },
                        "reasoning": f"Column has {data['percentage']:.1f}% missing values which need handling",
                        "impact": f"Will affect {data['count']:,} rows in column '{col}'",
                        "approved": False
                    })

        # 3. Handle outliers
        if quality and quality.get('outliers', {}).get('has_outliers'):
            outlier_details = quality['outliers'].get('outlier_details', {})
            for col, outlier_data in list(outlier_details.items())[:5]:  # Top 5
                if outlier_data['iqr_percentage'] > 1:  # More than 1% outliers
                    transformations.append({
                        "id": f"handle_outliers_{col}",
                        "type": "outlier_handling",
                        "priority": "medium",
                        "description": f"Cap outliers in '{col}' using IQR method",
                        "params": {
                            "column": col,
                            "method": "cap",
                            "lower_bound": outlier_data['lower_bound'],
                            "upper_bound": outlier_data['upper_bound'],
                            "outlier_count": outlier_data['iqr_outliers']
                        },
                        "reasoning": f"Column has {outlier_data['iqr_outliers']} outliers that may skew analysis",
                        "impact": f"Will cap {outlier_data['iqr_outliers']} values to range [{outlier_data['lower_bound']:.2f}, {outlier_data['upper_bound']:.2f}]",
                        "approved": False
                    })

        # 4. Handle data type conversions
        if quality and quality.get('data_types', {}).get('has_type_issues'):
            type_issues = quality['data_types'].get('type_issues', [])
            for issue in type_issues:
                transformations.append({
                    "id": f"convert_type_{issue['column']}",
                    "type": "type_conversion",
                    "priority": "medium",
                    "description": f"Convert '{issue['column']}' from {issue['current_type']} to {issue['suggested_type']}",
                    "params": {
                        "column": issue['column'],
                        "from_type": issue['current_type'],
                        "to_type": issue['suggested_type']
                    },
                    "reasoning": issue['reason'],
                    "impact": f"Will convert data type for better analysis and memory efficiency",
                    "approved": False
                })

        # 5. Handle high cardinality columns
        if profile:
            high_cardinality = profile.get('issues', {}).get('high_cardinality_cols', [])
            for col in high_cardinality[:3]:  # Top 3
                transformations.append({
                    "id": f"handle_cardinality_{col}",
                    "type": "cardinality_reduction",
                    "priority": "low",
                    "description": f"Consider dropping or encoding '{col}' (high cardinality)",
                    "params": {
                        "column": col,
                        "suggested_action": "review"
                    },
                    "reasoning": "High cardinality columns may not be useful for modeling",
                    "impact": "May improve model performance by removing ID-like columns",
                    "approved": False
                })

        # 6. Categorical encoding (for remaining categorical columns)
        if profile:
            categorical_cols = profile.get('column_types', {}).get('categorical', [])
            for col in categorical_cols[:5]:  # Top 5
                # Check if not already in transformations
                if not any(t['params'].get('column') == col for t in transformations):
                    transformations.append({
                        "id": f"encode_{col}",
                        "type": "categorical_encoding",
                        "priority": "low",
                        "description": f"One-hot encode categorical column '{col}'",
                        "params": {
                            "column": col,
                            "method": "onehot"
                        },
                        "reasoning": "Categorical columns need encoding for numerical analysis",
                        "impact": "Will create binary columns for each category",
                        "approved": False
                    })

        # 7. Numeric scaling
        if profile:
            numeric_cols = profile.get('column_types', {}).get('numeric', [])
            if len(numeric_cols) > 0:
                transformations.append({
                    "id": "scale_numeric",
                    "type": "scaling",
                    "priority": "low",
                    "description": f"Standardize numeric columns for modeling",
                    "params": {
                        "columns": numeric_cols[:10],  # Top 10
                        "method": "standard"
                    },
                    "reasoning": "Scaling ensures all features contribute equally to models",
                    "impact": "Will transform numeric columns to mean=0, std=1",
                    "approved": False
                })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        transformations.sort(key=lambda x: priority_order.get(x['priority'], 3))

        return {
            "total_transformations": len(transformations),
            "high_priority": sum(1 for t in transformations if t['priority'] == 'high'),
            "medium_priority": sum(1 for t in transformations if t['priority'] == 'medium'),
            "low_priority": sum(1 for t in transformations if t['priority'] == 'low'),
            "transformations": transformations
        }

    def _get_column_type(self, col: str, profile: Dict[str, Any]) -> str:
        """Determine column type from profile"""
        column_types = profile.get('column_types', {})
        if col in column_types.get('numeric', []):
            return "numeric"
        elif col in column_types.get('categorical', []):
            return "categorical"
        elif col in column_types.get('datetime', []):
            return "datetime"
        return "other"

    def apply_transformations(self, df: pd.DataFrame, transformations: List[Transformation]) -> pd.DataFrame:
        """
        Apply approved transformations to dataframe

        Args:
            df: Input dataframe
            transformations: List of approved transformations

        Returns:
            Transformed dataframe
        """
        df_transformed = df.copy()

        for transform in transformations:
            if not transform.get('approved', False):
                continue

            try:
                transform_type = transform['type']
                params = transform['params']

                if transform_type == "deduplication":
                    df_transformed = df_transformed.drop_duplicates(keep=params.get('keep', 'first'))

                elif transform_type == "missing_value_handling":
                    col = params['column']
                    strategy = params['strategy']

                    if strategy == "drop_column":
                        df_transformed = df_transformed.drop(columns=[col])
                    elif strategy == "impute_median":
                        df_transformed[col].fillna(df_transformed[col].median(), inplace=True)
                    elif strategy == "impute_mode":
                        df_transformed[col].fillna(df_transformed[col].mode()[0], inplace=True)
                    elif strategy == "impute_constant":
                        df_transformed[col].fillna("MISSING", inplace=True)

                elif transform_type == "outlier_handling":
                    col = params['column']
                    if params['method'] == "cap":
                        df_transformed[col] = df_transformed[col].clip(
                            lower=params['lower_bound'],
                            upper=params['upper_bound']
                        )

                elif transform_type == "type_conversion":
                    col = params['column']
                    to_type = params['to_type']

                    if to_type == "numeric":
                        df_transformed[col] = pd.to_numeric(df_transformed[col], errors='coerce')
                    elif to_type == "datetime":
                        df_transformed[col] = pd.to_datetime(df_transformed[col], errors='coerce')

                elif transform_type == "categorical_encoding":
                    col = params['column']
                    if params['method'] == "onehot":
                        dummies = pd.get_dummies(df_transformed[col], prefix=col)
                        df_transformed = pd.concat([df_transformed.drop(columns=[col]), dummies], axis=1)

                elif transform_type == "scaling":
                    cols = params['columns']
                    if params['method'] == "standard":
                        for col in cols:
                            if col in df_transformed.columns:
                                mean = df_transformed[col].mean()
                                std = df_transformed[col].std()
                                if std > 0:
                                    df_transformed[col] = (df_transformed[col] - mean) / std

            except Exception as e:
                print(f"Warning: Failed to apply transformation {transform['id']}: {str(e)}")
                continue

        return df_transformed

    def _prepare_context(self, transformation_proposals: Dict[str, Any], prior_context: Dict[str, Any]) -> str:
        """Prepare context string for LLM"""

        context = f"""
Transformation Analysis:

Total Transformations Proposed: {transformation_proposals['total_transformations']}
- High Priority: {transformation_proposals['high_priority']}
- Medium Priority: {transformation_proposals['medium_priority']}
- Low Priority: {transformation_proposals['low_priority']}

Proposed Transformations:
"""

        for i, transform in enumerate(transformation_proposals['transformations'][:10], 1):
            context += f"\n{i}. [{transform['priority'].upper()}] {transform['description']}"
            context += f"\n   Type: {transform['type']}"
            context += f"\n   Reasoning: {transform['reasoning']}"
            context += f"\n   Impact: {transform['impact']}\n"

        return context

    def _get_llm_interpretation(self, analysis_context: str) -> Dict[str, Any]:
        """Get LLM interpretation with explainability"""

        system_message = """You are a data transformation expert analyzing proposed data transformations.
Your job is to interpret the transformation proposals and provide strategic guidance.

You must respond in JSON format with these fields:
{{
    "reasoning": "Explain WHY these transformations were proposed and the overall strategy",
    "impact": "Explain WHAT impact these transformations will have on the dataset and analysis",
    "recommendations": ["List of 3-5 recommendations for prioritizing and applying transformations"],
    "confidence": 0.95
}}

Focus on:
1. Priority and sequencing of transformations
2. Potential risks or side effects
3. Dependencies between transformations
4. Expected improvements to data quality
5. Considerations for specific use cases

Be specific and actionable. Reference the actual proposed transformations."""

        user_message = f"""Analyze these proposed transformations and provide guidance:

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
                "reasoning": parsed.get("reasoning", "Transformations proposed based on data quality analysis"),
                "impact": parsed.get("impact", "Transformations will improve data quality for analysis"),
                "recommendations": parsed.get("recommendations", ["Review high priority items", "Apply transformations sequentially"]),
                "confidence": parsed.get("confidence", 0.85)
            }
        except Exception as e:
            # Fallback response
            return {
                "reasoning": "Transformations proposed to address data quality issues including missing values, outliers, and type inconsistencies",
                "impact": "Applying these transformations will improve data quality, reduce noise, and prepare data for modeling",
                "recommendations": [
                    "Start with high priority transformations",
                    "Review each transformation before approval",
                    "Apply deduplication and missing value handling first",
                    "Consider domain knowledge when handling outliers",
                    "Test transformations on a sample before full application"
                ],
                "confidence": 0.80
            }
