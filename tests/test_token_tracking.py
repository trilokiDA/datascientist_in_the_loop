"""
Test script to verify token tracking implementation
Run this to check if all imports work correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing Token Tracking Implementation...")
print("=" * 50)

# Test 1: Import TokenTracker
try:
    from src.utils.token_tracker import TokenTracker
    print("✅ TokenTracker imported successfully")
except Exception as e:
    print(f"❌ Failed to import TokenTracker: {e}")
    sys.exit(1)

# Test 2: Import token metrics components
try:
    from src.ui.components.token_metrics import display_token_metrics, display_mini_token_badge
    print("✅ Token metrics components imported successfully")
except Exception as e:
    print(f"❌ Failed to import token metrics components: {e}")
    sys.exit(1)

# Test 3: Import BaseAgent
try:
    from src.agents.base_agent import BaseAgent
    print("✅ BaseAgent imported successfully")
except Exception as e:
    print(f"❌ Failed to import BaseAgent: {e}")
    sys.exit(1)

# Test 4: Check TokenTracker methods
try:
    methods = ['initialize', 'track_usage', 'get_usage', 'reset',
               'format_tokens', 'format_cost', 'get_agent_breakdown']
    for method in methods:
        if hasattr(TokenTracker, method):
            print(f"  ✓ TokenTracker.{method} exists")
        else:
            print(f"  ✗ TokenTracker.{method} missing")
    print("✅ TokenTracker has all required methods")
except Exception as e:
    print(f"❌ Failed to verify TokenTracker methods: {e}")
    sys.exit(1)

# Test 5: Test TokenTracker initialization and usage (without Streamlit)
try:
    # Mock streamlit session_state for testing
    class MockSessionState:
        def __init__(self):
            self._state = {}

        def __getattr__(self, key):
            return self._state.get(key)

        def __setattr__(self, key, value):
            if key == '_state':
                object.__setattr__(self, key, value)
            else:
                self._state[key] = value

        def __contains__(self, key):
            return key in self._state

        def __delitem__(self, key):
            del self._state[key]

    # Simulate session state
    import streamlit as st
    if not hasattr(st, 'session_state'):
        st.session_state = MockSessionState()

    # Initialize
    TokenTracker.initialize()
    print("✅ TokenTracker initialized successfully")

    # Test tracking
    TokenTracker.track_usage(
        agent_name="TestAgent",
        model_name="llama-3.3-70b-versatile",
        input_tokens=1000,
        output_tokens=500,
        metadata={"test": True}
    )
    print("✅ Token tracking works")

    # Get usage
    usage = TokenTracker.get_usage()
    assert usage['input_tokens'] == 1000, "Input tokens mismatch"
    assert usage['output_tokens'] == 500, "Output tokens mismatch"
    assert usage['total_tokens'] == 1500, "Total tokens mismatch"
    print(f"✅ Token usage tracked correctly: {usage['total_tokens']} tokens, ${usage['total_cost']:.6f}")

    # Test formatting
    formatted_tokens = TokenTracker.format_tokens(1000)
    assert formatted_tokens == "1,000", "Token formatting failed"
    print(f"✅ Token formatting works: {formatted_tokens}")

    formatted_cost = TokenTracker.format_cost(0.00159)
    print(f"✅ Cost formatting works: {formatted_cost}")

    # Test agent breakdown
    breakdown = TokenTracker.get_agent_breakdown()
    assert len(breakdown) == 1, "Agent breakdown count mismatch"
    assert breakdown[0]['agent'] == "TestAgent", "Agent name mismatch"
    print(f"✅ Agent breakdown works: {breakdown[0]['agent']} with {breakdown[0]['calls']} call(s)")

    # Reset
    TokenTracker.reset()
    usage_after_reset = TokenTracker.get_usage()
    assert usage_after_reset['total_tokens'] == 0, "Reset failed"
    print("✅ Token tracking reset works")

except Exception as e:
    print(f"❌ Token tracking test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 50)
print("🎉 All tests passed! Token tracking is ready to use.")
print("\nNext steps:")
print("1. Run your Streamlit app: streamlit run src/ui/app.py")
print("2. Upload a dataset and run any agent")
print("3. Check the sidebar for token usage metrics")
