import os
from typing import Dict, Any, List, Literal
import pandas as pd
from pathlib import Path

from src.data.backends import DataBackend, InMemoryBackend, SampledBackend
from src.utils.types import MEMORY_THRESHOLD, SAMPLE_SIZE_PROFILING
from src.utils.helpers import format_bytes


class DatasetHandle:
    """
    Abstraction layer over dataset access.
    Automatically chooses between in-memory (pandas) and sampled (DuckDB) backends
    based on file size.
    """

    def __init__(self, path: str, force_mode: Literal["in_memory", "sampled"] = None):
        self.path = path
        self.file_size = os.path.getsize(path)

        # Determine backend mode
        if force_mode:
            self.mode = force_mode
        else:
            self.mode = "in_memory" if self.file_size < MEMORY_THRESHOLD else "sampled"

        # Initialize backend
        if self.mode == "in_memory":
            self.backend: DataBackend = InMemoryBackend(path)
        else:
            self.backend: DataBackend = SampledBackend(path, SAMPLE_SIZE_PROFILING)

        # Cache basic info
        self.shape = self.backend.get_shape()
        self.columns = self.backend.get_column_names()
        self.dtypes = self.backend.get_dtypes()

    def get_info(self) -> Dict[str, Any]:
        """Get dataset metadata"""
        return {
            "path": self.path,
            "mode": self.mode,
            "file_size": self.file_size,
            "file_size_formatted": format_bytes(self.file_size),
            "rows": self.shape[0],
            "columns": self.shape[1],
            "column_names": self.columns,
            "dtypes": self.dtypes,
            "threshold": MEMORY_THRESHOLD,
            "threshold_formatted": format_bytes(MEMORY_THRESHOLD)
        }

    def describe(self) -> pd.DataFrame:
        """Get statistical summary"""
        return self.backend.describe()

    def get_missing_info(self) -> Dict[str, Any]:
        """Get detailed missing value information"""
        missing_counts = self.backend.get_missing_counts()
        total_rows = self.shape[0]

        missing_info = {}
        for col, count in missing_counts.items():
            missing_info[col] = {
                "count": count,
                "percentage": (count / total_rows * 100) if total_rows > 0 else 0
            }

        return missing_info

    def get_cardinality_info(self) -> Dict[str, Any]:
        """Get cardinality (unique counts) information"""
        unique_counts = self.backend.get_unique_counts()
        total_rows = self.shape[0]

        cardinality_info = {}
        for col, count in unique_counts.items():
            cardinality_info[col] = {
                "unique_count": count,
                "unique_percentage": (count / total_rows * 100) if total_rows > 0 else 0,
                "is_high_cardinality": count > total_rows * 0.9
            }

        return cardinality_info

    def sample(self, n: int) -> pd.DataFrame:
        """Get random sample"""
        return self.backend.sample(n)

    def head(self, n: int = 5) -> pd.DataFrame:
        """Get first n rows"""
        return self.backend.head(n)

    def get_column_types(self) -> Dict[str, str]:
        """Categorize columns by data type"""
        numeric_cols = []
        categorical_cols = []
        datetime_cols = []
        other_cols = []

        for col, dtype in self.dtypes.items():
            dtype_lower = dtype.lower()
            if 'int' in dtype_lower or 'float' in dtype_lower:
                numeric_cols.append(col)
            elif any(x in dtype_lower for x in ['object', 'string', 'str', 'category']):
                categorical_cols.append(col)
            elif 'datetime' in dtype_lower:
                datetime_cols.append(col)
            else:
                other_cols.append(col)

        return {
            "numeric": numeric_cols,
            "categorical": categorical_cols,
            "datetime": datetime_cols,
            "other": other_cols
        }

    def get_profile_summary(self) -> Dict[str, Any]:
        """Get comprehensive profile summary for agents"""
        info = self.get_info()
        missing_info = self.get_missing_info()
        cardinality_info = self.get_cardinality_info()
        column_types = self.get_column_types()

        # Find columns with high missing values
        high_missing_cols = [
            col for col, data in missing_info.items()
            if data["percentage"] > 40
        ]

        # Find high cardinality columns
        high_cardinality_cols = [
            col for col, data in cardinality_info.items()
            if data["is_high_cardinality"]
        ]

        return {
            "basic_info": {
                "rows": info["rows"],
                "columns": info["columns"],
                "file_size": info["file_size_formatted"],
                "mode": info["mode"]
            },
            "column_types": column_types,
            "missing_info": missing_info,
            "cardinality_info": cardinality_info,
            "issues": {
                "high_missing_cols": high_missing_cols,
                "high_cardinality_cols": high_cardinality_cols
            }
        }

    def __repr__(self) -> str:
        return f"DatasetHandle(path={self.path}, mode={self.mode}, shape={self.shape})"
