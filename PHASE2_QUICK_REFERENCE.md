# Phase 2 Quick Reference - Insights & Dashboard

## Components Overview

### 1. Query Generation Agent
**File:** `query_generation_agent.py`  
**Purpose:** Iteratively generate and execute analysis queries

```python
from query_generation_agent import QueryGenerationAgent
from models import InvestigationType

agent = QueryGenerationAgent(client, explorer)
results = agent.investigate_objective(
    table="users",
    objective="Find top spending customers",
    investigation_type=InvestigationType.TOP_CONTRIBUTORS,
    dimensions=["customer_id"],
    metrics=["spending"]
)

# Results include:
# - queries: List of generated SQL queries
# - results: List of DataFrames
# - findings: Structured findings from each query
```

### 2. Insight Generator
**File:** `insight_generator.py`  
**Purpose:** Extract business insights from query results

```python
from insight_generator import InsightGenerator
from models import InvestigationType

generator = InsightGenerator()

# Generate insights for investigation findings
insights = generator.generate_insights(
    findings=[{...}],
    investigation_type=InvestigationType.TOP_CONTRIBUTORS,
    objective="Analyze customer segments",
    result_data=df
)

# Generate executive summary
summary = generator.generate_executive_summary(insights)
# Returns: {
#   "total_insights": 5,
#   "high_confidence": 3,
#   "medium_confidence": 2,
#   "key_findings": [...],
#   "recommendations": [...],
#   "risks": [...],
#   "opportunities": [...]
# }
```

### 3. Dashboard Generator
**File:** `dashboard_generator.py`  
**Purpose:** Create dashboard specifications from insights and results

```python
from dashboard_generator import DashboardGenerator

generator = DashboardGenerator()

dashboard = generator.generate(
    insights=insights_list,
    metrics={
        "total_revenue": {"value": 1000000, "change": 15, "unit": "$"},
        "customer_count": {"value": 5000, "change": -5, "unit": ""}
    },
    query_results=[df1, df2],
    executive_summary=summary
)

# Export dashboard
generator.export_html(dashboard, "report.html")
generator.export_json(dashboard, "report.json")
```

## Investigation Types

All investigation types are available via `InvestigationType` enum:

| Type | Purpose | Insight Focus | Use Case |
|------|---------|---------------|----------|
| TREND | Time-series analysis | Directional change % | Sales over time |
| SEGMENT | Group analysis | Performance patterns | Customer segments |
| TOP_CONTRIBUTORS | Ranking analysis | 80/20 Pareto principle | Top products/regions |
| DISTRIBUTION | Statistical analysis | Range & averages | Data distribution |
| ANOMALY | Outlier detection | Exceptions | Quality checks |
| CORRELATION | Relationship analysis | Variable relationships | Dependency analysis |

## Insight Structure

Each `Insight` object contains:

```python
class Insight:
    title: str                      # "Top Contributors Analysis"
    observation: str                # "Top 3 represent 80% of value"
    evidence: str                   # "Data shows clear concentration"
    impact: str                     # "Affects allocation strategy"
    recommendation: str             # "Prioritize top 3-5"
    confidence: str                 # "high" | "medium" | "low"
    investigation_type: str         # Type of analysis
```

## Dashboard Specification

Generated dashboard includes:

```python
{
    "title": "Data Analytics Dashboard",
    "version": "1.0",
    "kpi_cards": [
        {
            "title": "Revenue",
            "value": "1000000",
            "trend": "↑",
            "unit": "$",
            "status": "positive"
        },
        ...
    ],
    "tables": [
        {
            "id": "table_0",
            "title": "Results Table 1",
            "row_count": 3,
            "columns": ["segment", "revenue"],
            "data": [...],
            "summary": { "total_rows": 3, ... }
        },
        ...
    ],
    "insights": [
        {
            "title": "Segment Analysis",
            "observation": "...",
            "evidence": "...",
            "confidence": "high"
        },
        ...
    ],
    "sections": [
        {"id": "summary", "title": "Executive Summary", ...},
        {"id": "kpis", "title": "Key Metrics", ...},
        {"id": "insights", "title": "Top Insights", ...},
        {"id": "tables", "title": "Detailed Results", ...}
    ],
    "summary": { ... }
}
```

## Common Workflows

### Workflow 1: Complete Investigation → Insights → Dashboard

```python
# Step 1: Investigate
qga = QueryGenerationAgent(client, explorer)
investigation = qga.investigate_objective(
    table="events",
    objective="Top revenue sources",
    investigation_type=InvestigationType.TOP_CONTRIBUTORS,
    dimensions=["source"],
    metrics=["revenue"]
)

# Step 2: Generate insights
ig = InsightGenerator()
insights = ig.generate_insights(
    findings=investigation["findings"],
    investigation_type=InvestigationType.TOP_CONTRIBUTORS,
    objective=investigation["objective"],
    result_data=investigation["results"][0]
)

# Step 3: Create dashboard
dg = DashboardGenerator()
summary = ig.generate_executive_summary(insights)
dashboard = dg.generate(
    insights=insights,
    query_results=investigation["results"],
    executive_summary=summary
)

# Step 4: Export
dg.export_html(dashboard, "analysis_report.html")
```

