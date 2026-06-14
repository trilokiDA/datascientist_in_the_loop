import uuid
from datetime import datetime
from typing import Dict, Any
from src.utils.types import ReasoningLog, Transformation


def generate_id(prefix: str = "") -> str:
    """Generate unique ID with optional prefix"""
    unique = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique}" if prefix else unique


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat()


def create_reasoning_log(
    agent: str,
    action: str,
    reasoning: str,
    impact: str,
    confidence: float
) -> ReasoningLog:
    """Create a reasoning log entry"""
    return ReasoningLog(
        timestamp=get_timestamp(),
        agent=agent,
        action=action,
        reasoning=reasoning,
        impact=impact,
        confidence=confidence
    )


def create_transformation(
    trans_type: str,
    description: str,
    params: Dict[str, Any],
    reasoning: str,
    impact: str
) -> Transformation:
    """Create a transformation record"""
    return Transformation(
        id=generate_id("transform"),
        type=trans_type,
        description=description,
        params=params,
        reasoning=reasoning,
        impact=impact,
        approved=False
    )


def format_bytes(size_bytes: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_percentage(value: float, total: float) -> str:
    """Format as percentage string"""
    if total == 0:
        return "0.00%"
    return f"{(value / total * 100):.2f}%"
