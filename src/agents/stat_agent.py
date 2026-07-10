from typing import Dict, Any, List, Tuple
import json
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import (
    shapiro, normaltest, anderson, kstest,
    ttest_ind, mannwhitneyu, chi2_contingency,
    f_oneway, kruskal, pearsonr, spearmanr
)
from src.agents.base_agent import BaseAgent
from src.data.dataset_handle import DatasetHandle
from src.utils.types import AgentResponse


class StatAgent(BaseAgent):
    """
    Agent responsible for statistical validation and hypothesis testing.
    Performs normality tests, distribution analysis, and statistical significance tests.
    """

    def get_agent_name(self) -> str:
        return "StatAgent"

    def analyze(self, dataset_handle: DatasetHandle, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Perform statistical validation and provide explainable insights

        Returns structured analysis with statistical test results and interpretations
        """
        # Perform statistical analysis
        stat_results = self._perform_statistical_analysis(dataset_handle, context)

        # Create context for LLM
        analysis_context = self._prepare_context(stat_results, context)

        # Get LLM interpretation with explainability
        llm_response = self._get_llm_interpretation(analysis_context)

        # Construct AgentResponse
        return AgentResponse(
            result=stat_results,
            reasoning=llm_response["reasoning"],
            impact=llm_response["impact"],
            recommendations=llm_response["recommendations"],
            confidence=llm_response["confidence"]
        )

    def _perform_statistical_analysis(self, dataset_handle: DatasetHandle, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis"""

        # Get sample data
        sample_size = min(5000, dataset_handle.shape[0])  # Smaller sample for stat tests
        df_sample = dataset_handle.sample(sample_size)

        analysis = {
            "sample_size": len(df_sample),
            "normality_tests": self._test_normality(df_sample),
            "distribution_analysis": self._analyze_distributions(df_sample),
            "statistical_summaries": self._compute_statistical_summaries(df_sample),
            "hypothesis_tests": self._perform_hypothesis_tests(df_sample, context),
            "outlier_statistics": self._compute_outlier_statistics(df_sample)
        }

        return analysis

    def _test_normality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Test normality of numeric features using multiple tests"""

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        normality_results = []

        for col in numeric_cols[:10]:  # Top 10 features
            if df[col].notna().sum() < 3:
                continue

            data = df[col].dropna()

            if len(data) < 3:
                continue

            results = {
                "feature": col,
                "tests": {}
            }

            # Shapiro-Wilk test (sample size < 5000)
            if len(data) <= 5000:
                try:
                    stat, p_value = shapiro(data)
                    results["tests"]["shapiro_wilk"] = {
                        "statistic": float(stat),
                        "p_value": float(p_value),
                        "is_normal": p_value > 0.05,
                        "interpretation": "Normal" if p_value > 0.05 else "Not Normal"
                    }
                except:
                    pass

            # D'Agostino's K-squared test
            if len(data) >= 8:
                try:
                    stat, p_value = normaltest(data)
                    results["tests"]["dagostino"] = {
                        "statistic": float(stat),
                        "p_value": float(p_value),
                        "is_normal": p_value > 0.05,
                        "interpretation": "Normal" if p_value > 0.05 else "Not Normal"
                    }
                except:
                    pass

            # Skewness and Kurtosis
            try:
                skewness = stats.skew(data)
                kurtosis = stats.kurtosis(data)
                results["descriptive"] = {
                    "skewness": float(skewness),
                    "kurtosis": float(kurtosis),
                    "skew_interpretation": self._interpret_skewness(skewness),
                    "kurtosis_interpretation": self._interpret_kurtosis(kurtosis)
                }
            except:
                pass

            # Overall assessment
            normal_count = sum(1 for test in results["tests"].values() if test.get("is_normal", False))
            total_tests = len(results["tests"])

            results["overall_assessment"] = {
                "is_likely_normal": normal_count >= total_tests / 2 if total_tests > 0 else False,
                "confidence": "high" if total_tests >= 2 else "low"
            }

            normality_results.append(results)

        # Summary
        normal_features = sum(1 for r in normality_results if r["overall_assessment"]["is_likely_normal"])

        return {
            "total_tested": len(normality_results),
            "normal_features": normal_features,
            "non_normal_features": len(normality_results) - normal_features,
            "results": normality_results
        }

    def _interpret_skewness(self, skewness: float) -> str:
        """Interpret skewness value"""
        if abs(skewness) < 0.5:
            return "Approximately symmetric"
        elif skewness > 0.5:
            return f"Right-skewed (positive skew: {skewness:.2f})"
        else:
            return f"Left-skewed (negative skew: {skewness:.2f})"

    def _interpret_kurtosis(self, kurtosis: float) -> str:
        """Interpret kurtosis value"""
        if abs(kurtosis) < 0.5:
            return "Normal tails (mesokurtic)"
        elif kurtosis > 0.5:
            return f"Heavy tails (leptokurtic: {kurtosis:.2f})"
        else:
            return f"Light tails (platykurtic: {kurtosis:.2f})"

    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze distribution characteristics"""

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        distribution_analysis = []

        for col in numeric_cols[:10]:
            data = df[col].dropna()

            if len(data) < 2:
                continue

            analysis = {
                "feature": col,
                "distribution_type": self._identify_distribution_type(data),
                "moments": {
                    "mean": float(data.mean()),
                    "median": float(data.median()),
                    "mode": float(data.mode()[0]) if len(data.mode()) > 0 else float(data.median()),
                    "std": float(data.std()),
                    "variance": float(data.var()),
                    "range": float(data.max() - data.min()),
                    "iqr": float(data.quantile(0.75) - data.quantile(0.25))
                },
                "percentiles": {
                    "p01": float(data.quantile(0.01)),
                    "p05": float(data.quantile(0.05)),
                    "p25": float(data.quantile(0.25)),
                    "p50": float(data.quantile(0.50)),
                    "p75": float(data.quantile(0.75)),
                    "p95": float(data.quantile(0.95)),
                    "p99": float(data.quantile(0.99))
                }
            }

            distribution_analysis.append(analysis)

        return {
            "total_analyzed": len(distribution_analysis),
            "distributions": distribution_analysis
        }

    def _identify_distribution_type(self, data: pd.Series) -> str:
        """Identify likely distribution type based on characteristics"""

        skewness = stats.skew(data)
        kurtosis = stats.kurtosis(data)

        # Simple heuristics
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            return "likely_normal"
        elif skewness > 1:
            return "right_skewed"
        elif skewness < -1:
            return "left_skewed"
        elif kurtosis > 1:
            return "heavy_tailed"
        elif kurtosis < -1:
            return "light_tailed"
        else:
            return "mixed"

    def _compute_statistical_summaries(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute comprehensive statistical summaries"""

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        summaries = {
            "numeric_summary": {},
            "categorical_summary": {}
        }

        # Numeric summaries
        if numeric_cols:
            desc = df[numeric_cols].describe()
            summaries["numeric_summary"] = {
                "count": int(desc.loc['count'].mean()),
                "mean_of_means": float(desc.loc['mean'].mean()),
                "median_of_medians": float(df[numeric_cols].median().median()),
                "std_of_stds": float(desc.loc['std'].mean()),
                "cv_average": float(desc.loc['std'].mean() / (desc.loc['mean'].mean() + 1e-10))
            }

        # Categorical summaries
        if categorical_cols:
            summaries["categorical_summary"] = {
                "total_categories": sum(df[col].nunique() for col in categorical_cols),
                "avg_categories_per_feature": float(sum(df[col].nunique() for col in categorical_cols) / len(categorical_cols)),
                "most_diverse_feature": max(categorical_cols, key=lambda x: df[x].nunique()),
                "least_diverse_feature": min(categorical_cols, key=lambda x: df[x].nunique())
            }

        return summaries

    def _perform_hypothesis_tests(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform hypothesis tests based on data characteristics"""

        tests_performed = []

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        # Test 1: Correlation significance tests
        if len(numeric_cols) >= 2:
            # Test correlation between first two numeric features
            col1, col2 = numeric_cols[0], numeric_cols[1]
            data1 = df[col1].dropna()
            data2 = df[col2].dropna()

            # Get common indices
            common_idx = df[[col1, col2]].dropna().index
            if len(common_idx) > 2:
                try:
                    corr, p_value = pearsonr(df.loc[common_idx, col1], df.loc[common_idx, col2])
                    tests_performed.append({
                        "test_type": "pearson_correlation",
                        "feature1": col1,
                        "feature2": col2,
                        "correlation": float(corr),
                        "p_value": float(p_value),
                        "is_significant": p_value < 0.05,
                        "interpretation": f"Correlation is {'significant' if p_value < 0.05 else 'not significant'} at α=0.05"
                    })
                except:
                    pass

        # Test 2: Independence test for categorical variables
        if len(categorical_cols) >= 2:
            col1, col2 = categorical_cols[0], categorical_cols[1]
            try:
                contingency_table = pd.crosstab(df[col1], df[col2])
                chi2, p_value, dof, expected = chi2_contingency(contingency_table)

                tests_performed.append({
                    "test_type": "chi_square_independence",
                    "feature1": col1,
                    "feature2": col2,
                    "chi_square": float(chi2),
                    "p_value": float(p_value),
                    "degrees_of_freedom": int(dof),
                    "is_independent": p_value > 0.05,
                    "interpretation": f"Features are {'independent' if p_value > 0.05 else 'dependent'} at α=0.05"
                })
            except:
                pass

        # Test 3: Comparing means between groups (if categorical with numeric)
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]

            # Only test if categorical has 2-5 groups
            groups = df[cat_col].unique()
            if 2 <= len(groups) <= 5:
                try:
                    group_data = [df[df[cat_col] == g][num_col].dropna() for g in groups]
                    # Filter out empty groups
                    group_data = [g for g in group_data if len(g) > 0]

                    if len(group_data) >= 2:
                        # ANOVA test
                        f_stat, p_value = f_oneway(*group_data)

                        tests_performed.append({
                            "test_type": "one_way_anova",
                            "categorical_feature": cat_col,
                            "numeric_feature": num_col,
                            "f_statistic": float(f_stat),
                            "p_value": float(p_value),
                            "means_differ": p_value < 0.05,
                            "interpretation": f"Group means {'differ significantly' if p_value < 0.05 else 'do not differ'} at α=0.05"
                        })
                except:
                    pass

        return {
            "total_tests": len(tests_performed),
            "tests": tests_performed
        }

    def _compute_outlier_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute statistical measures of outliers"""

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        outlier_stats = []

        for col in numeric_cols[:10]:
            data = df[col].dropna()

            if len(data) < 4:
                continue

            # IQR method
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers_iqr = ((data < lower_bound) | (data > upper_bound)).sum()

            # Z-score method
            z_scores = np.abs(stats.zscore(data))
            outliers_z = (z_scores > 3).sum()

            # Modified Z-score (using median)
            median = data.median()
            mad = np.median(np.abs(data - median))
            modified_z_scores = 0.6745 * (data - median) / (mad + 1e-10)
            outliers_modified_z = (np.abs(modified_z_scores) > 3.5).sum()

            outlier_stats.append({
                "feature": col,
                "iqr_outliers": int(outliers_iqr),
                "iqr_percentage": float(outliers_iqr / len(data) * 100),
                "z_score_outliers": int(outliers_z),
                "z_score_percentage": float(outliers_z / len(data) * 100),
                "modified_z_outliers": int(outliers_modified_z),
                "severity": "high" if outliers_iqr > len(data) * 0.05 else "moderate" if outliers_iqr > 0 else "none"
            })

        return {
            "features_analyzed": len(outlier_stats),
            "outlier_statistics": outlier_stats
        }

    def _prepare_context(self, stat_results: Dict[str, Any], prior_context: Dict[str, Any]) -> str:
        """Prepare context string for LLM"""

        context = f"""
Statistical Analysis Results:

Sample Size: {stat_results['sample_size']:,} rows

1. Normality Tests:
   - Features tested: {stat_results['normality_tests']['total_tested']}
   - Normal distributions: {stat_results['normality_tests']['normal_features']}
   - Non-normal distributions: {stat_results['normality_tests']['non_normal_features']}
"""

        # Add normality details
        for result in stat_results['normality_tests']['results'][:3]:
            context += f"\n   - {result['feature']}: {result['overall_assessment']['is_likely_normal']} "
            if 'descriptive' in result:
                context += f"(skew={result['descriptive']['skewness']:.2f})"

        context += f"""

2. Distribution Analysis:
   - Features analyzed: {stat_results['distribution_analysis']['total_analyzed']}
"""

        for dist in stat_results['distribution_analysis']['distributions'][:3]:
            context += f"\n   - {dist['feature']}: {dist['distribution_type']} "
            context += f"(mean={dist['moments']['mean']:.2f}, std={dist['moments']['std']:.2f})"

        context += f"""

3. Hypothesis Tests:
   - Tests performed: {stat_results['hypothesis_tests']['total_tests']}
"""

        for test in stat_results['hypothesis_tests']['tests']:
            context += f"\n   - {test['test_type']}: {test['interpretation']}"

        context += f"""

4. Outlier Statistics:
   - Features analyzed: {stat_results['outlier_statistics']['features_analyzed']}
"""

        for outlier_stat in stat_results['outlier_statistics']['outlier_statistics'][:3]:
            context += f"\n   - {outlier_stat['feature']}: {outlier_stat['iqr_outliers']} outliers "
            context += f"({outlier_stat['iqr_percentage']:.1f}%) - severity: {outlier_stat['severity']}"

        return context

    def _get_llm_interpretation(self, analysis_context: str) -> Dict[str, Any]:
        """Get LLM interpretation with explainability"""

        system_message = """You are a statistical analysis expert interpreting hypothesis tests and distribution analysis.
Your job is to interpret the statistical results and provide actionable insights.

You must respond in JSON format with these fields:
{{
    "reasoning": "Explain WHY these statistical tests were performed and WHAT they reveal about the data",
    "impact": "Explain WHAT these statistical findings mean for modeling and analysis decisions",
    "recommendations": ["List of 3-5 specific actions based on statistical results"],
    "confidence": 0.95
}}

Focus on:
1. Normality assumptions for modeling
2. Statistical significance of relationships
3. Distribution characteristics and their implications
4. Outlier impact on statistical inference
5. Appropriate statistical methods to use

Be specific and reference actual test results."""

        user_message = f"""Analyze these statistical test results and provide guidance:

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
                "reasoning": parsed.get("reasoning", "Statistical tests performed to validate assumptions"),
                "impact": parsed.get("impact", "Statistical findings guide modeling approach"),
                "recommendations": parsed.get("recommendations", ["Check normality assumptions", "Address outliers"]),
                "confidence": parsed.get("confidence", 0.85)
            }
        except Exception as e:
            # Fallback response
            return {
                "reasoning": "Comprehensive statistical analysis including normality tests, distribution analysis, hypothesis testing, and outlier detection to validate data characteristics",
                "impact": "Statistical validation ensures appropriate modeling techniques are used and assumptions are met, improving model reliability and interpretability",
                "recommendations": [
                    "Use non-parametric methods for non-normal distributions",
                    "Transform skewed features before modeling",
                    "Validate statistical significance of feature relationships",
                    "Address outliers based on their statistical severity",
                    "Consider robust statistics for heavy-tailed distributions"
                ],
                "confidence": 0.80
            }
