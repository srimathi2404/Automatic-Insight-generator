"""
Comprehensive data profiling engine for autonomous analysis.
Profiles columns, detects dimensions/measures, and generates metadata.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import pandas as pd

from query_helpers import QueryHelpers


class ColumnType(Enum):
    """Classification of column types."""
    DIMENSION = "dimension"
    MEASURE = "measure"
    DATE = "date"
    ID = "id"
    CATEGORICAL = "categorical"
    NUMERIC = "numeric"
    UNKNOWN = "unknown"


@dataclass
class ColumnProfile:
    """Profile of a single column."""
    name: str
    data_type: str
    column_type: ColumnType
    null_count: int
    null_pct: float
    cardinality: int
    approx_cardinality: int
    sample_values: List[Any] = None
    top_values: Dict[Any, int] = None
    is_unique: bool = False
    is_key: bool = False
    numeric_stats: Optional[Dict[str, float]] = None
    date_range: Optional[Dict[str, str]] = None
    flags: List[str] = None

    def __post_init__(self):
        if self.sample_values is None:
            self.sample_values = []
        if self.top_values is None:
            self.top_values = {}
        if self.flags is None:
            self.flags = []


@dataclass
class DatasetProfile:
    """Complete profile of a dataset."""
    table_name: str
    row_count: int
    column_count: int
    columns: Dict[str, ColumnProfile]
    dimensions: List[str]
    measures: List[str]
    dates: List[str]
    ids: List[str]
    estimated_size_bytes: int = 0
    quality_flags: List[str] = None
    business_entities: List[str] = None

    def __post_init__(self):
        if self.quality_flags is None:
            self.quality_flags = []
        if self.business_entities is None:
            self.business_entities = []


class DataProfiler:
    """Autonomous data profiling engine."""

    def __init__(self, client):
        """Initialize profiler with Trino client."""
        self.client = client
        self.query_helpers = QueryHelpers()

    def profile_dataset(self, table_name: str) -> DatasetProfile:
        """Create comprehensive profile of entire dataset."""
        
        # Get basic info
        schema_df = self.client.run_query(self.query_helpers.describe_table(table_name))
        row_count = self.client.run_query(self.query_helpers.count_rows(table_name))
        row_count = row_count.iloc[0, 0] if len(row_count) > 0 else 0

        # Profile each column
        columns = {}
        dimensions = []
        measures = []
        dates = []
        ids = []

        for _, row in schema_df.iterrows():
            col_name = row.iloc[0]
            col_type = row.iloc[1]
            
            column_profile = self._profile_column(table_name, col_name, col_type)
            columns[col_name] = column_profile

            # Classify column
            if column_profile.column_type == ColumnType.DIMENSION:
                dimensions.append(col_name)
            elif column_profile.column_type == ColumnType.MEASURE:
                measures.append(col_name)
            elif column_profile.column_type == ColumnType.DATE:
                dates.append(col_name)
            elif column_profile.column_type == ColumnType.ID:
                ids.append(col_name)

        # Create dataset profile
        dataset_profile = DatasetProfile(
            table_name=table_name,
            row_count=row_count,
            column_count=len(columns),
            columns=columns,
            dimensions=dimensions,
            measures=measures,
            dates=dates,
            ids=ids
        )

        # Detect quality flags
        dataset_profile.quality_flags = self._detect_quality_issues(dataset_profile)

        return dataset_profile

    def _profile_column(self, table_name: str, column_name: str, data_type: str) -> ColumnProfile:
        """Profile a single column."""
        
        # Get null stats
        null_df = self.client.run_query(
            self.query_helpers.column_null_percentage(table_name, column_name)
        )
        total_rows = null_df.iloc[0, 0]
        null_count = null_df.iloc[0, 1] if len(null_df) > 0 else 0
        null_pct = null_df.iloc[0, 2] if len(null_df) > 0 else 0.0

        # Get cardinality
        card_df = self.client.run_query(
            self.query_helpers.column_cardinality(table_name, column_name)
        )
        approx_cardinality = card_df.iloc[0, 0] if len(card_df) > 0 else 0
        exact_cardinality = card_df.iloc[0, 1] if len(card_df) > 0 else 0

        # Classify column
        column_type = self._classify_column(
            column_name, data_type, total_rows, exact_cardinality, null_pct
        )

        # Get top values (sample)
        top_df = self.client.run_query(
            self.query_helpers.column_top_values(table_name, column_name, limit=10)
        )
        top_values = dict(zip(top_df.iloc[:, 0], top_df.iloc[:, 1])) if len(top_df) > 0 else {}

        # Get numeric stats if applicable
        numeric_stats = None
        if "int" in data_type.lower() or "float" in data_type.lower() or "double" in data_type.lower():
            try:
                num_df = self.client.run_query(
                    self.query_helpers.numeric_column_stats(table_name, column_name)
                )
                if len(num_df) > 0:
                    numeric_stats = {
                        "min": num_df.iloc[0, 1],
                        "max": num_df.iloc[0, 2],
                        "avg": num_df.iloc[0, 3],
                        "stddev": num_df.iloc[0, 4],
                        "p25": num_df.iloc[0, 5],
                        "p50": num_df.iloc[0, 6],
                        "p75": num_df.iloc[0, 7],
                    }
            except:
                pass

        # Get date range if applicable
        date_range = None
        if "timestamp" in data_type.lower() or "date" in data_type.lower():
            try:
                date_df = self.client.run_query(
                    self.query_helpers.date_column_range(table_name, column_name)
                )
                if len(date_df) > 0:
                    date_range = {
                        "min_date": str(date_df.iloc[0, 0]),
                        "max_date": str(date_df.iloc[0, 1]),
                        "date_cardinality": date_df.iloc[0, 2],
                    }
            except:
                pass

        # Detect flags
        flags = self._detect_column_flags(
            column_name, total_rows, exact_cardinality, null_pct
        )

        return ColumnProfile(
            name=column_name,
            data_type=data_type,
            column_type=column_type,
            null_count=null_count,
            null_pct=null_pct,
            cardinality=exact_cardinality,
            approx_cardinality=approx_cardinality,
            top_values=top_values,
            is_unique=(exact_cardinality == total_rows),
            is_key=(exact_cardinality == total_rows and null_pct == 0),
            numeric_stats=numeric_stats,
            date_range=date_range,
            flags=flags
        )

    def _classify_column(
        self,
        column_name: str,
        data_type: str,
        total_rows: int,
        cardinality: int,
        null_pct: float
    ) -> ColumnType:
        """Classify column as dimension, measure, date, or id."""
        
        col_lower = column_name.lower()
        type_lower = data_type.lower()

        # ID detection
        if "id" in col_lower or "key" in col_lower:
            return ColumnType.ID

        # Date detection
        if "timestamp" in type_lower or "date" in type_lower:
            return ColumnType.DATE

        # Numeric detection
        if any(x in type_lower for x in ["int", "float", "double", "decimal", "numeric"]):
            # High cardinality numeric = measure
            if cardinality > 100 or cardinality > (total_rows * 0.5):
                return ColumnType.MEASURE
            else:
                return ColumnType.DIMENSION

        # Low cardinality categorical = dimension
        if cardinality < min(100, total_rows * 0.1):
            return ColumnType.DIMENSION

        # Default to dimension for other types
        return ColumnType.DIMENSION

    def _detect_column_flags(
        self,
        column_name: str,
        total_rows: int,
        cardinality: int,
        null_pct: float
    ) -> List[str]:
        """Detect data quality flags for column."""
        flags = []

        if null_pct == 100:
            flags.append("all_null")
        elif null_pct > 50:
            flags.append("high_null_rate")
        elif null_pct > 0:
            flags.append("has_nulls")

        if cardinality == total_rows:
            flags.append("unique_values")

        if cardinality == 1:
            flags.append("single_value")

        return flags

    def _detect_quality_issues(self, dataset_profile: DatasetProfile) -> List[str]:
        """Detect overall data quality issues."""
        flags = []

        if dataset_profile.row_count == 0:
            flags.append("empty_table")

        # Count columns with high null rates
        high_null_cols = [
            col for col, profile in dataset_profile.columns.items()
            if profile.null_pct > 50
        ]
        if len(high_null_cols) > len(dataset_profile.columns) * 0.5:
            flags.append("many_columns_with_high_nulls")

        # Check for imbalance
        if len(dataset_profile.measures) == 0:
            flags.append("no_measures_detected")

        if len(dataset_profile.dimensions) == 0:
            flags.append("no_dimensions_detected")

        return flags

    def get_summary(self, profile: DatasetProfile) -> Dict[str, Any]:
        """Get human-readable summary of profile."""
        return {
            "table": profile.table_name,
            "rows": profile.row_count,
            "columns": profile.column_count,
            "dimensions": profile.dimensions,
            "measures": profile.measures,
            "dates": profile.dates,
            "ids": profile.ids,
            "quality_flags": profile.quality_flags,
            "estimated_size_mb": profile.estimated_size_bytes / (1024 * 1024)
        }
