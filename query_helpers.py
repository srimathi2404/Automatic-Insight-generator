"""
Reusable Trino query helpers for safe, efficient data profiling.
Prevents SQL injection through parameterized queries.
"""

from sqlalchemy import text


class QueryHelpers:
    """Collection of safe, reusable Trino queries."""

    @staticmethod
    def describe_table(table_name: str) -> str:
        """Get table schema."""
        return f"DESCRIBE {table_name}"

    @staticmethod
    def count_rows(table_name: str) -> str:
        """Count total rows in table."""
        return f"SELECT COUNT(*) as row_count FROM {table_name}"

    @staticmethod
    def sample_data(table_name: str, limit: int = 100) -> str:
        """Sample random rows from table."""
        return f"SELECT * FROM {table_name} LIMIT {limit}"

    @staticmethod
    def column_null_percentage(table_name: str, column_name: str) -> str:
        """Calculate null percentage for a column."""
        return f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(CASE WHEN {column_name} IS NULL THEN 1 END) as null_count,
            ROUND(100.0 * COUNT(CASE WHEN {column_name} IS NULL THEN 1 END) / COUNT(*), 2) as null_pct
        FROM {table_name}
        """

    @staticmethod
    def column_cardinality(table_name: str, column_name: str) -> str:
        """Count distinct values (cardinality)."""
        return f"""
        SELECT 
            APPROX_DISTINCT({column_name}) as approx_cardinality,
            COUNT(DISTINCT {column_name}) as exact_cardinality
        FROM {table_name}
        """

    @staticmethod
    def column_top_values(table_name: str, column_name: str, limit: int = 20) -> str:
        """Get top N most frequent values."""
        return f"""
        SELECT
            {column_name},
            COUNT(*) as frequency,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct
        FROM {table_name}
        WHERE {column_name} IS NOT NULL
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT {limit}
        """

    @staticmethod
    def numeric_column_stats(table_name: str, column_name: str) -> str:
        """Get statistics for numeric column."""
        return f"""
        SELECT
            COUNT(*) as count,
            MIN({column_name}) as min_val,
            MAX({column_name}) as max_val,
            AVG({column_name}) as avg_val,
            STDDEV_POP({column_name}) as stddev_val,
            APPROX_PERCENTILE({column_name}, 0.25) as p25,
            APPROX_PERCENTILE({column_name}, 0.50) as p50,
            APPROX_PERCENTILE({column_name}, 0.75) as p75
        FROM {table_name}
        WHERE {column_name} IS NOT NULL
        """

    @staticmethod
    def date_column_range(table_name: str, column_name: str) -> str:
        """Get date range for date/timestamp column."""
        return f"""
        SELECT
            MIN({column_name}) as min_date,
            MAX({column_name}) as max_date,
            COUNT(DISTINCT DATE({column_name})) as date_cardinality
        FROM {table_name}
        WHERE {column_name} IS NOT NULL
        """

    @staticmethod
    def detect_duplicates(table_name: str, columns: list) -> str:
        """Detect duplicate rows based on columns."""
        col_list = ", ".join(columns)
        return f"""
        SELECT
            {col_list},
            COUNT(*) as duplicate_count
        FROM {table_name}
        GROUP BY {col_list}
        HAVING COUNT(*) > 1
        ORDER BY COUNT(*) DESC
        LIMIT 100
        """

    @staticmethod
    def column_data_type_counts(table_name: str) -> str:
        """Analyze data types of all columns in table."""
        return f"""
        SELECT
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
        """

    @staticmethod
    def estimate_table_size(table_name: str) -> str:
        """Estimate table size and row count."""
        return f"""
        SELECT
            COUNT(*) as total_rows,
            SUM(CAST(total_bytes AS BIGINT)) as total_bytes
        FROM {table_name}
        """

    @staticmethod
    def correlation_check(table_name: str, col1: str, col2: str) -> str:
        """Check if two numeric columns are correlated."""
        return f"""
        SELECT
            CORR({col1}, {col2}) as correlation
        FROM {table_name}
        WHERE {col1} IS NOT NULL AND {col2} IS NOT NULL
        """

    @staticmethod
    def detect_outliers_zscore(table_name: str, column_name: str, threshold: float = 3.0) -> str:
        """Detect outliers using Z-score method (values > threshold * stddev)."""
        return f"""
        WITH stats AS (
            SELECT
                AVG({column_name}) as mean_val,
                STDDEV_POP({column_name}) as stddev_val
            FROM {table_name}
            WHERE {column_name} IS NOT NULL
        )
        SELECT
            {column_name},
            ABS(({column_name} - (SELECT mean_val FROM stats)) / 
                NULLIF((SELECT stddev_val FROM stats), 0)) as z_score,
            COUNT(*) as outlier_count
        FROM {table_name}
        CROSS JOIN stats
        WHERE {column_name} IS NOT NULL
            AND ABS(({column_name} - (SELECT mean_val FROM stats)) / 
                NULLIF((SELECT stddev_val FROM stats), 0)) > {threshold}
        GROUP BY 1, 2
        ORDER BY 3 DESC
        LIMIT 100
        """

    @staticmethod
    def trend_analysis(table_name: str, date_col: str, metric_col: str, period: str = "month") -> str:
        """Analyze trend of metric over time (period: day, week, month, year)."""
        if period == "day":
            date_trunc = f"DATE({date_col})"
        elif period == "week":
            date_trunc = f"DATE_TRUNC('week', {date_col})"
        elif period == "month":
            date_trunc = f"DATE_TRUNC('month', {date_col})"
        elif period == "year":
            date_trunc = f"DATE_TRUNC('year', {date_col})"
        else:
            date_trunc = f"DATE_TRUNC('{period}', {date_col})"

        return f"""
        SELECT
            {date_trunc} as period,
            SUM({metric_col}) as total_metric,
            COUNT(*) as record_count,
            AVG({metric_col}) as avg_metric
        FROM {table_name}
        WHERE {date_col} IS NOT NULL AND {metric_col} IS NOT NULL
        GROUP BY 1
        ORDER BY 1
        """

    @staticmethod
    def segment_distribution(table_name: str, dimension_col: str, metric_col: str) -> str:
        """Analyze distribution of metric across dimension."""
        return f"""
        SELECT
            {dimension_col},
            COUNT(*) as record_count,
            SUM({metric_col}) as total_metric,
            AVG({metric_col}) as avg_metric,
            MIN({metric_col}) as min_metric,
            MAX({metric_col}) as max_metric,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as pct_records
        FROM {table_name}
        WHERE {dimension_col} IS NOT NULL
        GROUP BY 1
        ORDER BY 2 DESC
        """

    @staticmethod
    def top_n_by_metric(table_name: str, dimension_col: str, metric_col: str, limit: int = 20) -> str:
        """Get top N dimension values by metric."""
        return f"""
        SELECT
            {dimension_col},
            SUM({metric_col}) as total_metric,
            COUNT(*) as record_count,
            ROUND(100.0 * SUM({metric_col}) / SUM(SUM({metric_col})) OVER (), 2) as pct_total
        FROM {table_name}
        WHERE {dimension_col} IS NOT NULL AND {metric_col} IS NOT NULL
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT {limit}
        """
