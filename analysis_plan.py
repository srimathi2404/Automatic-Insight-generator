"""
Analysis plan generator for autonomous investigation strategy.
Inspects schema, understands business entities, and creates prioritized analysis plans.
"""

from typing import List, Dict, Optional, Set
from data_profiler import DatasetProfile, ColumnType
from models import Investigation, AnalysisPlan, InvestigationType


class AnalysisPlanGenerator:
    """Generates prioritized analysis plans based on dataset profiles."""

    def __init__(self, profiler, client):
        """Initialize with data profiler and Trino client."""
        self.profiler = profiler
        self.client = client

    def generate_plan(self, table_name: str) -> AnalysisPlan:
        """Generate comprehensive analysis plan for dataset."""
        
        # Profile the dataset
        profile = self.profiler.profile_dataset(table_name)

        # Understand business context
        business_entities = self._infer_business_entities(profile)
        dataset_type = self._infer_dataset_type(profile, business_entities)

        # Generate investigations
        investigations = self._generate_investigations(profile, business_entities)

        # Create plan
        plan = AnalysisPlan(
            table_name=table_name,
            dataset_type=dataset_type,
            business_entities=business_entities,
            key_metrics=profile.measures,
            key_dimensions=profile.dimensions,
            investigations=investigations,
            total_priority_score=sum(10 - inv.priority for inv in investigations)
        )

        return plan

    def _infer_business_entities(self, profile: DatasetProfile) -> List[str]:
        """Infer business entities from column names and structure."""
        entities = set()

        # Common entity keywords in column names
        entity_keywords = {
            "user": ["user", "customer", "account", "member", "person"],
            "product": ["product", "item", "sku", "offering", "service"],
            "transaction": ["transaction", "order", "sale", "purchase", "payment"],
            "region": ["region", "country", "state", "location", "territory"],
            "time": ["date", "time", "period", "month", "quarter", "year"],
            "event": ["event", "action", "activity", "impression", "click"],
            "campaign": ["campaign", "channel", "source", "medium", "source"],
        }

        col_names = " ".join([col.lower() for col in profile.columns.keys()])

        for entity, keywords in entity_keywords.items():
            if any(keyword in col_names for keyword in keywords):
                entities.add(entity)

        return sorted(list(entities))

    def _infer_dataset_type(self, profile: DatasetProfile, entities: List[str]) -> str:
        """Infer high-level dataset type."""
        
        if not profile.measures:
            return "categorical"
        
        if "time" in entities:
            if "transaction" in entities:
                return "transaction_time_series"
            elif "event" in entities:
                return "event_time_series"
            return "time_series"
        
        if "transaction" in entities:
            return "transaction"
        
        if "event" in entities:
            return "event"
        
        return "analytical"

    def _generate_investigations(
        self,
        profile: DatasetProfile,
        business_entities: List[str]
    ) -> List[Investigation]:
        """Generate prioritized list of investigations."""
        investigations = []
        priority = 1

        # 1. Trend analysis (if dates exist)
        if profile.dates and profile.measures:
            for date_col in profile.dates:
                for measure_col in profile.measures[:1]:  # Top measure
                    investigations.append(
                        Investigation(
                            type=InvestigationType.TREND,
                            title=f"{measure_col} trend over time",
                            description=f"Analyze how {measure_col} changes over {date_col}",
                            priority=priority,
                            expected_impact="high",
                            suggested_metrics=[measure_col],
                            suggested_dimensions=[date_col]
                        )
                    )
                    priority += 1

        # 2. Segment analysis (if dimensions and measures exist)
        if profile.dimensions and profile.measures:
            for dim_col in profile.dimensions[:2]:  # Top 2 dimensions
                for measure_col in profile.measures[:1]:
                    investigations.append(
                        Investigation(
                            type=InvestigationType.SEGMENT,
                            title=f"{measure_col} by {dim_col}",
                            description=f"Analyze {measure_col} across different {dim_col} segments",
                            priority=priority,
                            expected_impact="high",
                            suggested_metrics=[measure_col],
                            suggested_dimensions=[dim_col]
                        )
                    )
                    priority += 1

        # 3. Top contributors
        if profile.dimensions and profile.measures:
            for measure_col in profile.measures[:1]:
                for dim_col in profile.dimensions[:1]:
                    investigations.append(
                        Investigation(
                            type=InvestigationType.TOP_CONTRIBUTORS,
                            title=f"Top {dim_col} by {measure_col}",
                            description=f"Identify the top {dim_col} contributing to {measure_col}",
                            priority=priority,
                            expected_impact="high",
                            suggested_metrics=[measure_col],
                            suggested_dimensions=[dim_col]
                        )
                    )
                    priority += 1

        # 4. Distribution analysis (for high-cardinality measures)
        for measure_col_name, measure_col in profile.columns.items():
            if measure_col.column_type == ColumnType.MEASURE and measure_col.cardinality > 100:
                investigations.append(
                    Investigation(
                        type=InvestigationType.DISTRIBUTION,
                        title=f"Distribution of {measure_col_name}",
                        description=f"Analyze the distribution and statistics of {measure_col_name}",
                        priority=priority,
                        expected_impact="medium",
                        suggested_metrics=[measure_col_name]
                    )
                )
                priority += 1

        # 5. Correlation analysis (if multiple measures exist)
        if len(profile.measures) >= 2:
            for i, measure1 in enumerate(profile.measures[:2]):
                for measure2 in profile.measures[i + 1:i + 2]:
                    investigations.append(
                        Investigation(
                            type=InvestigationType.CORRELATION,
                            title=f"Correlation: {measure1} vs {measure2}",
                            description=f"Check if {measure1} and {measure2} are correlated",
                            priority=priority,
                            expected_impact="medium",
                            suggested_metrics=[measure1, measure2]
                        )
                    )
                    priority += 1

        # 6. Anomaly detection (for numeric columns)
        for col_name, col_profile in profile.columns.items():
            if col_profile.numeric_stats and col_profile.cardinality > 100:
                investigations.append(
                    Investigation(
                        type=InvestigationType.ANOMALY,
                        title=f"Anomalies in {col_name}",
                        description=f"Detect outliers and anomalies in {col_name}",
                        priority=priority,
                        expected_impact="medium",
                        suggested_metrics=[col_name]
                    )
                )
                priority += 1
                if priority > 10:  # Limit to top investigations
                    break

        # Sort by priority and return top investigations
        investigations.sort(key=lambda x: x.priority)
        return investigations[:10]  # Return top 10

    def get_investigation_query(
        self,
        profile: DatasetProfile,
        investigation: Investigation
    ) -> str:
        """Generate SQL query for an investigation."""
        from query_helpers import QueryHelpers
        
        helpers = QueryHelpers()
        table = profile.table_name
        
        if investigation.type == InvestigationType.TREND:
            metric = investigation.suggested_metrics[0] if investigation.suggested_metrics else profile.measures[0]
            date_col = investigation.suggested_dimensions[0] if investigation.suggested_dimensions else profile.dates[0]
            return helpers.trend_analysis(table, date_col, metric, period="month")
        
        elif investigation.type == InvestigationType.SEGMENT:
            metric = investigation.suggested_metrics[0] if investigation.suggested_metrics else profile.measures[0]
            dim = investigation.suggested_dimensions[0] if investigation.suggested_dimensions else profile.dimensions[0]
            return helpers.segment_distribution(table, dim, metric)
        
        elif investigation.type == InvestigationType.TOP_CONTRIBUTORS:
            metric = investigation.suggested_metrics[0] if investigation.suggested_metrics else profile.measures[0]
            dim = investigation.suggested_dimensions[0] if investigation.suggested_dimensions else profile.dimensions[0]
            return helpers.top_n_by_metric(table, dim, metric, limit=20)
        
        elif investigation.type == InvestigationType.DISTRIBUTION:
            metric = investigation.suggested_metrics[0] if investigation.suggested_metrics else profile.measures[0]
            return helpers.numeric_column_stats(table, metric)
        
        elif investigation.type == InvestigationType.CORRELATION:
            col1 = investigation.suggested_metrics[0] if len(investigation.suggested_metrics) > 0 else profile.measures[0]
            col2 = investigation.suggested_metrics[1] if len(investigation.suggested_metrics) > 1 else profile.measures[1]
            return helpers.correlation_check(table, col1, col2)
        
        elif investigation.type == InvestigationType.ANOMALY:
            metric = investigation.suggested_metrics[0] if investigation.suggested_metrics else profile.measures[0]
            return helpers.detect_outliers_zscore(table, metric, threshold=3.0)
        
        return ""

    def print_plan(self, plan: AnalysisPlan) -> None:
        """Pretty print analysis plan."""
        print(f"\n{'='*70}")
        print(f"ANALYSIS PLAN: {plan.table_name}")
        print(f"{'='*70}")
        
        if plan.dataset_type:
            print(f"\nDataset Type: {plan.dataset_type}")
        
        if plan.business_entities:
            print(f"Business Entities: {', '.join(plan.business_entities)}")
        
        if plan.key_metrics:
            print(f"Key Metrics: {', '.join(plan.key_metrics)}")
        
        if plan.key_dimensions:
            print(f"Key Dimensions: {', '.join(plan.key_dimensions)}")
        
        print(f"\n{'INVESTIGATIONS':-^70}")
        for i, investigation in enumerate(plan.investigations, 1):
            print(f"\n{i}. [{investigation.type.value.upper()}] {investigation.title}")
            print(f"   Priority: {investigation.priority} | Impact: {investigation.expected_impact}")
            print(f"   {investigation.description}")
