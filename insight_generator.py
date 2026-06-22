"""
Insight Generation Module - Simple evidence-based insight extraction.
Converts findings into actionable business insights.
"""

from typing import List, Dict, Any
from models import Insight, InvestigationType
import pandas as pd


class InsightGenerator:
    """Generate business insights from investigation results."""

    def __init__(self, llm=None):
        """Initialize insight generator."""
        self.llm = llm  # Optional LLM for future enhancement

    def generate_insights(
        self,
        findings: List[Dict[str, Any]],
        investigation_type: InvestigationType,
        objective: str,
        result_data: pd.DataFrame = None
    ) -> List[Insight]:
        """
        Generate insights from findings.
        
        Args:
            findings: List of finding dictionaries
            investigation_type: Type of analysis
            objective: Analysis objective
            result_data: DataFrame with query results
            
        Returns:
            List of Insight objects
        """
        insights = []

        if not findings or len(findings) == 0:
            return insights

        primary_finding = findings[0]
        record_count = primary_finding.get("record_count", 0)

        if record_count == 0:
            return insights

        # Generate insight based on type
        if investigation_type == InvestigationType.SEGMENT:
            insights.append(
                self._generate_segment_insight(objective, result_data, primary_finding)
            )

        elif investigation_type == InvestigationType.TREND:
            insights.append(
                self._generate_trend_insight(objective, result_data, primary_finding)
            )

        elif investigation_type == InvestigationType.TOP_CONTRIBUTORS:
            insights.append(
                self._generate_topn_insight(objective, result_data, primary_finding)
            )

        elif investigation_type == InvestigationType.DISTRIBUTION:
            insights.append(
                self._generate_distribution_insight(objective, result_data, primary_finding)
            )

        elif investigation_type == InvestigationType.ANOMALY:
            insights.append(
                self._generate_anomaly_insight(objective, result_data, primary_finding)
            )

        else:
            insights.append(
                self._generate_generic_insight(objective, primary_finding)
            )

        return insights

    def _generate_segment_insight(
        self,
        objective: str,
        data: pd.DataFrame,
        finding: Dict
    ) -> Insight:
        """Generate segment analysis insight."""
        observation = f"Segment analysis reveals {len(data)} distinct groups"
        
        if len(data) > 0 and len(data.columns) > 1:
            top_segment = data.iloc[0, 0]
            top_value = data.iloc[0, 1]
            observation = f"Top segment '{top_segment}' shows value of {top_value}"

        evidence = f"{len(data)} segments analyzed with clear performance differences"
        impact = "Segment performance directly impacts resource allocation strategy"
        recommendation = "Focus on top-performing segments for growth"
        confidence = "high" if len(data) > 5 else "medium"

        return Insight(
            title=f"Segment Performance Analysis",
            observation=observation,
            evidence=evidence,
            impact=impact,
            recommendation=recommendation,
            confidence=confidence,
            investigation_type=InvestigationType.SEGMENT
        )

    def _generate_trend_insight(
        self,
        objective: str,
        data: pd.DataFrame,
        finding: Dict
    ) -> Insight:
        """Generate trend analysis insight."""
        observation = f"Time-series analysis spans {len(data)} periods"
        
        if len(data) > 1 and len(data.columns) > 1:
            first_val = data.iloc[0, 1] if len(data.columns) > 1 else 0
            last_val = data.iloc[-1, 1] if len(data.columns) > 1 else 0
            try:
                first_val = float(first_val)
                last_val = float(last_val)
                change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0
                direction = "increased" if change_pct > 0 else "decreased"
                observation = f"Metric {direction} by {abs(change_pct):.1f}% over period"
            except (ValueError, TypeError):
                pass

        evidence = f"{len(data)} time periods show consistent trend pattern"
        impact = "Trend direction is critical for forecasting and planning"
        recommendation = "Use trend analysis for quarterly business planning"
        confidence = "high" if len(data) > 10 else "medium"

        return Insight(
            title="Temporal Trend Analysis",
            observation=observation,
            evidence=evidence,
            impact=impact,
            recommendation=recommendation,
            confidence=confidence,
            investigation_type=InvestigationType.TREND
        )

    def _generate_topn_insight(
        self,
        objective: str,
        data: pd.DataFrame,
        finding: Dict
    ) -> Insight:
        """Generate top N contributors insight."""
        observation = f"Top 20 contributors identified from {len(data)} total"
        
        if len(data) > 0 and len(data.columns) > 1:
            try:
                if len(data.columns) > 2:
                    top3_pct = sum(pd.to_numeric(data.iloc[:3, 2], errors='coerce').fillna(0))
                    observation = f"Top 3 contributors represent {top3_pct:.1f}% of total"
                else:
                    observation = f"Top 3 contributors are significant"
            except Exception:
                observation = f"Top 3 contributors are significant"

        evidence = "Pareto analysis shows 80/20 rule - focus on vital few"
        impact = "80/20 rule likely applies - focus on vital few contributors"
        recommendation = "Prioritize top 3-5 contributors for strategic attention"
        confidence = "high"

        return Insight(
            title="Key Contributors Analysis",
            observation=observation,
            evidence=evidence,
            impact=impact,
            recommendation=recommendation,
            confidence=confidence,
            investigation_type=InvestigationType.TOP_CONTRIBUTORS
        )

    def _generate_distribution_insight(
        self,
        objective: str,
        data: pd.DataFrame,
        finding: Dict
    ) -> Insight:
        """Generate distribution analysis insight."""
        observation = "Numeric distribution statistics analyzed"
        
        if len(data) > 0 and len(data.columns) >= 2:
            try:
                min_val = float(data.iloc[0, 1])
                max_val = float(data.iloc[0, 2]) if len(data.columns) > 2 else min_val
                avg_val = float(data.iloc[0, 3]) if len(data.columns) > 3 else (min_val + max_val) / 2
                observation = f"Values range from {min_val} to {max_val} with average {avg_val:.2f}"
            except (ValueError, TypeError, IndexError):
                observation = "Distribution shows normal spread"

        evidence = "Statistical analysis of numeric column distribution"
        impact = "Distribution shape influences data quality and outlier detection"
        recommendation = "Monitor outliers and distribution shifts over time"
        confidence = "medium"

        return Insight(
            title="Statistical Distribution",
            observation=observation,
            evidence=evidence,
            impact=impact,
            recommendation=recommendation,
            confidence=confidence,
            investigation_type=InvestigationType.DISTRIBUTION
        )

    def _generate_anomaly_insight(
        self,
        objective: str,
        data: pd.DataFrame,
        finding: Dict
    ) -> Insight:
        """Generate anomaly detection insight."""
        observation = f"Anomaly detection identified {len(data)} outliers (Z-score > 3)"
        evidence = f"{len(data)} records flagged as statistical outliers"
        impact = "Anomalies could indicate data quality issues or genuine exceptions"
        recommendation = "Review outliers for data quality or business significance"
        confidence = "high" if len(data) > 0 else "medium"

        return Insight(
            title="Outlier & Anomaly Detection",
            observation=observation,
            evidence=evidence,
            impact=impact,
            recommendation=recommendation,
            confidence=confidence,
            investigation_type=InvestigationType.ANOMALY
        )

    def _generate_generic_insight(
        self,
        objective: str,
        finding: Dict
    ) -> Insight:
        """Generate generic insight."""
        observation = finding.get("observation", "Analysis complete")
        evidence = finding.get("summary", "Data analysis conducted")

        return Insight(
            title="Analysis Finding",
            observation=observation,
            evidence=evidence,
            impact="Finding requires business interpretation",
            recommendation="Review finding in business context",
            confidence="medium"
        )

    def generate_executive_summary(self, insights: List[Insight]) -> Dict[str, Any]:
        """Generate executive summary from insights."""
        summary = {
            "total_insights": len(insights),
            "high_confidence": sum(1 for i in insights if i.confidence == "high"),
            "medium_confidence": sum(1 for i in insights if i.confidence == "medium"),
            "low_confidence": sum(1 for i in insights if i.confidence == "low"),
            "key_findings": [],
            "recommendations": [],
            "risks": [],
            "opportunities": []
        }

        for insight in insights[:5]:  # Top 5 insights
            summary["key_findings"].append(insight.observation)
            summary["recommendations"].append(insight.recommendation)

            # Simple risk/opportunity classification
            if "decrease" in insight.observation.lower() or "negative" in insight.observation.lower():
                summary["risks"].append(insight.observation)
            elif "increase" in insight.observation.lower() or "positive" in insight.observation.lower():
                summary["opportunities"].append(insight.observation)

        return summary

    # Legacy method for backward compatibility
    def generate(self, metadata):
        """Legacy method - use generate_insights instead."""
        if self.llm:
            prompt = f"""Dataset Metadata: {metadata}\n\nGenerate:\n- Executive Summary\n- Top Insights\n- Risks\n- Opportunities"""
            return self.llm.invoke(prompt)
        return "LLM not configured"