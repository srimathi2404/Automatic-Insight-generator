"""
Query Generation Agent - Iterative investigation with follow-up queries.
Takes analysis objectives and generates/executes queries with validation.
"""

from typing import List, Dict, Any, Optional
from data_explorer import DataExplorer
from query_helpers import QueryHelpers
from models import InvestigationType
import pandas as pd


class QueryGenerationAgent:
    """Agent for iterative query generation and execution."""

    def __init__(self, client, explorer):
        """Initialize with Trino client and data explorer."""
        self.client = client
        self.explorer = explorer
        self.helpers = QueryHelpers()
        self.query_history = []
        self.result_history = {}

    def investigate_objective(
        self,
        table: str,
        objective: str,
        investigation_type: InvestigationType,
        dimensions: List[str] = None,
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Conduct iterative investigation for an objective.
        
        Args:
            table: Target table
            objective: What to investigate (e.g., "Find top revenue sources")
            investigation_type: Type of analysis
            dimensions: Optional dimension columns
            metrics: Optional metric columns
            
        Returns:
            Dictionary with queries, results, and findings
        """
        print(f"\n{'='*70}")
        print(f"INVESTIGATING: {objective}")
        print(f"{'='*70}\n")

        results = {
            "objective": objective,
            "investigation_type": investigation_type.value,
            "queries": [],
            "results": [],
            "findings": []
        }

        # Generate initial query
        initial_query = self._generate_query(
            table, investigation_type, dimensions, metrics
        )
        
        if initial_query:
            print(f"[Query 1] Executing primary investigation...")
            result = self._execute_and_store(initial_query, table)
            results["queries"].append(initial_query)
            results["results"].append(result)

            # Analyze result for follow-ups
            finding = self._analyze_result(result, objective)
            results["findings"].append(finding)
            print(f"✓ Found: {finding['observation']}")

            # Generate follow-up queries if needed
            follow_ups = self._generate_followups(
                table, result, investigation_type, dimensions, metrics
            )

            for i, follow_up_query in enumerate(follow_ups, 2):
                print(f"\n[Query {i}] Validation query...")
                follow_up_result = self._execute_and_store(follow_up_query, table)
                results["queries"].append(follow_up_query)
                results["results"].append(follow_up_result)

                finding = self._analyze_result(follow_up_result, objective)
                results["findings"].append(finding)
                print(f"✓ Validated: {finding['observation']}")

        return results

    def _generate_query(
        self,
        table: str,
        investigation_type: InvestigationType,
        dimensions: List[str] = None,
        metrics: List[str] = None
    ) -> Optional[str]:
        """Generate query based on investigation type."""
        try:
            # Get schema if not provided
            if not dimensions or not metrics:
                classification = self.explorer.detect_dimensions_and_measures(table)
                if not dimensions:
                    dimensions = classification.get("dimensions", [])
                if not metrics:
                    metrics = classification.get("measures", [])
            
            if not metrics:
                return None

            dim = dimensions[0] if dimensions else None
            metric = metrics[0]
            dates = self.explorer.get_schema(table)

            # Generate query by type
            if investigation_type == InvestigationType.TREND:
                date_col = None
                for _, row in dates.iterrows():
                    if "date" in row.iloc[0].lower() or "time" in row.iloc[0].lower():
                        date_col = row.iloc[0]
                        break
                if date_col:
                    return self.helpers.trend_analysis(table, date_col, metric, "month")

            elif investigation_type == InvestigationType.SEGMENT and dim:
                return self.helpers.segment_distribution(table, dim, metric)

            elif investigation_type == InvestigationType.TOP_CONTRIBUTORS and dim:
                return self.helpers.top_n_by_metric(table, dim, metric, limit=20)

            elif investigation_type == InvestigationType.DISTRIBUTION:
                return self.helpers.numeric_column_stats(table, metric)

            elif investigation_type == InvestigationType.CORRELATION:
                if len(metrics) >= 2:
                    return self.helpers.correlation_check(table, metrics[0], metrics[1])

            elif investigation_type == InvestigationType.ANOMALY:
                return self.helpers.detect_outliers_zscore(table, metric, threshold=3.0)

        except Exception as e:
            print(f"Error generating query: {e}")

        return None

    def _generate_followups(
        self,
        table: str,
        primary_result: pd.DataFrame,
        investigation_type: InvestigationType,
        dimensions: List[str],
        metrics: List[str]
    ) -> List[str]:
        """Generate follow-up validation queries."""
        followups = []

        try:
            if len(primary_result) == 0:
                return followups

            # For segment analysis, drill into top segment
            if investigation_type == InvestigationType.SEGMENT and dimensions:
                top_value = primary_result.iloc[0, 0]
                if metrics:
                    # Drill down query
                    dim = dimensions[0]
                    metric = metrics[0]
                    drill_query = f"""
                    SELECT *
                    FROM {table}
                    WHERE {dim} = '{top_value}'
                    LIMIT 100
                    """
                    followups.append(drill_query)

            # For trend, check recent performance
            elif investigation_type == InvestigationType.TREND:
                if len(primary_result) > 1:
                    recent_query = f"""
                    SELECT *
                    FROM ({primary_result})
                    ORDER BY 1 DESC
                    LIMIT 3
                    """
                    # Simple validation of recent data
                    pass

            # For top contributors, check tail
            elif investigation_type == InvestigationType.TOP_CONTRIBUTORS and dimensions:
                if metrics:
                    dim = dimensions[0]
                    metric = metrics[0]
                    # Get bottom performers for contrast
                    tail_query = self.helpers.top_n_by_metric(table, dim, metric, limit=20)
                    followups.append(tail_query)

        except Exception as e:
            print(f"Error generating followups: {e}")

        return followups

    def _execute_and_store(self, query: str, table: str) -> pd.DataFrame:
        """Execute query and store for history."""
        try:
            result = self.client.run_query(query)
            self.query_history.append(query)
            self.result_history[table] = result
            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()

    def _analyze_result(self, result: pd.DataFrame, objective: str) -> Dict[str, str]:
        """Analyze query result and extract finding."""
        finding = {
            "observation": "No data available",
            "summary": "",
            "record_count": len(result)
        }

        if len(result) > 0:
            # Simple summary
            if len(result.columns) >= 2:
                col_name = result.columns[0]
                col_value = result.iloc[0, 0]
                finding["observation"] = f"Found {len(result)} records. Top value: {col_value}"
                finding["summary"] = f"Primary column has {len(result)} distinct values"
            else:
                finding["observation"] = f"Retrieved {len(result)} records"
                finding["summary"] = str(result.iloc[0, 0]) if len(result) > 0 else "No data"

        return finding

    def get_query_history(self) -> List[str]:
        """Get all executed queries."""
        return self.query_history

    def get_results(self, table: str) -> Optional[pd.DataFrame]:
        """Get results for a table."""
        return self.result_history.get(table)
