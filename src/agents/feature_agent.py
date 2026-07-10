from typing import Dict, Any, List, Tuple
import json
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.preprocessing import LabelEncoder
from src.agents.base_agent import BaseAgent
from src.data.dataset_handle import DatasetHandle
from src.utils.types import AgentResponse


class FeatureAgent(BaseAgent):
    """
    Agent responsible for feature analysis and engineering suggestions.
    Analyzes correlations, multicollinearity, and proposes feature engineering strategies.
    """

    def get_agent_name(self) -> str:
        return "FeatureAgent"

    def analyze(self, dataset_handle: DatasetHandle, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Analyze feature relationships and provide engineering suggestions

        Returns structured analysis with feature insights and recommendations
        """
        # Perform feature analysis
        feature_analysis = self._perform_feature_analysis(dataset_handle, context)

        # Create context for LLM
        analysis_context = self._prepare_context(feature_analysis, context)

        # Get LLM interpretation with explainability
        llm_response = self._get_llm_interpretation(analysis_context)

        # Construct AgentResponse
        return AgentResponse(
            result=feature_analysis,
            reasoning=llm_response["reasoning"],
            impact=llm_response["impact"],
            recommendations=llm_response["recommendations"],
            confidence=llm_response["confidence"]
        )

    def _perform_feature_analysis(self, dataset_handle: DatasetHandle, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive feature analysis"""

        # Get sample data
        sample_size = min(10000, dataset_handle.shape[0])
        df_sample = dataset_handle.sample(sample_size)

        profile = context.get('profile_results') if context else None

        analysis = {
            "sample_size": len(df_sample),
            "total_features": len(df_sample.columns),
            "correlations": self._analyze_correlations(df_sample),
            "multicollinearity": self._detect_multicollinearity(df_sample),
            "feature_importance_hints": self._get_feature_importance_hints(df_sample, profile),
            "feature_interactions": self._detect_feature_interactions(df_sample),
            "engineering_suggestions": self._suggest_feature_engineering(df_sample, profile)
        }

        return analysis

    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between numeric features"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) < 2:
            return {
                "num_numeric_features": len(numeric_cols),
                "has_correlations": False,
                "strong_correlations": [],
                "moderate_correlations": []
            }

        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr()

        strong_correlations = []
        moderate_correlations = []

        # Find significant correlations
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]

                if abs(corr_val) > 0.7:
                    strong_correlations.append({
                        "feature1": col1,
                        "feature2": col2,
                        "correlation": float(corr_val),
                        "strength": "strong"
                    })
                elif abs(corr_val) > 0.4:
                    moderate_correlations.append({
                        "feature1": col1,
                        "feature2": col2,
                        "correlation": float(corr_val),
                        "strength": "moderate"
                    })

        return {
            "num_numeric_features": len(numeric_cols),
            "has_correlations": len(strong_correlations) > 0 or len(moderate_correlations) > 0,
            "strong_correlations": strong_correlations,
            "moderate_correlations": moderate_correlations[:10],  # Top 10
            "summary": f"{len(strong_correlations)} strong, {len(moderate_correlations)} moderate"
        }

    def _detect_multicollinearity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect multicollinearity using VIF (Variance Inflation Factor) approximation"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) < 2:
            return {
                "has_multicollinearity": False,
                "vif_analysis": []
            }

        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr()

        # Simple multicollinearity detection: features with very high correlation
        multicollinear_pairs = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = abs(corr_matrix.iloc[i, j])
                if corr_val > 0.85:  # High threshold for multicollinearity
                    multicollinear_pairs.append({
                        "feature1": corr_matrix.columns[i],
                        "feature2": corr_matrix.columns[j],
                        "correlation": float(corr_val),
                        "recommendation": "Consider removing one of these features"
                    })

        return {
            "has_multicollinearity": len(multicollinear_pairs) > 0,
            "multicollinear_pairs": multicollinear_pairs,
            "severity": "high" if len(multicollinear_pairs) > 3 else "moderate" if len(multicollinear_pairs) > 0 else "none"
        }

    def _get_feature_importance_hints(self, df: pd.DataFrame, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Provide hints about feature importance based on characteristics"""

        hints = []

        # High variance features (likely more informative)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        variance_scores = {}

        for col in numeric_cols:
            if df[col].std() > 0:
                # Normalized variance (coefficient of variation)
                cv = df[col].std() / (abs(df[col].mean()) + 1e-10)
                variance_scores[col] = float(cv)

        # Sort by variance
        high_variance_features = sorted(variance_scores.items(), key=lambda x: x[1], reverse=True)[:5]

        if high_variance_features:
            hints.append({
                "type": "high_variance",
                "features": [f[0] for f in high_variance_features],
                "reasoning": "Features with high variance tend to be more informative for modeling",
                "priority": "high"
            })

        # Low cardinality categorical features (good for modeling)
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        good_categorical = []

        for col in categorical_cols:
            unique_count = df[col].nunique()
            if 2 <= unique_count <= 20:  # Sweet spot for categorical features
                good_categorical.append(col)

        if good_categorical:
            hints.append({
                "type": "good_categorical",
                "features": good_categorical[:5],
                "reasoning": "Categorical features with 2-20 unique values are typically good for modeling",
                "priority": "medium"
            })

        # Potential ID columns (low importance)
        if profile:
            high_cardinality = profile.get('issues', {}).get('high_cardinality_cols', [])
            if high_cardinality:
                hints.append({
                    "type": "potential_ids",
                    "features": high_cardinality[:5],
                    "reasoning": "High cardinality columns are likely IDs with low predictive value",
                    "priority": "low",
                    "recommendation": "Consider removing these features"
                })

        # Constant or near-constant features
        low_variance_features = []
        for col in numeric_cols:
            if df[col].nunique() < 2:
                low_variance_features.append(col)

        if low_variance_features:
            hints.append({
                "type": "low_variance",
                "features": low_variance_features,
                "reasoning": "Features with no variance provide no information",
                "priority": "high",
                "recommendation": "Remove these features"
            })

        return {
            "total_hints": len(hints),
            "hints": hints
        }

    def _detect_feature_interactions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect potential feature interactions"""

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) < 2:
            return {
                "has_interactions": False,
                "suggested_interactions": []
            }

        # Look for pairs with moderate correlation that might benefit from interaction terms
        corr_matrix = df[numeric_cols].corr()

        interaction_candidates = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = abs(corr_matrix.iloc[i, j])
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]

                # Moderate correlation suggests potential interaction
                if 0.3 < corr_val < 0.7:
                    interaction_candidates.append({
                        "feature1": col1,
                        "feature2": col2,
                        "correlation": float(corr_val),
                        "suggested_operation": "multiply",
                        "new_feature_name": f"{col1}_x_{col2}",
                        "reasoning": "Moderate correlation suggests these features might interact"
                    })

        # Also suggest ratio features for related numeric columns
        ratio_candidates = []
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                col1 = numeric_cols[i]
                col2 = numeric_cols[j]

                # Check if denominator has no zeros
                if (df[col2] != 0).all() and df[col2].min() > 0:
                    ratio_candidates.append({
                        "feature1": col1,
                        "feature2": col2,
                        "suggested_operation": "divide",
                        "new_feature_name": f"{col1}_div_{col2}",
                        "reasoning": "Ratio might capture relative relationship"
                    })

        return {
            "has_interactions": len(interaction_candidates) > 0 or len(ratio_candidates) > 0,
            "multiplication_interactions": interaction_candidates[:5],  # Top 5
            "ratio_interactions": ratio_candidates[:3],  # Top 3
            "total_suggestions": len(interaction_candidates) + len(ratio_candidates)
        }

    def _suggest_feature_engineering(self, df: pd.DataFrame, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest feature engineering strategies"""

        suggestions = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        # 1. Binning suggestions for continuous variables
        for col in numeric_cols[:3]:  # Top 3
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.5:  # Highly continuous
                suggestions.append({
                    "type": "binning",
                    "feature": col,
                    "strategy": "quantile_binning",
                    "parameters": {"n_bins": 5},
                    "reasoning": "Convert continuous variable to categorical bins for non-linear patterns",
                    "priority": "medium"
                })

        # 2. Log transformation for skewed features
        for col in numeric_cols:
            if df[col].min() > 0:  # Can apply log
                skewness = df[col].skew()
                if abs(skewness) > 1:
                    suggestions.append({
                        "type": "log_transform",
                        "feature": col,
                        "skewness": float(skewness),
                        "reasoning": f"High skewness ({skewness:.2f}) - log transform can normalize distribution",
                        "priority": "high" if abs(skewness) > 2 else "medium"
                    })

        # 3. Polynomial features
        if len(numeric_cols) >= 2:
            suggestions.append({
                "type": "polynomial_features",
                "features": numeric_cols[:3],
                "degree": 2,
                "reasoning": "Create squared and interaction terms to capture non-linear relationships",
                "priority": "low"
            })

        # 4. Target encoding for high cardinality categoricals
        for col in categorical_cols:
            unique_count = df[col].nunique()
            if unique_count > 20:
                suggestions.append({
                    "type": "target_encoding",
                    "feature": col,
                    "unique_values": int(unique_count),
                    "reasoning": f"High cardinality ({unique_count} categories) - target encoding better than one-hot",
                    "priority": "medium"
                })

        # 5. Date feature extraction
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                suggestions.append({
                    "type": "datetime_features",
                    "feature": col,
                    "extract": ["year", "month", "day", "day_of_week", "is_weekend"],
                    "reasoning": "Extract temporal features from datetime columns",
                    "priority": "high"
                })

        # 6. Aggregation features (if there are potential grouping columns)
        if profile:
            categorical_cols_profile = profile.get('column_types', {}).get('categorical', [])
            if categorical_cols_profile and len(numeric_cols) > 0:
                suggestions.append({
                    "type": "aggregation",
                    "group_by": categorical_cols_profile[:2],
                    "aggregate_features": numeric_cols[:3],
                    "operations": ["mean", "sum", "std", "count"],
                    "reasoning": "Create group-level statistics for categorical segments",
                    "priority": "medium"
                })

        return {
            "total_suggestions": len(suggestions),
            "by_priority": {
                "high": sum(1 for s in suggestions if s.get('priority') == 'high'),
                "medium": sum(1 for s in suggestions if s.get('priority') == 'medium'),
                "low": sum(1 for s in suggestions if s.get('priority') == 'low')
            },
            "suggestions": suggestions
        }

    def _prepare_context(self, feature_analysis: Dict[str, Any], prior_context: Dict[str, Any]) -> str:
        """Prepare context string for LLM"""

        context = f"""
Feature Analysis Results:

Dataset: {feature_analysis['total_features']} features analyzed ({feature_analysis['sample_size']:,} sample)

1. Correlation Analysis:
   - Numeric features: {feature_analysis['correlations']['num_numeric_features']}
   - Strong correlations (|r| > 0.7): {len(feature_analysis['correlations']['strong_correlations'])}
   - Moderate correlations (|r| > 0.4): {len(feature_analysis['correlations']['moderate_correlations'])}
"""

        if feature_analysis['correlations']['strong_correlations']:
            context += "\n   Strong correlation pairs:\n"
            for corr in feature_analysis['correlations']['strong_correlations'][:3]:
                context += f"   - {corr['feature1']} ↔ {corr['feature2']}: {corr['correlation']:.3f}\n"

        context += f"""
2. Multicollinearity:
   - Status: {feature_analysis['multicollinearity']['severity']}
   - Multicollinear pairs: {len(feature_analysis['multicollinearity'].get('multicollinear_pairs', []))}
"""

        if feature_analysis['multicollinearity'].get('multicollinear_pairs'):
            for pair in feature_analysis['multicollinearity']['multicollinear_pairs'][:2]:
                context += f"   - {pair['feature1']} ↔ {pair['feature2']}: {pair['correlation']:.3f}\n"

        context += f"""
3. Feature Importance Hints:
   - Total hints: {feature_analysis['feature_importance_hints']['total_hints']}
"""

        for hint in feature_analysis['feature_importance_hints']['hints'][:3]:
            context += f"   - {hint['type']}: {len(hint['features'])} features ({hint['priority']} priority)\n"

        context += f"""
4. Feature Interactions:
   - Multiplication interactions: {len(feature_analysis['feature_interactions'].get('multiplication_interactions', []))}
   - Ratio interactions: {len(feature_analysis['feature_interactions'].get('ratio_interactions', []))}

5. Engineering Suggestions:
   - Total suggestions: {feature_analysis['engineering_suggestions']['total_suggestions']}
   - High priority: {feature_analysis['engineering_suggestions']['by_priority']['high']}
   - Medium priority: {feature_analysis['engineering_suggestions']['by_priority']['medium']}
   - Low priority: {feature_analysis['engineering_suggestions']['by_priority']['low']}
"""

        return context

    def _get_llm_interpretation(self, analysis_context: str) -> Dict[str, Any]:
        """Get LLM interpretation with explainability"""

        system_message = """You are a feature engineering expert analyzing feature relationships and engineering opportunities.
Your job is to interpret the feature analysis and provide strategic guidance for ML modeling.

You must respond in JSON format with these fields:
{{
    "reasoning": "Explain WHY these features were analyzed and WHAT the methodology reveals",
    "impact": "Explain WHAT these feature insights mean for modeling and prediction",
    "recommendations": ["List of 3-5 prioritized feature engineering recommendations"],
    "confidence": 0.95
}}

Focus on:
1. Most important feature relationships to leverage
2. Multicollinearity issues and remediation
3. Feature engineering priorities
4. Potential model performance improvements
5. Risks of overfitting or data leakage

Be specific and actionable. Reference actual findings from the analysis."""

        user_message = f"""Analyze these feature analysis results and provide guidance:

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
                "reasoning": parsed.get("reasoning", "Feature analysis performed to identify relationships and engineering opportunities"),
                "impact": parsed.get("impact", "Feature insights guide modeling strategy"),
                "recommendations": parsed.get("recommendations", ["Address multicollinearity", "Engineer interaction features"]),
                "confidence": parsed.get("confidence", 0.85)
            }
        except Exception as e:
            # Fallback response
            return {
                "reasoning": "Comprehensive feature analysis performed including correlation analysis, multicollinearity detection, and engineering opportunity identification",
                "impact": "Understanding feature relationships helps prioritize feature engineering, avoid multicollinearity issues, and improve model performance",
                "recommendations": [
                    "Address multicollinear features by removing redundant variables",
                    "Create interaction terms for moderately correlated features",
                    "Apply transformations to highly skewed features",
                    "Engineer domain-specific features based on business knowledge",
                    "Validate feature importance with actual model training"
                ],
                "confidence": 0.80
            }
