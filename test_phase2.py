"""
Phase 2 Tests - Query Generation, Insight Generation, and Dashboard Generator.
Tests iterative investigation, insight extraction, and dashboard creation.
"""

import sys
import pandas as pd
from models import Insight, InvestigationType
from insight_generator import InsightGenerator
from dashboard_generator import DashboardGenerator, KPICard
from query_generation_agent import QueryGenerationAgent


def test_imports():
    """Test all Phase 2 imports."""
    print("✓ All Phase 2 imports successful")
    return True


def test_kpi_card():
    """Test KPI Card creation."""
    card = KPICard(
        title="Revenue",
        value=150000,
        trend="↑",
        unit="$",
        status="positive"
    )
    
    card_dict = card.to_dict()
    assert card_dict["title"] == "Revenue"
    assert card_dict["value"] == "150000"
    assert card_dict["status"] == "positive"
    print("✓ KPI Card creation works")
    return True


def test_insight_generator():
    """Test insight generation from findings."""
    generator = InsightGenerator()
    
    # Create sample findings
    findings = [
        {
            "record_count": 100,
            "observation": "Top segment has 40% share",
            "summary": "Clear winner identified"
        }
    ]
    
    # Create sample data
    data = pd.DataFrame({
        "segment": ["A", "B", "C"],
        "value": [40, 30, 30]
    })
    
    # Test segment insights
    insights = generator.generate_insights(
        findings=findings,
        investigation_type=InvestigationType.SEGMENT,
        objective="Analyze segments",
        result_data=data
    )
    
    assert len(insights) > 0
    assert insights[0].title == "Segment Performance Analysis"
    assert insights[0].confidence in ["high", "medium", "low"]
    print("✓ Insight generation works")
    return True


def test_trend_insights():
    """Test trend-specific insights."""
    generator = InsightGenerator()
    
    findings = [
        {
            "record_count": 50,
            "observation": "Trend detected"
        }
    ]
    
    data = pd.DataFrame({
        "date": ["2024-01", "2024-02", "2024-03"],
        "value": [100, 120, 145]
    })
    
    insights = generator.generate_insights(
        findings=findings,
        investigation_type=InvestigationType.TREND,
        objective="Analyze trend",
        result_data=data
    )
    
    assert len(insights) > 0
    assert "increased" in insights[0].observation.lower()
    print("✓ Trend insights work")
    return True


def test_executive_summary():
    """Test executive summary generation."""
    generator = InsightGenerator()
    
    insights = [
        Insight(
            title="Insight 1",
            observation="Positive change",
            evidence="Data shows growth",
            impact="Revenue impact",
            recommendation="Action 1",
            confidence="high",
            investigation_type=InvestigationType.TREND
        ),
        Insight(
            title="Insight 2",
            observation="Risk detected",
            evidence="Data shows decline",
            impact="Risk impact",
            recommendation="Action 2",
            confidence="medium",
            investigation_type=InvestigationType.ANOMALY
        )
    ]
    
    summary = generator.generate_executive_summary(insights)
    
    assert summary["total_insights"] == 2
    assert summary["high_confidence"] == 1
    assert summary["medium_confidence"] == 1
    assert len(summary["key_findings"]) > 0
    print("✓ Executive summary works")
    return True


def test_dashboard_generation():
    """Test dashboard generation."""
    generator = DashboardGenerator()
    
    metrics = {
        "total_revenue": {"value": 1000000, "change": 15, "unit": "$"},
        "customer_count": {"value": 5000, "change": -5, "unit": ""},
        "avg_order_value": 200
    }
    
    dashboard = generator.generate(metrics=metrics)
    
    assert dashboard["title"] == "Data Analytics Dashboard"
    assert len(dashboard["kpi_cards"]) == 3
    assert dashboard["kpi_cards"][0]["status"] == "positive"  # Positive change
    print("✓ Dashboard generation works")
    return True


def test_dashboard_with_tables():
    """Test dashboard with tables."""
    generator = DashboardGenerator()
    
    df1 = pd.DataFrame({
        "segment": ["A", "B", "C"],
        "revenue": [100000, 80000, 60000]
    })
    
    df2 = pd.DataFrame({
        "month": ["Jan", "Feb", "Mar"],
        "sales": [50000, 55000, 60000]
    })
    
    dashboard = generator.generate(query_results=[df1, df2])
    
    assert len(dashboard["tables"]) == 2
    assert dashboard["tables"][0]["row_count"] == 3
    assert "segment" in dashboard["tables"][0]["columns"]
    print("✓ Dashboard with tables works")
    return True


def test_dashboard_with_insights():
    """Test dashboard with insights."""
    generator = DashboardGenerator()
    
    insights = [
        Insight(
            title="Top Insight",
            observation="Key finding",
            evidence="Evidence data",
            impact="Business impact",
            recommendation="Action recommended",
            confidence="high",
            investigation_type=InvestigationType.TOP_CONTRIBUTORS
        )
    ]
    
    dashboard = generator.generate(insights=insights)
    
    assert len(dashboard["insights"]) > 0
    assert dashboard["insights"][0]["title"] == "Top Insight"
    print("✓ Dashboard with insights works")
    return True


