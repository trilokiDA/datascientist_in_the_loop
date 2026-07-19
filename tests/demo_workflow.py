"""
Quick demo script to show Phase 2 workflow capabilities
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from src.graph.workflow import EDAWorkflow
from src.utils.helpers import generate_id
import json


def create_sample_data():
    """Create sample dataset"""
    print("\n=== Creating Sample Dataset ===")
    data = {
        'customer_id': range(1, 51),
        'age': [25, 30, 35, 40, 45, None] * 8 + [25, 30],  # Missing values
        'income': [50000, 60000, 70000, 80000, 90000, 100000] * 8 + [50000, 60000],
        'category': ['A', 'B', 'C'] * 16 + ['A', 'B'],
        'score': [85, 90, 78, 92, 88, 95] * 8 + [85, 90]
    }

    df = pd.DataFrame(data)

    # Add some duplicates
    df = pd.concat([df, df.iloc[:3]], ignore_index=True)

    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / "demo_data.csv"
    df.to_csv(file_path, index=False)

    print(f"Created: {file_path}")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")

    return str(file_path)


def run_demo():
    """Run workflow demo"""
    print("\n" + "=" * 70)
    print("PHASE 2 WORKFLOW DEMO")
    print("=" * 70)

    # Create dataset
    dataset_path = create_sample_data()

    # Initialize workflow
    print("\n=== Initializing Workflow ===")
    workflow = EDAWorkflow()
    thread_id = generate_id("demo")
    session_id = generate_id("demo_session")

    # Create initial state
    initial_state = workflow.create_initial_state(
        dataset_path=dataset_path,
        session_id=session_id,
        workflow_type="quick_profile"
    )

    print(f"Thread ID: {thread_id}")
    print(f"Workflow: quick_profile")

    # Run workflow
    print("\n=== Running Workflow ===")
    print("(Workflow will pause at each approval point)\n")

    step_num = 1

    try:
        for event in workflow.run(initial_state, thread_id):
            for node_name, node_state in event.items():
                if node_state:
                    current_step = node_state.get('current_step', 'N/A')
                    print(f"\nStep {step_num}: {node_name}")
                    print(f"  Current: {current_step}")
                    print(f"  Completed: {node_state.get('completed_steps', [])}")

                    if node_state.get('pending_approval'):
                        approval_ctx = node_state.get('approval_context', {})
                        agent = approval_ctx.get('agent', 'Unknown')

                        print(f"\n--- {agent} Results ---")
                        print(f"Confidence: {approval_ctx.get('confidence', 0):.0%}")
                        print(f"\nReasoning:")
                        print(f"  {approval_ctx.get('reasoning', 'N/A')[:150]}...")
                        print(f"\nImpact:")
                        print(f"  {approval_ctx.get('impact', 'N/A')[:150]}...")
                        print(f"\nRecommendations:")
                        for i, rec in enumerate(approval_ctx.get('recommendations', [])[:3], 1):
                            print(f"  {i}. {rec}")

                        print("\n>>> Workflow paused for approval <<<")
                        print("    (In UI: user would click Approve/Reject/Skip)")

                        # For demo, we break after first agent
                        if agent == "ProfileAgent":
                            print("\n[Demo ends here - full workflow continues in UI]")
                            break

                    step_num += 1

            # Break outer loop too
            if node_state and node_state.get('pending_approval'):
                break

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

    # Get final state
    print("\n=== Checkpoint State ===")
    saved_state = workflow.get_state(thread_id)

    if saved_state:
        print(f"State saved: Yes")
        print(f"Can resume: Yes")
        print(f"Profile results: {'Yes' if saved_state.get('profile_results') else 'No'}")

        # Show a sample of profile results
        if saved_state.get('profile_results'):
            profile = saved_state['profile_results']
            print(f"\nProfile Summary:")
            print(f"  Rows: {profile['basic_info']['rows']:,}")
            print(f"  Columns: {profile['basic_info']['columns']}")
            print(f"  Mode: {profile['basic_info']['mode']}")
            print(f"  Issues detected: {len(profile['issues']['high_missing_cols'])} high missing cols")

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Run: streamlit run src/ui/app_v2.py")
    print("  2. Upload demo_data.csv")
    print("  3. Click 'Start Quick Profile'")
    print("  4. Review and approve each agent")
    print("\n")


if __name__ == "__main__":
    run_demo()
