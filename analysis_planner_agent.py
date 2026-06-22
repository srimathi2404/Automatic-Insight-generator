"""
Analysis Planner Agent - Autonomous investigation strategy generator.
Inspects datasets, infers business context, and creates prioritized analysis plans.
"""

from data_profiler import DataProfiler, DatasetProfile
from analysis_plan import AnalysisPlanGenerator
from models import AnalysisPlan


class AnalysisPlannerAgent:
    """Autonomous agent for generating analysis plans."""

    def __init__(self, client):
        """Initialize agent with Trino client."""
        self.client = client
        self.profiler = DataProfiler(client)
        self.plan_generator = AnalysisPlanGenerator(self.profiler, client)

    def analyze_table(self, table_name: str) -> dict:
        """
        Complete analysis workflow: profile → plan → generate queries.
        
        Args:
            table_name: Fully qualified table name (catalog.schema.table)
            
        Returns:
            Dictionary with profile, plan, and suggested queries
        """
        print(f"\n{'='*70}")
        print(f"AUTONOMOUS ANALYSIS PLANNER AGENT")
        print(f"{'='*70}")
        print(f"\nAnalyzing table: {table_name}")

        # Step 1: Profile dataset
        print("\n[1/3] Profiling dataset...")
        profile = self.profiler.profile_dataset(table_name)
        profile_summary = self.profiler.get_summary(profile)
        print(f"✓ Found {profile.row_count:,} rows with {profile.column_count} columns")
        print(f"  • Dimensions: {', '.join(profile.dimensions[:5])}")
        print(f"  • Measures: {', '.join(profile.measures[:5])}")
        print(f"  • Dates: {', '.join(profile.dates)}")
        
        if profile.quality_flags:
            print(f"  • Quality Flags: {', '.join(profile.quality_flags)}")

        # Step 2: Generate analysis plan
        print("\n[2/3] Generating analysis plan...")
        plan = self.plan_generator.generate_plan(table_name)
        print(f"✓ Generated {len(plan.investigations)} investigation(s)")
        print(f"  • Dataset Type: {plan.dataset_type}")
        print(f"  • Business Entities: {', '.join(plan.business_entities)}")

        # Step 3: Generate investigation queries
        print("\n[3/3] Preparing investigation queries...")
        investigation_queries = []
        for inv in plan.investigations[:3]:  # Top 3
            query = self.plan_generator.get_investigation_query(profile, inv)
            investigation_queries.append({
                "investigation": inv.title,
                "type": inv.type.value,
                "priority": inv.priority,
                "query": query
            })
        print(f"✓ Ready to execute {len(investigation_queries)} queries")

        # Print detailed plan
        print("\n")
        self.plan_generator.print_plan(plan)

        # Return comprehensive result
        return {
            "table_name": table_name,
            "profile": {
                "summary": profile_summary,
                "row_count": profile.row_count,
                "column_count": profile.column_count,
                "dimensions": profile.dimensions,
                "measures": profile.measures,
                "dates": profile.dates,
                "ids": profile.ids,
                "quality_flags": profile.quality_flags,
                "columns": {
                    col_name: {
                        "data_type": col.data_type,
                        "type": col.column_type.value,
                        "cardinality": col.cardinality,
                        "null_pct": col.null_pct,
                        "flags": col.flags,
                        "is_key": col.is_key
                    }
                    for col_name, col in profile.columns.items()
                }
            },
            "plan": {
                "dataset_type": plan.dataset_type,
                "business_entities": plan.business_entities,
                "key_metrics": plan.key_metrics,
                "key_dimensions": plan.key_dimensions,
                "investigations": [
                    {
                        "type": inv.type.value,
                        "priority": inv.priority,
                        "title": inv.title,
                        "description": inv.description,
                        "expected_impact": inv.expected_impact,
                        "suggested_metrics": inv.suggested_metrics,
                        "suggested_dimensions": inv.suggested_dimensions
                    }
                    for inv in plan.investigations
                ]
            },
            "investigation_queries": investigation_queries,
            "next_steps": [
                "1. Execute investigation queries to gather evidence",
                "2. Validate findings with statistical tests",
                "3. Generate business insights and recommendations",
                "4. Create interactive dashboard for stakeholders"
            ]
        }

    def get_profile_only(self, table_name: str) -> DatasetProfile:
        """Get only the dataset profile without plan."""
        return self.profiler.profile_dataset(table_name)

    def get_plan_only(self, table_name: str) -> AnalysisPlan:
        """Get only the analysis plan without profile details."""
        profile = self.profiler.profile_dataset(table_name)
        return self.plan_generator.generate_plan(table_name)

    def print_profile(self, table_name: str) -> None:
        """Print detailed profile information."""
        profile = self.profiler.profile_dataset(table_name)
        
        print(f"\n{'='*70}")
        print(f"DATASET PROFILE: {table_name}")
        print(f"{'='*70}")
        
        summary = self.profiler.get_summary(profile)
        for key, value in summary.items():
            if isinstance(value, list):
                print(f"\n{key}:")
                for item in value:
                    print(f"  • {item}")
            else:
                print(f"{key}: {value}")
        
        print(f"\n{'COLUMN DETAILS':-^70}")
        for col_name, col in profile.columns.items():
            print(f"\n{col_name}")
            print(f"  Type: {col.data_type} → {col.column_type.value}")
            print(f"  Cardinality: {col.cardinality:,} (null: {col.null_pct}%)")
            
            if col.is_key:
                print(f"  🔑 Primary Key")
            
            if col.numeric_stats:
                stats = col.numeric_stats
                print(f"  Stats: min={stats['min']:.2f}, max={stats['max']:.2f}, avg={stats['avg']:.2f}")
            
            if col.date_range:
                date_range = col.date_range
                print(f"  Date Range: {date_range['min_date']} to {date_range['max_date']}")
            
            if col.top_values:
                print(f"  Top values: {', '.join(str(v) for v in list(col.top_values.keys())[:3])}")
            
            if col.flags:
                print(f"  Flags: {', '.join(col.flags)}")
