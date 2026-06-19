"""
Test script for interrupt/resume workflow functionality
Tests the quick_profile workflow with checkpointing
"""

import sys
from pathlib import Path
import pandas as pd
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph.workflow import EDAWorkflow
from src.utils.helpers import generate_id, get_timestamp
from src.utils.types import UserDecision


def create_test_dataset():
    """Create a test dataset with quality issues"""
    print(" Creating test dataset...")

    # Create dataset with various issues
    data = {
        'id': range(1, 101),
        'age': [25, 30, 35, -5, 40, 45] * 16 + [25, 30, 35, None],  # Negative age, missing values
        'income': [50000, 60000, 70000, 80000, 90000, 100000] * 16 + [50000, 60000, 70000, 80000],
        'category': ['A', 'B', 'C', 'A', 'B', 'C'] * 16 + ['A', 'B', 'C', 'A'],
        'score': [85.5, 90.2, 78.3, 92.1, 88.7, 150.0] * 16 + [85.5, 90.2, 78.3, 92.1]  # Outlier: 150
    }

    df = pd.DataFrame(data)

    # Add some duplicates
    df = pd.concat([df, df.iloc[:5]], ignore_index=True)

    # Save to uploads
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / "test_workflow_data.csv"
    df.to_csv(file_path, index=False)

    print(f" Created test dataset: {file_path}")
    print(f"   - Rows: {len(df)}")
    print(f"   - Columns: {len(df.columns)}")
    print(f"   - Issues: duplicates, outliers, negative values, missing values")

    return str(file_path)