### Workflow 2: Multiple Investigations Combined

```python
all_insights = []
all_results = []

# Investigation 1: Trends
trend_results = qga.investigate_objective(
    table="sales",
    objective="Revenue trends",
    investigation_type=InvestigationType.TREND,
    metrics=["revenue"]
)
trend_insights = ig.generate_insights(
    findings=trend_results["findings"],
    investigation_type=InvestigationType.TREND,
    objective="trends",
    result_data=trend_results["results"][0]
)
all_insights.extend(trend_insights)
all_results.extend(trend_results["results"])

# Investigation 2: Segments
segment_results = qga.investigate_objective(
    table="sales",
    objective="Segment analysis",
    investigation_type=InvestigationType.SEGMENT,
    dimensions=["region"],
    metrics=["revenue"]
)
segment_insights = ig.generate_insights(
    findings=segment_results["findings"],
    investigation_type=InvestigationType.SEGMENT,
    objective="segments",
    result_data=segment_results["results"][0]
)
all_insights.extend(segment_insights)
all_results.extend(segment_results["results"])

# Create combined dashboard
dashboard = dg.generate(
    insights=all_insights,
    query_results=all_results,
    executive_summary=ig.generate_executive_summary(all_insights)
)

dg.export_html(dashboard, "comprehensive_report.html")
```

## Testing

### Run Phase 2 Tests

```bash
python3 test_phase2.py
```

Expected Output:
```
PHASE 2 TEST SUITE - Query Gen, Insights, Dashboard
======================================================================
✓ All Phase 2 imports successful
✓ KPI Card creation works
✓ Insight generation works
✓ Trend insights work
✓ Executive summary works
✓ Dashboard generation works
✓ Dashboard with tables works
✓ Dashboard with insights works
✓ Dashboard layout works
✓ HTML export works
✓ JSON Export works
✓ Top-N insights work
✓ Distribution insights work
✓ Anomaly insights work

RESULTS: 14 passed, 0 failed / 14 total
```

## Dashboard HTML Features

The HTML dashboard includes:

- **Executive Summary**: High-level overview
- **KPI Grid**: 4-column grid of metric cards with trends
- **Insights Section**: Top 5 insights with confidence indicators
- **Data Tables**: First 20 rows of each result set
- **Responsive Design**: Basic responsive layout
- **Color Coding**: Green (positive), Orange (medium), Red (negative)

### Sample HTML Output Structure

```html
<!DOCTYPE html>
<html>
<head>
    <title>Data Analytics Dashboard</title>
    <style>
        .kpi-grid { grid-template-columns: repeat(4, 1fr); }
        .insight-confidence.high { background: #4CAF50; }
        .insight-confidence.medium { background: #FF9800; }
        table { width: 100%; border-collapse: collapse; }
    </style>
</head>
<body>
    <h1>Data Analytics Dashboard</h1>
    
    <!-- Summary section -->
    <div class="section">
        <h2>Summary</h2>
        <p>Total Insights: 5</p>
        <p>High Confidence: 3 | Medium: 2 | Low: 0</p>
    </div>
    
    <!-- KPI cards -->
    <div class="section">
        <h2>Key Performance Indicators</h2>
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-value">1000000 ↑</div>
                <div class="kpi-title">Total Revenue</div>
            </div>
            ...
        </div>
    </div>
    
    <!-- Tables -->
    <div class="section">
        <h2>Detailed Results</h2>
        <table>
            <thead><tr><th>Column 1</th><th>Column 2</th></tr></thead>
            <tbody>
                <tr><td>Value 1</td><td>Value 2</td></tr>
                ...
            </tbody>
        </table>
    </div>
</body>
</html>
```

## Troubleshooting

### Issue: "No insights generated"
**Solution:** Check that findings list has `record_count > 0`

### Issue: "DataFrame columns not found"
**Solution:** Verify result_data has expected columns for insight type

### Issue: "HTML export produces empty tables"
**Solution:** Ensure query_results contains valid DataFrames (not None)

### Issue: "Trend calculation shows 0% change"
**Solution:** Check if first and last values are equal; may need larger date range

## Performance Notes

- Insight generation: < 100ms per insight
- Dashboard generation: < 500ms total
- HTML export: < 1s for dashboards with 10+ tables
- JSON export: < 100ms

## Next Steps

**Phase 3 Enhancements:**
- LLM-powered insight generation
- Advanced chart generation
- Natural language recommendations
- Confidence scoring refinement

**Phase 4 Enhancements:**
- Result caching
- Historical insight tracking
- A/B testing framework
- Automated alerting
