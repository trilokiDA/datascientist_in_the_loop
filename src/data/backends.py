from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
import duckdb
from pathlib import Path


class DataBackend(ABC):
    """Abstract base class for data backends"""

    @abstractmethod
    def get_shape(self) -> tuple[int, int]:
        """Get (rows, columns) shape"""
        pass

    @abstractmethod
    def get_dtypes(self) -> Dict[str, str]:
        """Get column data types"""
        pass

    @abstractmethod
    def get_column_names(self) -> List[str]:
        """Get list of column names"""
        pass

    @abstractmethod
    def describe(self) -> pd.DataFrame:
        """Get statistical summary"""
        pass

    @abstractmethod
    def get_missing_counts(self) -> Dict[str, int]:
        """Get missing value counts per column"""
        pass

    @abstractmethod
    def get_unique_counts(self) -> Dict[str, int]:
        """Get unique value counts per column"""
        pass

    @abstractmethod
    def sample(self, n: int) -> pd.DataFrame:
        """Get random sample of n rows"""
        pass

    @abstractmethod
    def head(self, n: int = 5) -> pd.DataFrame:
        """Get first n rows"""
        pass

    @abstractmethod
    def get_dataframe(self) -> pd.DataFrame:
        """Get full dataframe (use with caution for large datasets)"""
        pass


class InMemoryBackend(DataBackend):
    """Pandas-based backend for in-memory datasets"""

    def __init__(self, path: str):
        self.path = path
        self.df = pd.read_csv(path)

    def get_shape(self) -> tuple[int, int]:
        return self.df.shape

    def get_dtypes(self) -> Dict[str, str]:
        return {col: str(dtype) for col, dtype in self.df.dtypes.items()}

    def get_column_names(self) -> List[str]:
        return self.df.columns.tolist()

    def describe(self) -> pd.DataFrame:
        return self.df.describe(include='all')

    def get_missing_counts(self) -> Dict[str, int]:
        return self.df.isnull().sum().to_dict()

    def get_unique_counts(self) -> Dict[str, int]:
        return {col: self.df[col].nunique() for col in self.df.columns}

    def sample(self, n: int) -> pd.DataFrame:
        n = min(n, len(self.df))
        return self.df.sample(n=n, random_state=42)

    def head(self, n: int = 5) -> pd.DataFrame:
        return self.df.head(n)

    def get_dataframe(self) -> pd.DataFrame:
        return self.df


class SampledBackend(DataBackend):
    """DuckDB-based backend for large datasets with sampling"""

    def __init__(self, path: str, sample_size: int = 100_000):
        self.path = path
        self.sample_size = sample_size
        self.conn = duckdb.connect(':memory:')

        # Create view of the CSV
        self.table_name = 'dataset'
        self.conn.execute(f"""
            CREATE VIEW {self.table_name} AS
            SELECT * FROM read_csv_auto('{path}')
        """)

        # Cache shape
        self._shape = self._compute_shape()

        # Create sample for profiling
        self._sample_df = self._create_sample()

    def _compute_shape(self) -> tuple[int, int]:
        rows = self.conn.execute(f"SELECT COUNT(*) FROM {self.table_name}").fetchone()[0]
        cols = len(self.conn.execute(f"DESCRIBE {self.table_name}").fetchall())
        return (rows, cols)

    def _create_sample(self) -> pd.DataFrame:
        """Create stratified sample for profiling"""
        sample_size = min(self.sample_size, self._shape[0])
        query = f"""
            SELECT * FROM {self.table_name}
            USING SAMPLE {sample_size} ROWS
        """
        return self.conn.execute(query).df()

    def get_shape(self) -> tuple[int, int]:
        return self._shape

    def get_dtypes(self) -> Dict[str, str]:
        return {col: str(dtype) for col, dtype in self._sample_df.dtypes.items()}

    def get_column_names(self) -> List[str]:
        return self._sample_df.columns.tolist()

    def describe(self) -> pd.DataFrame:
        """Describe based on sample"""
        return self._sample_df.describe(include='all')

    def get_missing_counts(self) -> Dict[str, int]:
        """Estimate missing counts from sample, extrapolate to full dataset"""
        sample_missing = self._sample_df.isnull().sum()
        ratio = self._shape[0] / len(self._sample_df)
        return {col: int(count * ratio) for col, count in sample_missing.items()}

    def get_unique_counts(self) -> Dict[str, int]:
        """Unique counts from sample (approximate)"""
        return {col: self._sample_df[col].nunique() for col in self._sample_df.columns}

    def sample(self, n: int) -> pd.DataFrame:
        n = min(n, self._shape[0])
        query = f"""
            SELECT * FROM {self.table_name}
            USING SAMPLE {n} ROWS
        """
        return self.conn.execute(query).df()

    def head(self, n: int = 5) -> pd.DataFrame:
        query = f"SELECT * FROM {self.table_name} LIMIT {n}"
        return self.conn.execute(query).df()

    def get_dataframe(self) -> pd.DataFrame:
        """WARNING: Loads full dataset into memory"""
        return self.conn.execute(f"SELECT * FROM {self.table_name}").df()

    def __del__(self):
        """Clean up connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
