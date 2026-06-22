"""
Enhanced DataExplorer with comprehensive profiling and dimension/measure detection.
"""

from query_helpers import QueryHelpers


class DataExplorer:
    """Enhanced data exploration with profiling and classification."""

    def __init__(self, client):
        self.client = client
        self.query_helpers = QueryHelpers()

    def get_schema(self, table):
        """Get table schema (column names and types)."""
        sql = f"DESCRIBE {table}"
        return self.client.run_query(sql)

    def get_row_count(self, table):
        """Get total row count."""
        sql = self.query_helpers.count_rows(table)
        return self.client.run_query(sql)

    def sample_rows(self, table, limit=20):
        """Get random sample of rows."""
        sql = self.query_helpers.sample_data(table, limit)
        return self.client.run_query(sql)

    def distinct_count(self, table, column):
        """Get distinct count for column."""
        sql = self.query_helpers.column_cardinality(table, column)
        return self.client.run_query(sql)

    def top_values(self, table, column, limit=20):
        """Get top N most frequent values."""
        sql = self.query_helpers.column_top_values(table, column, limit)
        return self.client.run_query(sql)

    def numeric_summary(self, table, column):
        """Get summary statistics for numeric column."""
        sql = self.query_helpers.numeric_column_stats(table, column)
        return self.client.run_query(sql)

    def column_null_stats(self, table, column):
        """Get null percentage for column."""
        sql = self.query_helpers.column_null_percentage(table, column)
        return self.client.run_query(sql)

    def date_range(self, table, column):
        """Get date range for date/timestamp column."""
        sql = self.query_helpers.date_column_range(table, column)
        return self.client.run_query(sql)

    def profile_table(self, table):
        """Get comprehensive table profile (quick version)."""
        row_count = self.get_row_count(table)
        schema = self.get_schema(table)
        sample = self.sample_rows(table, limit=10)
        
        return {
            "table": table,
            "row_count": row_count.iloc[0, 0] if len(row_count) > 0 else 0,
            "column_count": len(schema),
            "schema": schema,
            "sample": sample
        }

    def detect_dimensions_and_measures(self, table):
        """Classify columns as dimensions vs measures."""
        schema = self.get_schema(table)
        dimensions = []
        measures = []
        dates = []
        ids = []
        
        for _, row in schema.iterrows():
            col_name = row.iloc[0]
            col_type = row.iloc[1]
            col_lower = col_name.lower()
            type_lower = col_type.lower()
            
            # ID detection
            if "id" in col_lower or "key" in col_lower:
                ids.append(col_name)
            # Date detection
            elif "timestamp" in type_lower or "date" in type_lower:
                dates.append(col_name)
            # Numeric = measure
            elif any(x in type_lower for x in ["int", "float", "double", "decimal", "numeric"]):
                measures.append(col_name)
            # Everything else = dimension
            else:
                dimensions.append(col_name)
        
        return {
            "dimensions": dimensions,
            "measures": measures,
            "dates": dates,
            "ids": ids
        }

    def column_profiling_summary(self, table, column):
        """Get comprehensive profile for single column."""
        schema = self.get_schema(table)
        col_type = None
        
        for _, row in schema.iterrows():
            if row.iloc[0] == column:
                col_type = row.iloc[1]
                break
        
        if col_type is None:
            return {"error": f"Column {column} not found"}
        
        result = {
            "column": column,
            "data_type": col_type
        }
        
        # Null stats
        null_stats = self.column_null_stats(table, column)
        if len(null_stats) > 0:
            result["total_rows"] = null_stats.iloc[0, 0]
            result["null_count"] = null_stats.iloc[0, 1]
            result["null_pct"] = null_stats.iloc[0, 2]
        
        # Cardinality
        card_stats = self.distinct_count(table, column)
        if len(card_stats) > 0:
            result["cardinality"] = card_stats.iloc[0, 1]
        
        # Top values
        top_vals = self.top_values(table, column, limit=5)
        if len(top_vals) > 0:
            result["top_values"] = dict(zip(top_vals.iloc[:, 0], top_vals.iloc[:, 1]))
        
        # Numeric stats if applicable
        if any(x in col_type.lower() for x in ["int", "float", "double", "decimal"]):
            num_stats = self.numeric_summary(table, column)
            if len(num_stats) > 0:
                result["numeric_stats"] = {
                    "min": num_stats.iloc[0, 1],
                    "max": num_stats.iloc[0, 2],
                    "avg": num_stats.iloc[0, 3]
                }
        
        # Date range if applicable
        if "date" in col_type.lower() or "timestamp" in col_type.lower():
            date_stats = self.date_range(table, column)
            if len(date_stats) > 0:
                result["date_range"] = {
                    "min": str(date_stats.iloc[0, 0]),
                    "max": str(date_stats.iloc[0, 1])
                }
        
        return result