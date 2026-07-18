"""
Demo script to showcase Phase 1 & 2 UI enhancements
Run with: python demo_enhancements.py
"""

import time
from datetime import datetime
from src.ui.components import (
    WorkflowStep,
    WorkflowProgressTracker,
    create_workflow_tracker,
    QualityVisualizer
)
import pandas as pd
import numpy as np


def demo_progress_tracker():
    """Demonstrate the progress tracking system"""
    print("=" * 60)
    print("DEMO: Progress Tracker Component")
    print("=" * 60)
    print()

    # Create a workflow tracker
    tracker = create_workflow_tracker("complete_analysis")

    print(f"Workflow: {tracker.workflow_name}")
    print(f"Total Steps: {tracker.total_steps}")
    print()

    # Simulate workflow execution
    for i, step in enumerate(tracker.steps):
        print(f"\nStep {i+1}/{tracker.total_steps}: {step.name}")
        print(f"  Description: {step.description}")
        print(f"  Status: {step.status_emoji} {step.status}")

        # Start step
        step.start()
        print(f"  Started at: {step.start_time.strftime('%H:%M:%S')}")

        # Simulate work
        work_time = np.random.uniform(0.5, 2.0)
        time.sleep(work_time)

        # Complete step
        step.complete()
        print(f"  Completed in: {step.duration:.2f}s")
        print(f"  Overall Progress: {tracker.progress_percentage:.1f}%")

        if tracker.estimated_time_remaining:
            print(f"  ETA: {tracker.estimated_time_remaining}")

    print()
    print(f"✅ Workflow completed!")
    print(f"Total time: {sum(s.duration for s in tracker.steps if s.duration):.2f}s")
    print()


