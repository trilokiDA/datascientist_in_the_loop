"""
Test script for new agents: VisualizationAgent, FeatureAgent, and StatAgent
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.dataset_handle import DatasetHandle
from src.agents.viz_agent import VisualizationAgent
from src.agents.feature_agent import FeatureAgent
from src.agents.stat_agent import StatAgent
from src.agents.profile_agent import ProfileAgent
from src.agents.quality_agent import QualityAgent
import pandas as pd
import os


def create_test_dataset():
    """Create a test dataset with interesting characteristics"""
    print("\n" + "="*60)
    print("Creating test dataset...")
    print("="*60)

    # Create sample data with various characteristics
    np.random.seed(42)
    n_samples = 1000

    data = {
        # Numeric features with different distributions
        'age': np.random.normal(35, 10, n_samples).clip(18, 80),
        'income': np.random.exponential(50000, n_samples),  # Right-skewed
        'score': np.random.normal(75, 15, n_samples),
        'rating': np.random.uniform(1, 5, n_samples),

        # Correlated features
        'experience_years': None,  # Will correlate with age
        'salary': None,  # Will correlate with income

        # Categorical features
        'category': np.random.choice(['A', 'B', 'C', 'D'], n_samples, p=[0.4, 0.3, 0.2, 0.1]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_samples),
        'status': np.random.choice(['Active', 'Inactive'], n_samples, p=[0.7, 0.3]),

        # High cardinality
        'user_id': range(n_samples)
    }

    df = pd.DataFrame(data)

    # Create correlations
    df['experience_years'] = (df['age'] - 18) * 0.6 + np.random.normal(0, 2, n_samples)
    df['experience_years'] = df['experience_years'].clip(0, 50)
    df['salary'] = df['income'] * 1.2 + np.random.normal(0, 10000, n_samples)

    # Add some missing values
    missing_indices = np.random.choice(n_samples, size=int(n_samples * 0.1), replace=False)
    df.loc[missing_indices, 'income'] = np.nan

    # Add some outliers
    outlier_indices = np.random.choice(n_samples, size=int(n_samples * 0.05), replace=False)
    df.loc[outlier_indices, 'score'] = np.random.uniform(0, 30, len(outlier_indices))

    # Save to CSV
    output_dir = Path("data/uploads")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "test_dataset_enhanced.csv"
    df.to_csv(output_path, index=False)

    print(f"\nTest dataset created: {output_path}")
    print(f"Shape: {df.shape}")
    print(f"Size: {os.path.getsize(output_path):,} bytes")

    return str(output_path)


def test_visualization_agent(dataset_path: str):
    """Test VisualizationAgent"""
    print("\n" + "="*60)
    print("Testing VisualizationAgent...")
    print("="*60)

    # Create dataset handle
    handle = DatasetHandle(dataset_path)

    # Run profile and quality first for context
    profile_agent = ProfileAgent()
    quality_agent = QualityAgent()

    profile_response = profile_agent.analyze(handle)
    quality_response = quality_agent.analyze(handle, {"profile_results": profile_response["result"]})

    # Test visualization agent
    viz_agent = VisualizationAgent()

    context = {
        "profile_results": profile_response["result"],
        "quality_results": quality_response["result"]
    }

    response = viz_agent.analyze(handle, context)

    print(f"\nAgent: {viz_agent.get_agent_name()}")
    print(f"\nTotal Plots Generated: {response['result']['total_plots']}")
    print(f"Sample Size: {response['result']['sample_size']:,}")

    print(f"\nPlot Summary:")
    for plot_type, count in response['result']['summary']['by_type'].items():
        print(f"  - {plot_type}: {count}")

    print(f"\nReasoning:")
    print(f"  {response['reasoning'][:200]}...")

    print(f"\nImpact:")
    print(f"  {response['impact'][:200]}...")

    print(f"\nRecommendations:")
    for i, rec in enumerate(response['recommendations'], 1):
        print(f"  {i}. {rec}")

    print(f"\nConfidence: {response['confidence']:.0%}")

    # List generated plots
    print(f"\nGenerated Plots:")
    for plot in response['result']['plots'][:5]:  # Show first 5
        print(f"  - {plot['type']}: {plot.get('column', 'N/A')} -> {Path(plot['path']).name}")

    return response


def test_feature_agent(dataset_path: str):
    """Test FeatureAgent"""
    print("\n" + "="*60)
    print("Testing FeatureAgent...")
    print("="*60)

    # Create dataset handle
    handle = DatasetHandle(dataset_path)

    # Run profile first for context
    profile_agent = ProfileAgent()
    profile_response = profile_agent.analyze(handle)

    # Test feature agent
    feature_agent = FeatureAgent()

    context = {
        "profile_results": profile_response["result"]
    }

    response = feature_agent.analyze(handle, context)

    print(f"\nAgent: {feature_agent.get_agent_name()}")

    print(f"\nFeature Analysis Summary:")
    print(f"  Total Features: {response['result']['total_features']}")

    print(f"\nCorrelations:")
    corr = response['result']['correlations']
    print(f"  Strong (|r| > 0.7): {len(corr['strong_correlations'])}")
    print(f"  Moderate (|r| > 0.4): {len(corr['moderate_correlations'])}")

    if corr['strong_correlations']:
        print(f"\n  Top Strong Correlations:")
        for c in corr['strong_correlations'][:3]:
            print(f"    - {c['feature1']} <-> {c['feature2']}: {c['correlation']:.3f}")

    print(f"\nMulticollinearity:")
    multi = response['result']['multicollinearity']
    print(f"  Severity: {multi['severity']}")
    print(f"  Multicollinear Pairs: {len(multi.get('multicollinear_pairs', []))}")

    print(f"\nFeature Importance Hints:")
    hints = response['result']['feature_importance_hints']
    print(f"  Total Hints: {hints['total_hints']}")
    for hint in hints['hints'][:3]:
        print(f"    - {hint['type']} ({hint['priority']} priority): {len(hint['features'])} features")

    print(f"\nEngineering Suggestions:")
    eng = response['result']['engineering_suggestions']
    print(f"  Total: {eng['total_suggestions']}")
    print(f"  High Priority: {eng['by_priority']['high']}")
    print(f"  Medium Priority: {eng['by_priority']['medium']}")
    print(f"  Low Priority: {eng['by_priority']['low']}")

    print(f"\nReasoning:")
    print(f"  {response['reasoning'][:200]}...")

    print(f"\nRecommendations:")
    for i, rec in enumerate(response['recommendations'], 1):
        print(f"  {i}. {rec}")

    print(f"\nConfidence: {response['confidence']:.0%}")

    return response


def test_stat_agent(dataset_path: str):
    """Test StatAgent"""
    print("\n" + "="*60)
    print("Testing StatAgent...")
    print("="*60)

    # Create dataset handle
    handle = DatasetHandle(dataset_path)

    # Run profile and feature analysis for context
    profile_agent = ProfileAgent()
    feature_agent = FeatureAgent()

    profile_response = profile_agent.analyze(handle)
    feature_response = feature_agent.analyze(handle, {"profile_results": profile_response["result"]})

    # Test stat agent
    stat_agent = StatAgent()

    context = {
        "profile_results": profile_response["result"],
        "feature_results": feature_response["result"]
    }

    response = stat_agent.analyze(handle, context)

    print(f"\nAgent: {stat_agent.get_agent_name()}")

    print(f"\nStatistical Analysis Summary:")
    print(f"  Sample Size: {response['result']['sample_size']:,}")

    print(f"\nNormality Tests:")
    norm = response['result']['normality_tests']
    print(f"  Features Tested: {norm['total_tested']}")
    print(f"  Normal: {norm['normal_features']}")
    print(f"  Non-Normal: {norm['non_normal_features']}")

    if norm['results']:
        print(f"\n  Sample Results:")
        for result in norm['results'][:3]:
            assessment = result['overall_assessment']
            print(f"    - {result['feature']}: {'Normal' if assessment['is_likely_normal'] else 'Non-Normal'}")
            if 'descriptive' in result:
                desc = result['descriptive']
                print(f"      Skewness: {desc['skewness']:.2f}, Kurtosis: {desc['kurtosis']:.2f}")

    print(f"\nDistribution Analysis:")
    dist = response['result']['distribution_analysis']
    print(f"  Features Analyzed: {dist['total_analyzed']}")

    if dist['distributions']:
        print(f"\n  Sample Distributions:")
        for d in dist['distributions'][:3]:
            print(f"    - {d['feature']}: {d['distribution_type']}")
            print(f"      Mean: {d['moments']['mean']:.2f}, Median: {d['moments']['median']:.2f}")

    print(f"\nHypothesis Tests:")
    hyp = response['result']['hypothesis_tests']
    print(f"  Tests Performed: {hyp['total_tests']}")

    if hyp['tests']:
        print(f"\n  Test Results:")
        for test in hyp['tests']:
            print(f"    - {test['test_type']}: {test['interpretation']}")

    print(f"\nOutlier Statistics:")
    outliers = response['result']['outlier_statistics']
    print(f"  Features Analyzed: {outliers['features_analyzed']}")

    if outliers['outlier_statistics']:
        print(f"\n  Sample Results:")
        for stat in outliers['outlier_statistics'][:3]:
            print(f"    - {stat['feature']}: {stat['iqr_outliers']} outliers ({stat['severity']} severity)")

    print(f"\nReasoning:")
    print(f"  {response['reasoning'][:200]}...")

    print(f"\nRecommendations:")
    for i, rec in enumerate(response['recommendations'], 1):
        print(f"  {i}. {rec}")

    print(f"\nConfidence: {response['confidence']:.0%}")

    return response


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("NEW AGENTS TEST SUITE")
    print("="*60)

    # Import numpy here to avoid issues if not installed
    import numpy as np
    globals()['np'] = np

    # Create test dataset
    dataset_path = create_test_dataset()

    # Test all three new agents
    print("\n\nTesting all three new agents...\n")

    try:
        # Test 1: VisualizationAgent
        viz_response = test_visualization_agent(dataset_path)

        # Test 2: FeatureAgent
        feature_response = test_feature_agent(dataset_path)

        # Test 3: StatAgent
        stat_response = test_stat_agent(dataset_path)

        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)

        print("\nSummary:")
        print(f"  - VisualizationAgent: {viz_response['result']['total_plots']} plots generated")
        print(f"  - FeatureAgent: {feature_response['result']['engineering_suggestions']['total_suggestions']} suggestions")
        print(f"  - StatAgent: {stat_response['result']['hypothesis_tests']['total_tests']} hypothesis tests")

        print("\nNext Steps:")
        print("  1. Check generated plots in: data/artifacts/plots/")
        print("  2. Review agent recommendations")
        print("  3. Run: streamlit run src/ui/app_v2.py")
        print("  4. Test integrated workflow with all agents")

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
