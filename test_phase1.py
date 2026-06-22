"""
Phase 1 Test Suite - Validates structure and implementation
Tests imports, module integration, and core functionality
"""

import sys
import traceback
from typing import List, Tuple


def test_imports() -> Tuple[bool, str]:
    """Test all imports work correctly."""
    try:
        print("\n[TEST 1/5] Testing Imports...")
        
        from query_helpers import QueryHelpers
        from data_profiler import DataProfiler, ColumnProfile, DatasetProfile, ColumnType
        from analysis_plan import AnalysisPlanGenerator
        from analysis_planner_agent import AnalysisPlannerAgent
        from models import (
            Investigation, AnalysisPlan, Insight, 
            InvestigationType, QueryResult
        )
        from data_explorer import DataExplorer
        from trino_client import TrinoClient
        
        print("  ✓ All imports successful")
        return True, "All modules imported successfully"
    
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        traceback.print_exc()
        return False, str(e)


def test_query_helpers() -> Tuple[bool, str]:
    """Test QueryHelpers module."""
    try:
        print("\n[TEST 2/5] Testing QueryHelpers...")
        
        from query_helpers import QueryHelpers
        
        helpers = QueryHelpers()
        
        # Test query generation (no execution)
        queries = {
            "describe": helpers.describe_table("test_table"),
            "count": helpers.count_rows("test_table"),
            "sample": helpers.sample_data("test_table"),
            "null_stats": helpers.column_null_percentage("test_table", "col1"),
            "cardinality": helpers.column_cardinality("test_table", "col1"),
            "top_values": helpers.column_top_values("test_table", "col1"),
            "numeric": helpers.numeric_column_stats("test_table", "col1"),
            "date_range": helpers.date_column_range("test_table", "col1"),
            "trend": helpers.trend_analysis("test_table", "date_col", "metric_col"),
            "segment": helpers.segment_distribution("test_table", "dim_col", "metric_col"),
        }
        
        # Validate all queries are strings
        for name, query in queries.items():
            if not isinstance(query, str) or len(query) == 0:
                raise ValueError(f"Query {name} is invalid: {query}")
            # Check for basic SQL structure (SELECT, FROM, or DESCRIBE)
            query_upper = query.strip().upper()
            if not any(keyword in query_upper for keyword in ["SELECT", "DESCRIBE"]):
                raise ValueError(f"Query {name} missing SELECT or DESCRIBE: {query}")
        
        print(f"  ✓ Generated {len(queries)} query templates")
        return True, f"All {len(queries)} query templates valid"
    
    except Exception as e:
        print(f"  ✗ QueryHelpers test failed: {e}")
        traceback.print_exc()
        return False, str(e)


def test_models() -> Tuple[bool, str]:
    """Test data models."""
    try:
        print("\n[TEST 3/5] Testing Models...")
        
        from models import (
            Investigation, AnalysisPlan, Insight, 
            InvestigationType, QueryResult
        )
        
        # Test Investigation model
        inv = Investigation(
            type=InvestigationType.TREND,
            title="Test Trend",
            description="Test description",
            priority=1,
            expected_impact="high",
            suggested_metrics=["metric1"]
        )
        assert inv.title == "Test Trend"
        print("  ✓ Investigation model works")
        
        # Test Insight model
        insight = Insight(
            title="Test Insight",
            observation="Something happened",
            evidence="Data shows X",
            impact="This matters",
            recommendation="Do this",
            confidence="high"
        )
        assert insight.title == "Test Insight"
        print("  ✓ Insight model works")
        
        # Test QueryResult model
        result = QueryResult(
            query="SELECT * FROM test",
            result_rows=100,
            success=True
        )
        assert result.result_rows == 100
        print("  ✓ QueryResult model works")
        
        print("  ✓ All models valid")
        return True, "All models instantiate correctly"
    
    except Exception as e:
        print(f"  ✗ Models test failed: {e}")
        traceback.print_exc()
        return False, str(e)


def test_data_profiler_structure() -> Tuple[bool, str]:
    """Test DataProfiler class structure."""
    try:
        print("\n[TEST 4/5] Testing DataProfiler Structure...")
        
        from data_profiler import DataProfiler, ColumnProfile, DatasetProfile, ColumnType
        
        # Test ColumnProfile
        col = ColumnProfile(
            name="test_col",
            data_type="bigint",
            column_type=ColumnType.MEASURE,
            null_count=0,
            null_pct=0.0,
            cardinality=1000,
            approx_cardinality=1000
        )
        assert col.name == "test_col"
        assert col.column_type == ColumnType.MEASURE
        print("  ✓ ColumnProfile structure valid")
        
        # Test DatasetProfile
        profile = DatasetProfile(
            table_name="test_table",
            row_count=10000,
            column_count=5,
            columns={"col1": col},
            dimensions=["dim1"],
            measures=["metric1"],
            dates=[],
            ids=[]
        )
        assert profile.table_name == "test_table"
        assert len(profile.columns) == 1
        print("  ✓ DatasetProfile structure valid")
        
        # Test ColumnType enum
        assert ColumnType.DIMENSION.value == "dimension"
        assert ColumnType.MEASURE.value == "measure"
        assert ColumnType.DATE.value == "date"
        print("  ✓ ColumnType enum valid")
        
        print("  ✓ DataProfiler structures valid")
        return True, "DataProfiler structures are correct"
    
    except Exception as e:
        print(f"  ✗ DataProfiler structure test failed: {e}")
        traceback.print_exc()
        return False, str(e)


def test_analysis_plan_structure() -> Tuple[bool, str]:
    """Test AnalysisPlan and related structures."""
    try:
        print("\n[TEST 5/5] Testing AnalysisPlan Structure...")
        
        from analysis_plan import AnalysisPlanGenerator
        from models import Investigation, AnalysisPlan, InvestigationType
        
        # Test Investigation creation
        investigations = [
            Investigation(
                type=InvestigationType.TREND,
                title="Trend Analysis",
                description="Analyze trend",
                priority=1,
                expected_impact="high"
            ),
            Investigation(
                type=InvestigationType.SEGMENT,
                title="Segment Analysis",
                description="Analyze segments",
                priority=2,
                expected_impact="high"
            )
        ]
        
        # Test AnalysisPlan creation
        plan = AnalysisPlan(
            table_name="test_table",
            dataset_type="time_series",
            business_entities=["transaction", "time"],
            key_metrics=["revenue", "units"],
            key_dimensions=["region", "product"],
            investigations=investigations
        )
        
        assert plan.table_name == "test_table"
        assert len(plan.investigations) == 2
        assert plan.investigations[0].priority == 1
        print("  ✓ AnalysisPlan structure valid")
        
        print("  ✓ All AnalysisPlan structures valid")
        return True, "AnalysisPlan structures are correct"
    
    except Exception as e:
        print(f"  ✗ AnalysisPlan structure test failed: {e}")
        traceback.print_exc()
        return False, str(e)


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*70)
    print("PHASE 1 TEST SUITE")
    print("="*70)
    
    tests = [
        ("Imports", test_imports),
        ("QueryHelpers", test_query_helpers),
        ("Models", test_models),
        ("DataProfiler", test_data_profiler_structure),
        ("AnalysisPlan", test_analysis_plan_structure),
    ]
    
    results: List[Tuple[str, bool, str]] = []
    
    for name, test_func in tests:
        success, message = test_func()
        results.append((name, success, message))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, message in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name:20s} - {message}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 1 implementation is structurally sound.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