def test_dashboard_layout():
    """Test dashboard layout generation."""
    generator = DashboardGenerator()
    
    insights = [Insight(
        title="Test",
        observation="obs",
        evidence="ev",
        impact="imp",
        recommendation="rec",
        confidence="high"
    )]
    
    query_results = [pd.DataFrame({"col": [1, 2, 3]})]
    
    dashboard = generator.generate(
        insights=insights,
        query_results=query_results
    )
    
    sections = dashboard["sections"]
    assert len(sections) >= 4
    assert sections[0]["id"] == "summary"
    assert sections[1]["id"] == "kpis"
    assert any(s["id"] == "tables" for s in sections)
    print("✓ Dashboard layout works")
    return True


def test_html_export():
    """Test HTML export."""
    generator = DashboardGenerator()
    
    dashboard = generator.generate(
        metrics={"metric1": 100},
        query_results=[pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})]
    )
    
    filename = generator.export_html(dashboard, "test_dashboard.html")
    assert filename == "test_dashboard.html"
    
    # Check file exists
    try:
        with open(filename, "r") as f:
            content = f.read()
            assert "Data Analytics Dashboard" in content
            assert "Key Performance Indicators" in content
    finally:
        import os
        if os.path.exists(filename):
            os.remove(filename)
    
    print("✓ HTML export works")
    return True


def test_json_export():
    """Test JSON export."""
    generator = DashboardGenerator()
    
    dashboard = generator.generate(
        metrics={"metric1": 100}
    )
    
    filename = generator.export_json(dashboard, "test_dashboard.json")
    assert filename == "test_dashboard.json"
    
    # Check file exists and is valid JSON
    try:
        import json
        with open(filename, "r") as f:
            data = json.load(f)
            assert data["title"] == "Data Analytics Dashboard"
    finally:
        import os
        if os.path.exists(filename):
            os.remove(filename)
    
    print("✓ JSON export works")
    return True


def test_topn_insights():
    """Test top-N contributor insights."""
    generator = InsightGenerator()
    
    findings = [{"record_count": 20}]
    
    data = pd.DataFrame({
        "contributor": ["A", "B", "C"],
        "contribution": [50, 30, 20],
        "percentage": [50, 30, 20]
    })
    
    insights = generator.generate_insights(
        findings=findings,
        investigation_type=InvestigationType.TOP_CONTRIBUTORS,
        objective="Find top contributors",
        result_data=data
    )
    
    assert len(insights) > 0
    assert "80/20" in insights[0].evidence
    print("✓ Top-N insights work")
    return True


def test_distribution_insights():
    """Test distribution analysis insights."""
    generator = InsightGenerator()
    
    findings = [{"record_count": 100}]
    
    data = pd.DataFrame({
        "stat": ["count", "min", "max", "avg", "stddev"],
        "value": [1000, 10, 1000, 500, 200]
    })
    
    insights = generator.generate_insights(
        findings=findings,
        investigation_type=InvestigationType.DISTRIBUTION,
        objective="Distribution analysis",
        result_data=data
    )
    
    assert len(insights) > 0
    assert "range" in insights[0].observation.lower()
    print("✓ Distribution insights work")
    return True


def test_anomaly_insights():
    """Test anomaly detection insights."""
    generator = InsightGenerator()
    
    findings = [{"record_count": 5}]
    
    data = pd.DataFrame({
        "value": [1, 2, 3, 100, 200]
    })
    
    insights = generator.generate_insights(
        findings=findings,
        investigation_type=InvestigationType.ANOMALY,
        objective="Find outliers",
        result_data=data
    )
    
    assert len(insights) > 0
    assert "outlier" in insights[0].title.lower()
    print("✓ Anomaly insights work")
    return True


def run_all_tests():
    """Run all Phase 2 tests."""
    tests = [
        ("Imports", test_imports),
        ("KPI Card", test_kpi_card),
        ("Insight Generation", test_insight_generator),
        ("Trend Insights", test_trend_insights),
        ("Executive Summary", test_executive_summary),
        ("Dashboard Generation", test_dashboard_generation),
        ("Dashboard with Tables", test_dashboard_with_tables),
        ("Dashboard with Insights", test_dashboard_with_insights),
        ("Dashboard Layout", test_dashboard_layout),
        ("HTML Export", test_html_export),
        ("JSON Export", test_json_export),
        ("Top-N Insights", test_topn_insights),
        ("Distribution Insights", test_distribution_insights),
        ("Anomaly Insights", test_anomaly_insights),
    ]

    print("\n" + "="*70)
    print("PHASE 2 TEST SUITE - Query Gen, Insights, Dashboard")
    print("="*70 + "\n")

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"✗ {test_name} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {test_name} failed: {e}")

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed / {len(tests)} total")
    print("="*70 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
