"""
Token Tracker Service
Tracks token usage and costs for LLM API calls
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import streamlit as st


class TokenTracker:
    """Singleton service to track token usage and costs across the session"""

    # Llama 3.3 70B pricing on Groq (per 1M tokens)
    PRICING = {
        'llama-3.3-70b-versatile': {
            'input': 0.59,   # $0.59 per 1M input tokens
            'output': 0.79   # $0.79 per 1M output tokens
        }
    }

    @staticmethod
    def initialize():
        """Initialize token tracking in session state"""
        if 'token_usage' not in st.session_state:
            st.session_state.token_usage = {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'requests': [],  # List of individual requests
                'agent_breakdown': {}  # Tokens per agent
            }

    @staticmethod
    def track_usage(
        agent_name: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Track token usage from an LLM call

        Args:
            agent_name: Name of the agent making the call
            model_name: Model name (e.g., 'llama-3.3-70b-versatile')
            input_tokens: Number of input/prompt tokens
            output_tokens: Number of output/completion tokens
            metadata: Optional additional metadata
        """
        TokenTracker.initialize()

        # Calculate cost
        pricing = TokenTracker.PRICING.get(model_name, TokenTracker.PRICING['llama-3.3-70b-versatile'])
        input_cost = (input_tokens * pricing['input']) / 1_000_000
        output_cost = (output_tokens * pricing['output']) / 1_000_000
        total_cost = input_cost + output_cost

        # Update cumulative totals
        st.session_state.token_usage['input_tokens'] += input_tokens
        st.session_state.token_usage['output_tokens'] += output_tokens
        st.session_state.token_usage['total_tokens'] += (input_tokens + output_tokens)
        st.session_state.token_usage['total_cost'] += total_cost

        # Track per-agent usage
        if agent_name not in st.session_state.token_usage['agent_breakdown']:
            st.session_state.token_usage['agent_breakdown'][agent_name] = {
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'cost': 0.0,
                'calls': 0
            }

        agent_stats = st.session_state.token_usage['agent_breakdown'][agent_name]
        agent_stats['input_tokens'] += input_tokens
        agent_stats['output_tokens'] += output_tokens
        agent_stats['total_tokens'] += (input_tokens + output_tokens)
        agent_stats['cost'] += total_cost
        agent_stats['calls'] += 1

        # Store individual request
        request_record = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'model': model_name,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'cost': total_cost,
            'metadata': metadata or {}
        }
        st.session_state.token_usage['requests'].append(request_record)

    @staticmethod
    def get_usage() -> Dict[str, Any]:
        """Get current token usage statistics"""
        TokenTracker.initialize()
        return st.session_state.token_usage

    @staticmethod
    def reset():
        """Reset token tracking"""
        if 'token_usage' in st.session_state:
            del st.session_state.token_usage
        TokenTracker.initialize()

    @staticmethod
    def format_tokens(tokens: int) -> str:
        """Format token count with thousands separator"""
        return f"{tokens:,}"

    @staticmethod
    def format_cost(cost: float) -> str:
        """Format cost in USD"""
        if cost < 0.01:
            return f"${cost:.4f}"
        elif cost < 1.0:
            return f"${cost:.3f}"
        else:
            return f"${cost:.2f}"

    @staticmethod
    def get_agent_breakdown() -> List[Dict[str, Any]]:
        """Get token usage breakdown by agent"""
        TokenTracker.initialize()
        breakdown = []
        for agent_name, stats in st.session_state.token_usage['agent_breakdown'].items():
            breakdown.append({
                'agent': agent_name,
                'input_tokens': stats['input_tokens'],
                'output_tokens': stats['output_tokens'],
                'total_tokens': stats['total_tokens'],
                'cost': stats['cost'],
                'calls': stats['calls']
            })
        # Sort by total tokens descending
        breakdown.sort(key=lambda x: x['total_tokens'], reverse=True)
        return breakdown
