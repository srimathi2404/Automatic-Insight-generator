"""
Enhanced Trino client with streaming, batching, and query optimization.
Handles large datasets efficiently without memory issues.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from trino.auth import BasicAuthentication
from trino.sqlalchemy import URL
from typing import Iterator, Optional

from config import *


class TrinoClient:
    """Enhanced Trino client with streaming and optimization."""

    def __init__(self):
        """Initialize Trino connection."""
        url = URL(
            host=TRINO_HOST,
            port=TRINO_PORT
        )

        connect_args = {
            "auth": BasicAuthentication(
                TRINO_USER,
                TRINO_PASSWORD
            ),
            "http_scheme": "https",
            "verify": TRINO_CERT,
        }

        self.engine = create_engine(
            url,
            connect_args=connect_args
        )

    def run_query(self, sql: str) -> pd.DataFrame:
        """
        Execute query and return results as DataFrame.
        Use for small to medium results (<100K rows).
        """
        with self.engine.connect() as conn:
            return pd.read_sql(sql, conn)

    def run_query_streaming(
        self,
        sql: str,
        batch_size: int = 10000
    ) -> Iterator[pd.DataFrame]:
        """
        Stream query results in batches to handle large datasets.
        Memory usage stays constant regardless of result size.
        
        Args:
            sql: SQL query to execute
            batch_size: Rows per batch
            
        Yields:
            DataFrames with batch_size rows each
            
        Example:
            for batch in client.run_query_streaming("SELECT * FROM huge_table"):
                process(batch)  # Process each batch
        """
        with self.engine.connect() as conn:
            for chunk in pd.read_sql(sql, conn, chunksize=batch_size):
                yield chunk

    def run_query_aggregated(self, sql: str) -> pd.DataFrame:
        """
        Execute query assuming results are already aggregated at database.
        Optimized for GROUP BY queries where result size is manageable.
        
        Args:
            sql: SQL query (typically with aggregations)
            
        Returns:
            Complete result as DataFrame (safe for aggregated queries)
        """
        with self.engine.connect() as conn:
            return pd.read_sql(sql, conn)

    def execute_parameterized(
        self,
        sql: str,
        params: dict = None
    ) -> pd.DataFrame:
        """
        Execute parameterized query to prevent SQL injection.
        
        Args:
            sql: SQL query with :param placeholders
            params: Dictionary of parameter values
            
        Returns:
            Query result as DataFrame
            
        Example:
            result = client.execute_parameterized(
                "SELECT * FROM users WHERE id = :user_id",
                {"user_id": 123}
            )
        """
        with self.engine.connect() as conn:
            query = text(sql)
            return pd.read_sql(query, conn, params=params or {})

    def get_query_plan(self, sql: str) -> dict:
        """
        Get EXPLAIN plan for query optimization analysis.
        
        Args:
            sql: SQL query to analyze
            
        Returns:
            Dictionary with execution plan details
        """
        explain_sql = f"EXPLAIN {sql}"
        result = self.run_query(explain_sql)
        
        return {
            "query": sql,
            "plan": result.iloc[:, 0].tolist() if len(result) > 0 else [],
            "estimated_rows": self._extract_row_estimate(result)
        }

    def _extract_row_estimate(self, plan_df: pd.DataFrame) -> Optional[int]:
        """Extract estimated row count from EXPLAIN plan."""
        if len(plan_df) == 0:
            return None
        
        # Parse first row for row estimate (Trino specific)
        plan_text = plan_df.iloc[0, 0]
        if "rows" in str(plan_text).lower():
            try:
                # Simple extraction - can be enhanced
                return int(str(plan_text).split()[-1])
            except:
                pass
        
        return None

    def estimate_result_size(self, sql: str) -> dict:
        """
        Estimate query result size using EXPLAIN ANALYZE.
        
        Args:
            sql: SQL query to estimate
            
        Returns:
            Dictionary with size estimates
        """
        try:
            result = self.run_query(f"EXPLAIN ANALYZE {sql}")
            
            return {
                "query": sql,
                "plan_available": True,
                "details": result.iloc[:, 0].tolist() if len(result) > 0 else []
            }
        except Exception as e:
            return {
                "query": sql,
                "plan_available": False,
                "error": str(e)
            }

    def batch_insert(
        self,
        table: str,
        records: list,
        batch_size: int = 1000
    ) -> int:
        """
        Insert records in batches for better performance.
        
        Args:
            table: Target table name
            records: List of dictionaries
            batch_size: Records per batch
            
        Returns:
            Total records inserted
        """
        total_inserted = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batch_df = pd.DataFrame(batch)
            
            with self.engine.begin() as conn:
                batch_df.to_sql(
                    table,
                    conn,
                    if_exists='append',
                    index=False
                )
            
            total_inserted += len(batch)
        
        return total_inserted

    def close(self):
        """Close database connection."""
        self.engine.dispose()