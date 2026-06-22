from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from enum import Enum


class InvestigationType(str, Enum):
    """Types of analyses that can be performed."""
    TREND = "trend"
    SEGMENT = "segment"
    CORRELATION = "correlation"
    ANOMALY = "anomaly"
    TOP_CONTRIBUTORS = "top_contributors"
    DISTRIBUTION = "distribution"


class Investigation(BaseModel):
    """Proposed investigation for a dataset."""
    type: InvestigationType
    title: str
    description: str
    priority: int  # 1 = highest
    expected_impact: str  # "high", "medium", "low"
    suggested_metrics: Optional[List[str]] = None
    suggested_dimensions: Optional[List[str]] = None
    query_template: Optional[str] = None


class AnalysisPlan(BaseModel):
    """Plan for analyzing a dataset."""
    table_name: str
    dataset_type: Optional[str] = None
    business_entities: List[str]
    key_metrics: List[str]
    key_dimensions: List[str]
    investigations: List[Investigation]
    total_priority_score: int = 0


class Insight(BaseModel):
    """Business insight extracted from data."""
    title: str
    observation: str
    evidence: str
    impact: str
    recommendation: str
    confidence: str
    investigation_type: Optional[InvestigationType] = None


class QueryResult(BaseModel):
    """Result of a query execution."""
    query: str
    result_rows: int
    execution_time_ms: Optional[float] = None
    sample_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    success: bool = True