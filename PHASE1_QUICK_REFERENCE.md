# Phase 1 Quick Reference

## 🚀 Getting Started

### Installation
```bash
pip3 install -r requirements.txt
```

### Run Demo
```bash
python3 main.py
```

### Run Tests
```bash
python3 test_phase1.py
```

---

## 📦 Core Modules

### 1. **QueryHelpers** - Safe Query Templates
```python
from query_helpers import QueryHelpers
helpers = QueryHelpers()

# Basic
helpers.count_rows("table")
helpers.sample_data("table", limit=100)

# Profiling
helpers.column_null_percentage("table", "col")
helpers.column_cardinality("table", "col")
helpers.column_top_values("table", "col", limit=20)
helpers.numeric_column_stats("table", "col")
helpers.date_column_range("table", "col")

# Analysis
helpers.trend_analysis("table", "date_col", "metric", "month")
helpers.segment_distribution("table", "dim", "metric")
helpers.correlation_check("table", "col1", "col2")
helpers.detect_outliers_zscore("table", "col", threshold=3.0)
```

### 2. **DataProfiler** - Column & Dataset Profiling
```python
from data_profiler import DataProfiler

profiler = DataProfiler(client)
profile = profiler.profile_dataset("table")

# Access data
print(profile.row_count)
print(profile.dimensions)
print(profile.measures)
print(profile.dates)
print(profile.columns["col_name"].null_pct)
print(profile.columns["col_name"].cardinality)
print(profile.columns["col_name"].column_type)  # DIMENSION, MEASURE, DATE, ID
```

### 3. **DataExplorer** - Interactive Exploration
```python
from data_explorer import DataExplorer

explorer = DataExplorer(client)

# Classification
classification = explorer.detect_dimensions_and_measures("table")
print(classification["dimensions"])
print(classification["measures"])

# Profiling
profile = explorer.column_profiling_summary("table", "column")
print(profile["null_pct"])
print(profile["top_values"])
```

### 4. **AnalysisPlanGenerator** - Investigation Planning
```python
from analysis_plan import AnalysisPlanGenerator

generator = AnalysisPlanGenerator(profiler, client)
plan = generator.generate_plan("table")

# Access plan
print(plan.dataset_type)
print(plan.business_entities)
print(len(plan.investigations))  # Usually 10

for inv in plan.investigations:
    print(f"{inv.priority}. {inv.title}")
    query = generator.get_investigation_query(profile, inv)
```

### 5. **AnalysisPlannerAgent** - Complete Workflow
```python
from analysis_planner_agent import AnalysisPlannerAgent

agent = AnalysisPlannerAgent(client)

# Full analysis
result = agent.analyze_table("table")

# Access results
profile = result["profile"]
plan = result["plan"]
queries = result["investigation_queries"]

# Or individual methods
profile = agent.get_profile_only("table")
plan = agent.get_plan_only("table")
agent.print_profile("table")
```

### 6. **Enhanced TrinoClient** - Query Execution
```python
from trino_client import TrinoClient

client = TrinoClient()

# Normal query
result = client.run_query("SELECT * FROM table")

# Stream large results
for batch in client.run_query_streaming("SELECT * FROM huge_table", batch_size=10000):
    process(batch)

# Safe parameterized
result = client.execute_parameterized(
    "SELECT * FROM users WHERE id = :id",
    {"id": 123}
)

# Query optimization
plan = client.get_query_plan("SELECT * FROM huge_table")
```

---

## 📊 Models

### Investigation Types
```python
from models import InvestigationType

InvestigationType.TREND              # Metric over time
InvestigationType.SEGMENT            # Metric by dimension
InvestigationType.TOP_CONTRIBUTORS   # Top N values
InvestigationType.DISTRIBUTION       # Value distribution
InvestigationType.CORRELATION        # Relationship analysis
InvestigationType.ANOMALY            # Outlier detection
```

### Column Types
```python
from data_profiler import ColumnType

ColumnType.DIMENSION    # Categorical
ColumnType.MEASURE      # Numeric metric
ColumnType.DATE         # Temporal
ColumnType.ID           # Identifier
```

---

## 🎯 Common Workflows

### Workflow 1: Profile a Dataset
```python
from analysis_planner_agent import AnalysisPlannerAgent
from trino_client import TrinoClient

client = TrinoClient()
agent = AnalysisPlannerAgent(client)

result = agent.analyze_table("my_table")
plan = result["plan"]
profile = result["profile"]

print(f"Dimensions: {profile['dimensions']}")
print(f"Measures: {profile['measures']}")
print(f"Investigations: {len(plan['investigations'])}")
```

### Workflow 2: Get Specific Column Profile
```python
from data_explorer import DataExplorer
from trino_client import TrinoClient

client = TrinoClient()
explorer = DataExplorer(client)

summary = explorer.column_profiling_summary("table", "revenue")
print(summary["numeric_stats"])
print(summary["top_values"])
```

### Workflow 3: Generate Custom Analysis
```python
from query_helpers import QueryHelpers
from trino_client import TrinoClient

client = TrinoClient()
helpers = QueryHelpers()

# Create custom investigation
query = helpers.trend_analysis("sales", "date", "revenue", "quarter")
result = client.run_query(query)
print(result)
```