def test_workflow_with_interrupts():
    """Test workflow with interrupt/resume functionality"""

    print("\n" + "=" * 70)
    print(" TESTING WORKFLOW INTERRUPT/RESUME FUNCTIONALITY")
    print("=" * 70 + "\n")

    # Create test dataset
    dataset_path = create_test_dataset()

    # Initialize workflow
    print("\n Initializing workflow...")
    workflow = EDAWorkflow()

    # Create unique thread ID for this test
    thread_id = generate_id("test_thread")
    session_id = generate_id("test_session")

    print(f"   Thread ID: {thread_id}")
    print(f"   Session ID: {session_id}")

    # Create initial state
    initial_state = workflow.create_initial_state(
        dataset_path=dataset_path,
        session_id=session_id,
        workflow_type="quick_profile"
    )

    print(f"\n Initial State:")
    print(f"   - Dataset: {initial_state['dataset_path']}")
    print(f"   - Mode: {initial_state['dataset_mode']}")
    print(f"   - Rows: {initial_state['dataset_rows']:,}")
    print(f"   - Columns: {initial_state['dataset_cols']}")

    # ===== STEP 1: Run until first interrupt (after profile) =====
    print("\n" + "-" * 70)
    print(" STEP 1: Running workflow until first interrupt (ProfileAgent)...")
    print("-" * 70)

    events_count = 0
    last_state = None

    try:
        for event in workflow.run(initial_state, thread_id):
            events_count += 1
            print(f"\n Event {events_count}: {list(event.keys())}")

            for node_name, node_state in event.items():
                if node_state:
                    last_state = node_state
                    print(f"   Node: {node_name}")
                    print(f"   Current Step: {node_state.get('current_step', 'N/A')}")
                    print(f"   Completed Steps: {node_state.get('completed_steps', [])}")
                    print(f"   Pending Approval: {node_state.get('pending_approval', False)}")

                    # Check for interrupt
                    if node_state.get('pending_approval'):
                        print(f"\n  INTERRUPT: Workflow paused for human review")
                        approval_context = node_state.get('approval_context', {})
                        print(f"   Agent: {approval_context.get('agent', 'Unknown')}")
                        print(f"   Step: {approval_context.get('step', 'Unknown')}")
                        print(f"   Confidence: {approval_context.get('confidence', 0):.0%}")
                        break

    except Exception as e:
        print(f"\n Error during workflow execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    if not last_state:
        print("\n No state captured!")
        return False

    # ===== STEP 2: Verify checkpoint persistence =====
    print("\n" + "-" * 70)
    print(" STEP 2: Verifying checkpoint persistence...")
    print("-" * 70)

    # Get state from checkpoint
    saved_state = workflow.get_state(thread_id)

    if saved_state:
        print(" State retrieved from checkpoint!")
        print(f"   Current Step: {saved_state.get('current_step', 'N/A')}")
        print(f"   Completed Steps: {saved_state.get('completed_steps', [])}")
        print(f"   Profile Results: {'' if saved_state.get('profile_results') else ''}")
        print(f"   Quality Results: {'' if saved_state.get('quality_results') else ''}")
    else:
        print(" Failed to retrieve state from checkpoint!")
        return False

    # ===== STEP 3: Simulate user approval and resume =====
    print("\n" + "-" * 70)
    print(" STEP 3: Simulating user approval...")
    print("-" * 70)

    # Create user decision
    user_decision = UserDecision(
        step_id=saved_state.get('current_step', 'profile'),
        decision="approved",
        timestamp=get_timestamp(),
        feedback="Looks good, proceed to quality check"
    )

    print(f"   Decision: {user_decision['decision']}")
    print(f"   Feedback: {user_decision['feedback']}")

    # Update state with user decision
    updates = {
        "user_decisions": saved_state.get("user_decisions", []) + [user_decision],
        "pending_approval": False
    }

    workflow.update_state(thread_id, updates)
    print(" State updated with user decision")

    # ===== STEP 4: Resume workflow =====
    print("\n" + "-" * 70)
    print("  STEP 4: Resuming workflow from checkpoint...")
    print("-" * 70)

    time.sleep(1)  # Brief pause

    resume_events = 0
    try:
        for event in workflow.resume(thread_id):
            resume_events += 1
            print(f"\n Resume Event {resume_events}: {list(event.keys())}")

            for node_name, node_state in event.items():
                if node_state:
                    print(f"   Node: {node_name}")
                    print(f"   Current Step: {node_state.get('current_step', 'N/A')}")
                    print(f"   Completed Steps: {node_state.get('completed_steps', [])}")

                    # Check for next interrupt
                    if node_state.get('pending_approval'):
                        print(f"\n  INTERRUPT: Workflow paused again for human review")
                        approval_context = node_state.get('approval_context', {})
                        print(f"   Agent: {approval_context.get('agent', 'Unknown')}")
                        print(f"   Step: {approval_context.get('step', 'Unknown')}")
                        break

    except Exception as e:
        print(f"\n Error during resume: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # ===== STEP 5: Final verification =====
    print("\n" + "-" * 70)
    print(" STEP 5: Final verification...")
    print("-" * 70)

    final_state = workflow.get_state(thread_id)

    if final_state:
        print(f"   Completed Steps: {final_state.get('completed_steps', [])}")
        print(f"   Profile Results: {'' if final_state.get('profile_results') else ''}")
        print(f"   Quality Results: {'' if final_state.get('quality_results') else ''}")
        print(f"   Total Events: {events_count + resume_events}")
        print(f"   User Decisions: {len(final_state.get('user_decisions', []))}")
        print(f"   Reasoning Logs: {len(final_state.get('reasoning_log', []))}")

        # Display quality results summary
        if final_state.get('quality_results'):
            quality = final_state['quality_results']
            print(f"\n    Quality Results Summary:")
            print(f"      - Duplicates: {quality.get('duplicates', {}).get('duplicate_rows', 0)}")
            print(f"      - Columns with outliers: {quality.get('outliers', {}).get('columns_with_outliers', 0)}")
            print(f"      - Inconsistencies: {quality.get('inconsistencies', {}).get('inconsistency_count', 0)}")
    else:
        print(" Failed to retrieve final state!")
        return False

    print("\n" + "=" * 70)
    print(" WORKFLOW INTERRUPT/RESUME TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70 + "\n")

    return True


def test_full_quick_profile_workflow():
    """Test complete quick_profile workflow with all approvals"""

    print("\n" + "=" * 70)
    print(" TESTING COMPLETE QUICK_PROFILE WORKFLOW")
    print("=" * 70 + "\n")

    # Create test dataset
    dataset_path = create_test_dataset()

    # Initialize workflow
    workflow = EDAWorkflow()

    # Create unique thread ID
    thread_id = generate_id("full_test")
    session_id = generate_id("full_session")

    # Create initial state
    initial_state = workflow.create_initial_state(
        dataset_path=dataset_path,
        session_id=session_id,
        workflow_type="quick_profile"
    )

    print(" Running complete workflow with auto-approval...")

    step_count = 0
    max_steps = 10  # Safety limit

    try:
        # Start workflow
        for event in workflow.run(initial_state, thread_id):
            step_count += 1

            if step_count > max_steps:
                print(f"\n  Reached max steps ({max_steps}), stopping...")
                break

            for node_name, node_state in event.items():
                if node_state and node_state.get('pending_approval'):
                    step = node_state.get('current_step', 'unknown')
                    print(f"\n  Interrupt at step: {step}")

                    # Auto-approve
                    user_decision = UserDecision(
                        step_id=step,
                        decision="approved",
                        timestamp=get_timestamp(),
                        feedback="Auto-approved for testing"
                    )

                    updates = {
                        "user_decisions": node_state.get("user_decisions", []) + [user_decision],
                        "pending_approval": False
                    }

                    workflow.update_state(thread_id, updates)
                    print(f"    Auto-approved, resuming...")

                    # Resume
                    for resume_event in workflow.resume(thread_id):
                        step_count += 1
                        for rnode, rstate in resume_event.items():
                            if rstate and rstate.get('pending_approval'):
                                # Handle next interrupt in outer loop
                                break

        # Final state
        final_state = workflow.get_state(thread_id)
        print(f"\n Workflow completed!")
        print(f"   Steps: {step_count}")
        print(f"   Completed: {final_state.get('completed_steps', [])}")

    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("WORKFLOW TESTING SUITE")
    print("=" * 70 + "\n")

    # Test 1: Interrupt/Resume
    test1_passed = test_workflow_with_interrupts()

    # Test 2: Complete workflow
    # test2_passed = test_full_quick_profile_workflow()

    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)
    print(f"   Test 1 (Interrupt/Resume): {' PASSED' if test1_passed else ' FAILED'}")
    # print(f"   Test 2 (Complete Workflow): {' PASSED' if test2_passed else ' FAILED'}")
    print("=" * 70 + "\n")
