"""
Quality Thresholds Configuration
Centralized configuration for all data quality check thresholds
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional


@dataclass
class QualityThresholds:
    """Configurable thresholds for data quality checks"""

    # Missing data thresholds
    missing_value_threshold: float = 40.0  # percentage - flag columns above this % missing

    # Cardinality thresholds
    high_cardinality_threshold: float = 90.0  # percentage - flag columns with >90% unique values
    low_cardinality_threshold: float = 5.0    # percentage - flag columns with <5% unique values

    # Outlier detection thresholds
    iqr_multiplier: float = 1.5        # IQR method multiplier (1.5=standard, 3.0=extreme)
    z_score_threshold: float = 3.0     # Z-score standard deviations

    # Correlation thresholds
    strong_correlation_threshold: float = 0.7      # |r| > 0.7 = strong
    moderate_correlation_threshold: float = 0.4    # |r| > 0.4 = moderate

    # Inconsistency thresholds
    format_variance_threshold: float = 0.5  # For detecting inconsistent formatting

    # Statistical distribution thresholds
    skewness_threshold: float = 0.5    # Absolute skewness threshold
    kurtosis_threshold: float = 0.5    # Absolute kurtosis threshold

    # Confidence thresholds (for AI responses)
    min_confidence_threshold: float = 0.6   # Minimum acceptable confidence
    high_confidence_threshold: float = 0.8  # High confidence indicator

    # Data type detection threshold
    datetime_parse_threshold: float = 0.5  # 50% successful parses to consider datetime

    def validate(self) -> None:
        """Validate that threshold values are sensible"""
        errors = []

        # Percentage thresholds (0-100)
        percentage_fields = [
            'missing_value_threshold',
            'high_cardinality_threshold',
            'low_cardinality_threshold'
        ]
        for field in percentage_fields:
            value = getattr(self, field)
            if not (0 <= value <= 100):
                errors.append(f"{field} must be between 0 and 100 (got {value})")

        # Positive thresholds
        if self.iqr_multiplier <= 0:
            errors.append(f"iqr_multiplier must be positive (got {self.iqr_multiplier})")
        if self.z_score_threshold <= 0:
            errors.append(f"z_score_threshold must be positive (got {self.z_score_threshold})")

        # Correlation thresholds (0-1)
        if not (0 <= self.strong_correlation_threshold <= 1):
            errors.append(f"strong_correlation_threshold must be between 0 and 1")
        if not (0 <= self.moderate_correlation_threshold <= 1):
            errors.append(f"moderate_correlation_threshold must be between 0 and 1")
        if self.moderate_correlation_threshold >= self.strong_correlation_threshold:
            errors.append("moderate_correlation_threshold must be < strong_correlation_threshold")

        # Raise all validation errors
        if errors:
            raise ValueError("Threshold validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'QualityThresholds':
        """Create from dictionary, ignoring unknown keys"""
        valid_fields = {k: v for k, v in config.items() if k in cls.__annotations__}
        return cls(**valid_fields)

    @classmethod
    def strict_preset(cls) -> 'QualityThresholds':
        """Strict quality checks - low tolerance for issues"""
        return cls(
            missing_value_threshold=20.0,      # More sensitive to missing data
            high_cardinality_threshold=80.0,   # Flag high cardinality earlier
            low_cardinality_threshold=10.0,    # Less sensitive to low cardinality
            iqr_multiplier=1.0,                # Stricter outlier detection
            z_score_threshold=2.5,             # Stricter Z-score
            strong_correlation_threshold=0.6,  # Lower bar for "strong"
            moderate_correlation_threshold=0.3,
            skewness_threshold=0.3,
            kurtosis_threshold=0.3
        )

    @classmethod
    def balanced_preset(cls) -> 'QualityThresholds':
        """Balanced quality checks - default settings"""
        return cls()  # Use default values

    @classmethod
    def permissive_preset(cls) -> 'QualityThresholds':
        """Permissive quality checks - high tolerance"""
        return cls(
            missing_value_threshold=60.0,      # Less sensitive to missing data
            high_cardinality_threshold=95.0,   # Only flag very high cardinality
            low_cardinality_threshold=2.0,     # More sensitive to low cardinality
            iqr_multiplier=3.0,                # Only extreme outliers
            z_score_threshold=4.0,             # Very conservative Z-score
            strong_correlation_threshold=0.8,  # Higher bar for "strong"
            moderate_correlation_threshold=0.5,
            skewness_threshold=1.0,
            kurtosis_threshold=1.0
        )

    def get_description(self, field_name: str) -> str:
        """Get human-readable description for a threshold field"""
        descriptions = {
            'missing_value_threshold': 'Flag columns with missing values above this percentage',
            'high_cardinality_threshold': 'Flag columns with unique values above this percentage',
            'low_cardinality_threshold': 'Flag columns with unique values below this percentage',
            'iqr_multiplier': 'IQR outlier detection multiplier (1.5=standard, 3.0=extreme)',
            'z_score_threshold': 'Standard deviations for Z-score outlier detection',
            'strong_correlation_threshold': 'Minimum |r| to classify as strong correlation',
            'moderate_correlation_threshold': 'Minimum |r| to classify as moderate correlation',
            'format_variance_threshold': 'Threshold for detecting inconsistent value formatting',
            'skewness_threshold': 'Absolute skewness value to flag distributions',
            'kurtosis_threshold': 'Absolute kurtosis value to flag distributions',
            'min_confidence_threshold': 'Minimum AI confidence score to accept',
            'high_confidence_threshold': 'AI confidence score considered high',
            'datetime_parse_threshold': 'Success rate to convert column to datetime'
        }
        return descriptions.get(field_name, 'No description available')

    def __str__(self) -> str:
        """Human-readable string representation"""
        return f"""Quality Thresholds:
  Missing Data: >{self.missing_value_threshold}%
  High Cardinality: >{self.high_cardinality_threshold}%
  Low Cardinality: <{self.low_cardinality_threshold}%
  Outliers: IQR={self.iqr_multiplier}x, Z-score={self.z_score_threshold}σ
  Correlations: Strong |r|>{self.strong_correlation_threshold}, Moderate |r|>{self.moderate_correlation_threshold}
  Distributions: Skewness>{self.skewness_threshold}, Kurtosis>{self.kurtosis_threshold}"""
