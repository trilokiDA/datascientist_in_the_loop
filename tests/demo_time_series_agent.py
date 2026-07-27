"""
Demo script for TimeSeriesAgent

This script demonstrates the TimeSeriesAgent's capabilities:
1. Temporal profiling (frequency, gaps, duplicates)
2. Trend & seasonality detection (STL decomposition)
3. Stationarity testing (ADF test)
4. Interactive visualizations

Usage:
    python tests/demo_time_series_agent.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.time_series_agent import TimeSeriesAgent
from src.data.dataset_handle import DatasetHandle


def create_sample_time_series_data(output_path: str = "data/uploads/sample_timeseries.csv"):
    """Create sample time series dataset for testing"""

    print("Creating sample time series data...")

    # Generate 365 days of data
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(365)]

    # Generate synthetic time series with trend and seasonality
    np.random.seed(42)

    # Trend component (upward)
    trend = np.linspace(100, 200, 365)

    # Seasonal component (weekly pattern)
    seasonal = 20 * np.sin(2 * np.pi * np.arange(365) / 7)

    # Random noise
    noise = np.random.normal(0, 5, 365)

    # Combine components
    sales = trend + seasonal + noise

    # Add some missing dates (gaps)
    gap_indices = [50, 51, 100, 200, 201, 202]
    dates_with_gaps = [d for i, d in enumerate(dates) if i not in gap_indices]
    sales_with_gaps = [s for i, s in enumerate(sales) if i not in gap_indices]

    # Create DataFrame
    df = pd.DataFrame({
        'date': dates_with_gaps,
        'sales': sales_with_gaps,
        'temperature': np.random.uniform(15, 35, len(dates_with_gaps)),
        'region': np.random.choice(['North', 'South', 'East', 'West'], len(dates_with_gaps))
    })

    # Add some duplicate dates
    duplicate_rows = df.sample(5)
    df = pd.concat([df, duplicate_rows]).sort_values('date').reset_index(drop=True)

    # Save to CSV
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"[SUCCESS] Sample data created: {output_path}")
    print(f"  - Rows: {len(df)}")
    print(f"  - Columns: {df.columns.tolist()}")
    print(f"  - Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  - Gaps: {len(gap_indices)} dates missing")
    print(f"  - Duplicates: 5 duplicate timestamps\n")

    return str(output_path)


def run_time_series_analysis(dataset_path: str):
    """Run TimeSeriesAgent analysis on dataset"""

    print("=" * 60)
    print("TIME SERIES AGENT DEMO")
    print("=" * 60)

    # Initialize agent and dataset handle
    print("\n1. Initializing TimeSeriesAgent...")
    agent = TimeSeriesAgent()
    dataset_handle = DatasetHandle(dataset_path, force_mode="in_memory")

    print(f"   Dataset: {dataset_handle.shape[0]} rows, {dataset_handle.shape[1]} columns")
    print(f"   Mode: {dataset_handle.mode}")

    # Create mock context (simulating ProfileAgent results)
    print("\n2. Creating analysis context...")
    context = {
        "profile_results": {
            "column_types": {
                "numeric": ["sales", "temperature"],
                "categorical": ["region"],
                "datetime": ["date"],
                "other": []
            }
        }
    }

    # Run analysis
    print("\n3. Running time series analysis...")
    print("   - Identifying datetime columns")
    print("   - Profiling temporal data")
    print("   - Decomposing time series (STL)")
    print("   - Testing stationarity (ADF)")

    result = agent.analyze(dataset_handle, context)

    # Display results
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)

    # Agent response structure
    print("\n[RESULTS] RESULT SUMMARY:")
    ts_summary = result["result"]

    print(f"   Datetime Columns: {len(ts_summary['datetime_columns'])}")
    print(f"   Columns analyzed: {', '.join(ts_summary['datetime_columns'])}")

    # Temporal profiles
    if ts_summary.get("temporal_profiles"):
        print("\n[TIME] TEMPORAL PROFILES:")
        for col, profile in ts_summary["temporal_profiles"].items():
            if "error" not in profile:
                print(f"\n   {col}:")
                print(f"     - Date Range: {profile['min_date']} to {profile['max_date']}")
                print(f"     - Span: {profile['date_range_days']} days")
                print(f"     - Frequency: {profile.get('inferred_frequency', 'unknown')}")
                print(f"     - Gaps: {profile.get('gaps_detected', 0)} ({profile.get('gap_percentage', 0):.1f}%)")
                print(f"     - Duplicates: {profile.get('duplicate_timestamps', 0)} ({profile.get('duplicate_percentage', 0):.1f}%)")
                if 'coverage_percentage' in profile:
                    print(f"     - Coverage: {profile['coverage_percentage']:.1f}%")

    # Decompositions
    if ts_summary.get("decompositions"):
        print("\n[TREND] TREND & SEASONALITY:")
        for key, decomp in ts_summary["decompositions"].items():
            if "error" not in decomp:
                print(f"\n   {key}:")
                print(f"     - Trend Direction: {decomp['trend']['direction']}")
                print(f"     - Trend Mean: {decomp['trend']['mean']:.2f}")
                print(f"     - Seasonal Strength: {decomp['seasonal']['strength']:.3f}")
                print(f"     - Period: {decomp['period_used']} observations")

    # Stationarity tests
    if ts_summary.get("stationarity_tests"):
        print("\n[TEST] STATIONARITY TESTS:")
        for col, test in ts_summary["stationarity_tests"].items():
            if "error" not in test:
                print(f"\n   {col}:")
                print(f"     - Test: {test['test']}")
                print(f"     - Result: {test['interpretation']}")
                print(f"     - P-value: {test['p_value']:.4f}")
                print(f"     - ADF Statistic: {test['adf_statistic']:.4f}")

    # LLM interpretation
    print("\n[LLM] LLM INTERPRETATION:")
    print(f"\n   Reasoning:\n   {result['reasoning']}\n")
    print(f"   Impact:\n   {result['impact']}\n")
    print(f"   Confidence: {result['confidence']:.2%}")

    print("\n[TIPS] RECOMMENDATIONS:")
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"   {i}. {rec}")

    # Generate visualizations
    print("\n4. Generating visualizations...")
    plots = agent.generate_visualizations(dataset_handle, ts_summary)

    if plots:
        print(f"\n[VIZ] VISUALIZATIONS GENERATED: {len(plots)}")
        for plot in plots:
            print(f"   - {plot['type']}: {plot['description']}")
            print(f"     Path: {plot['path']}")
    else:
        print("   No visualizations generated (insufficient data or errors)")

    print("\n" + "=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("=" * 60)

    return result, plots


def main():
    """Main demo function"""

    # Step 1: Create sample data
    dataset_path = create_sample_time_series_data()

    # Step 2: Run analysis
    result, plots = run_time_series_analysis(dataset_path)

    print("\n[SUCCESS] Demo completed!")
    print(f"\n[FILES] Generated files:")
    print(f"   - Dataset: {dataset_path}")
    print(f"   - Visualizations: data/artifacts/timeseries/")
    print(f"\nOpen the HTML files in your browser to view interactive plots!")


if __name__ == "__main__":
    main()