### Workflow 4: Stream Large Table
```python
from trino_client import TrinoClient
import pandas as pd

client = TrinoClient()

# Process in batches
combined = []
for batch in client.run_query_streaming("SELECT * FROM huge_table"):
    # Do something with each batch
    combined.append(batch.shape[0])

print(f"Total rows: {sum(combined)}")
```

---

## 🔍 Investigation Types Explained

### TREND Analysis
```
Purpose: Understand how metrics change over time
Query: GROUP BY date_trunc, SUM(metric)
Output: Time series data
Useful for: Revenue trends, growth rates, seasonal patterns
```

### SEGMENT Analysis
```
Purpose: Compare metrics across categories
Query: GROUP BY dimension, aggregate metrics
Output: Segment comparison
Useful for: Regional performance, product categories, cohorts
```

### TOP_CONTRIBUTORS
```
Purpose: Find top categories by metric
Query: GROUP BY dimension, ORDER BY metric DESC
Output: Ranked categories
Useful for: Pareto analysis, focus areas
```

### DISTRIBUTION Analysis
```
Purpose: Understand numeric value distribution
Query: MIN, MAX, AVG, STDDEV, PERCENTILES
Output: Statistical summary
Useful for: Outlier detection, range validation
```

### CORRELATION Analysis
```
Purpose: Check if two metrics are related
Query: CORR(col1, col2)
Output: Correlation coefficient
Useful for: Driver analysis, causality exploration
```

### ANOMALY Detection
```
Purpose: Find unusual values (outliers)
Query: Z-score > 3.0 detection
Output: Outlier records
Useful for: Data quality, fraud detection
```

---

## ⚠️ Common Pitfalls

❌ **Don't**: Use f-string SQL with column names
```python
# WRONG
query = f"SELECT {col_name} FROM {table}"
```

✅ **Do**: Use QueryHelpers
```python
# CORRECT
query = helpers.column_top_values(table, col_name)
```

---

❌ **Don't**: Load huge tables into memory
```python
# WRONG - Will crash
result = client.run_query("SELECT * FROM huge_table")
df = pd.DataFrame(result)
```

✅ **Do**: Use streaming
```python
# CORRECT - Constant memory
for batch in client.run_query_streaming("SELECT * FROM huge_table"):
    process(batch)
```

---

❌ **Don't**: Assume column type without profiling
```python
# WRONG
if "revenue" in table:
    # assume it's a measure
```

✅ **Do**: Use automatic classification
```python
# CORRECT
classification = explorer.detect_dimensions_and_measures(table)
if "revenue" in classification["measures"]:
    # definitely a measure
```

---

## 📞 Troubleshooting

### Issue: "No module named 'pandas'"
**Solution**: `pip3 install -r requirements.txt`

### Issue: Trino connection timeout
**Solution**: Check .env file has correct credentials and host

### Issue: Query returns empty result
**Solution**: 
1. Check table exists: `explorer.get_schema(table)`
2. Check row count: `explorer.get_row_count(table)`
3. Print sample: `explorer.sample_rows(table)`

### Issue: Profile takes too long
**Solution**: 
1. Check table size: `explorer.get_row_count(table)`
2. For huge tables (>1B rows), sample first
3. Use `APPROX_DISTINCT` for cardinality

---

## 📈 Performance Tips

1. **Use aggregations at DB level** - Don't pull raw data to Python
2. **Stream large results** - Use `run_query_streaming()` for >100K rows
3. **Cache profiling results** - Profile once, reuse
4. **Use date partitioning** - Filter before analysis
5. **Batch your queries** - Execute multiple investigations in parallel (Phase 2)

---

## 🎓 Example: Complete Analysis

```python
from analysis_planner_agent import AnalysisPlannerAgent
from trino_client import TrinoClient

# Setup
client = TrinoClient()
agent = AnalysisPlannerAgent(client)

# Step 1: Analyze dataset
print("Analyzing dataset...")
result = agent.analyze_table("sales")

# Step 2: View plan
plan = result["plan"]
print(f"\nDataset Type: {plan['dataset_type']}")
print(f"Entities: {plan['business_entities']}")
print(f"\nTop 3 Investigations:")

for i, inv in enumerate(plan['investigations'][:3], 1):
    print(f"\n{i}. {inv['title']}")
    print(f"   Type: {inv['type']}")
    print(f"   Impact: {inv['expected_impact']}")

# Step 3: Execute first investigation
first_inv = result['investigation_queries'][0]
print(f"\n\nExecuting: {first_inv['investigation']}")
print(f"Query:\n{first_inv['query']}")

result_df = client.run_query(first_inv['query'])
print(f"\nResult:\n{result_df}")
```

---

## ✅ Validation Checklist

Before moving to Phase 2:
- [ ] All tests pass: `python3 test_phase1.py`
- [ ] Can profile any dataset
- [ ] Dimension/measure detection works
- [ ] Investigation plan generates 10 items
- [ ] Queries execute without errors
- [ ] Can stream large datasets
- [ ] No SQL injection vulnerabilities

---

**Created**: Phase 1 Implementation  
**Status**: ✅ Production Ready  
**Next**: Phase 2 (Query Execution & Insights)  