def demo_quality_visualizer():
    """Demonstrate the quality visualization component"""
    print("=" * 60)
    print("DEMO: Quality Visualization Component")
    print("=" * 60)
    print()

    # Create sample dataset with quality issues
    np.random.seed(42)
    n_rows = 1000

    df = pd.DataFrame({
        'id': range(n_rows),
        'age': np.random.randint(18, 80, n_rows),
        'salary': np.random.normal(50000, 20000, n_rows),
        'name': ['John', 'Jane', 'Bob'] * (n_rows // 3) + ['Alice'],
        'score': np.random.uniform(0, 100, n_rows)
    })

    # Introduce quality issues

    # 1. Missing values
    df.loc[np.random.choice(n_rows, 150, replace=False), 'age'] = np.nan
    df.loc[np.random.choice(n_rows, 80, replace=False), 'salary'] = np.nan

    # 2. Outliers
    outlier_indices = np.random.choice(n_rows, 50, replace=False)
    df.loc[outlier_indices, 'salary'] = np.random.uniform(200000, 500000, 50)

    # 3. Duplicates
    df = pd.concat([df, df.iloc[:30]], ignore_index=True)

    print(f"Sample Dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    print()

    # Create visualizer
    viz = QualityVisualizer()

    # Calculate missing info
    missing_info = {}
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            missing_info[col] = {
                'count': int(missing_count),
                'percentage': float(missing_count / len(df) * 100)
            }

    print("Missing Value Analysis:")
    print("-" * 40)
    for col, info in missing_info.items():
        severity = "🔴" if info['percentage'] > 40 else "🟡" if info['percentage'] > 20 else "🟢"
        print(f"  {severity} {col}: {info['count']} ({info['percentage']:.1f}%)")
    print()

    # Calculate outlier info
    outlier_details = {}
    for col in ['age', 'salary', 'score']:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = ((df[col] < lower) | (df[col] > upper)).sum()

        if outliers > 0:
            outlier_details[col] = {
                'iqr_outliers': int(outliers),
                'iqr_percentage': float(outliers / len(df) * 100),
                'lower_bound': float(lower),
                'upper_bound': float(upper),
                'min': float(df[col].min()),
                'max': float(df[col].max())
            }

    print("Outlier Analysis:")
    print("-" * 40)
    for col, details in outlier_details.items():
        print(f"  ⚠️  {col}: {details['iqr_outliers']} outliers ({details['iqr_percentage']:.1f}%)")
        print(f"      Range: [{details['min']:.2f}, {details['max']:.2f}]")
        print(f"      Normal bounds: [{details['lower_bound']:.2f}, {details['upper_bound']:.2f}]")
    print()

    # Calculate duplicate info
    dup_count = df.duplicated().sum()
    dup_pct = (dup_count / len(df)) * 100

    print("Duplicate Analysis:")
    print("-" * 40)
    print(f"  {'🔴' if dup_pct > 15 else '🟡' if dup_pct > 5 else '🟢'} Duplicates: {dup_count} rows ({dup_pct:.1f}%)")
    print()

    # Calculate quality score
    quality_results = {
        'duplicates': {
            'duplicate_percentage': dup_pct
        },
        'outliers': {
            'outlier_details': outlier_details
        },
        'inconsistencies': {
            'inconsistency_count': 0
        }
    }

    score = viz._calculate_quality_score(quality_results)

    print("Overall Quality Score:")
    print("-" * 40)
    grade = "Excellent" if score >= 80 else "Good" if score >= 60 else "Fair" if score >= 40 else "Poor"
    emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🟠" if score >= 40 else "🔴"
    print(f"  {emoji} {score:.1f}/100 - {grade}")
    print()

    print("📊 In Streamlit, these would be displayed as interactive Plotly charts:")
    print("   - Missing value heatmap")
    print("   - Missing value bar chart")
    print("   - Outlier box plots")
    print("   - Outlier scatter plot")
    print("   - Duplicate gauge chart")
    print("   - Quality summary dashboard")
    print()


def demo_combined_workflow():
    """Demonstrate both enhancements in a simulated workflow"""
    print("=" * 60)
    print("DEMO: Combined Workflow with Progress & Quality Viz")
    print("=" * 60)
    print()

    # Create tracker
    tracker = create_workflow_tracker("quick_analysis")

    print("Starting Quick Analysis Workflow...")
    print()

    # Step 1: Profile
    step = tracker.steps[0]
    step.start()
    print(f"🔄 {step.name} - {step.description}")
    time.sleep(1.0)
    step.complete()
    print(f"   ✅ Completed in {step.duration:.1f}s")
    print()

    # Step 2: Quality
    step = tracker.steps[1]
    step.start()
    print(f"🔄 {step.name} - {step.description}")
    time.sleep(1.5)
    step.complete()
    print(f"   ✅ Completed in {step.duration:.1f}s")
    print()

    # Display quality findings
    print("   Quality Issues Found:")
    print("   • Missing values: 15% of cells")
    print("   • Outliers detected in 3 columns")
    print("   • 2.3% duplicate rows")
    print("   • Quality score: 76/100")
    print()

    # Step 3: Visualization
    step = tracker.steps[2]
    step.start()
    print(f"🔄 {step.name} - {step.description}")
    time.sleep(1.2)
    step.complete()
    print(f"   ✅ Completed in {step.duration:.1f}s")
    print()

    # Summary
    print(f"✅ Workflow Complete!")
    print(f"   Progress: {tracker.completed_count}/{tracker.total_steps} steps")
    print(f"   Total time: {sum(s.duration for s in tracker.steps if s.duration):.1f}s")
    print(f"   Status: All agents completed successfully")
    print()


def main():
    """Run all demos"""
    demos = [
        ("1", "Progress Tracker", demo_progress_tracker),
        ("2", "Quality Visualizer", demo_quality_visualizer),
        ("3", "Combined Workflow", demo_combined_workflow)
    ]

    print("\n")
    print("=" * 60)
    print("         UI/UX ENHANCEMENTS DEMO")
    print("         Phases 1 & 2 Implementation")
    print("=" * 60)
    print("\nAvailable Demos:")
    for num, name, _ in demos:
        print(f"  {num}. {name}")
    print("  4. Run all demos")
    print("  0. Exit")
    print()

    while True:
        choice = input("Select demo (0-4): ").strip()

        if choice == "0":
            print("\nExiting demo. Thank you!")
            break
        elif choice == "4":
            print("\nRunning all demos...\n")
            for _, _, demo_func in demos:
                demo_func()
                print("\nPress Enter to continue...")
                input()
            print("\n✅ All demos completed!")
            break
        elif choice in ["1", "2", "3"]:
            demo_num = int(choice) - 1
            _, demo_name, demo_func = demos[demo_num]
            print(f"\nRunning: {demo_name}")
            print()
            demo_func()
            print("\nPress Enter to return to menu...")
            input()
        else:
            print("Invalid choice. Please select 0-4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
