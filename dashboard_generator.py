"""
Dashboard Generator - Simple dashboard creation from insights and query results.
Generates KPI cards, tables, and dashboard layout.
"""

from typing import List, Dict, Any
import pandas as pd
from models import Insight, InvestigationType
import json


class KPICard:
    """Represents a single KPI card on the dashboard."""
    
    def __init__(self, title: str, value: Any, trend: str = "", unit: str = "", status: str = "neutral"):
        """
        Args:
            title: KPI title
            value: Current value
            trend: Trend indicator (up/down/stable)
            unit: Unit of measurement
            status: Status indicator (positive/negative/neutral)
        """
        self.title = title
        self.value = value
        self.trend = trend
        self.unit = unit
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "value": str(self.value),
            "trend": self.trend,
            "unit": self.unit,
            "status": self.status
        }


class DashboardGenerator:
    """Generate simple dashboards from insights and query results."""

    def __init__(self):
        """Initialize dashboard generator."""
        pass

    def generate(
        self,
        insights: List[Insight] = None,
        metrics: Dict[str, Any] = None,
        query_results: List[pd.DataFrame] = None,
        executive_summary: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate dashboard specification.
        
        Args:
            insights: List of Insight objects
            metrics: Dictionary of metric values
            query_results: List of DataFrames from queries
            executive_summary: Executive summary from insight generator
            
        Returns:
            Dictionary with dashboard specification
        """
        dashboard = {
            "title": "Data Analytics Dashboard",
            "version": "1.0",
            "kpi_cards": [],
            "tables": [],
            "insights": [],
            "sections": [],
            "summary": executive_summary or {}
        }

        # Generate KPI cards from metrics
        if metrics:
            dashboard["kpi_cards"] = self._generate_kpi_cards(metrics)

        # Generate tables from query results
        if query_results:
            dashboard["tables"] = self._generate_tables(query_results)

        # Add insights
        if insights:
            dashboard["insights"] = self._format_insights(insights)

        # Generate layout sections
        dashboard["sections"] = self._generate_layout(insights, query_results)

        return dashboard

    def _generate_kpi_cards(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate KPI cards from metrics dictionary."""
        cards = []

        for metric_name, metric_value in metrics.items():
            # Determine trend and status
            trend = ""
            status = "neutral"

            if isinstance(metric_value, dict):
                value = metric_value.get("value", 0)
                change = metric_value.get("change", 0)
                unit = metric_value.get("unit", "")
                
                if change > 0:
                    trend = "↑"
                    status = "positive"
                elif change < 0:
                    trend = "↓"
                    status = "negative"
                else:
                    trend = "→"
            else:
                value = metric_value
                unit = ""

            card = KPICard(
                title=metric_name.replace("_", " ").title(),
                value=value,
                trend=trend,
                unit=unit,
                status=status
            )
            cards.append(card.to_dict())

        return cards

    def _generate_tables(self, query_results: List[pd.DataFrame]) -> List[Dict[str, Any]]:
        """Convert DataFrames to table specifications."""
        tables = []

        for idx, df in enumerate(query_results):
            if df is None or len(df) == 0:
                continue

            table_spec = {
                "id": f"table_{idx}",
                "title": f"Results Table {idx + 1}",
                "row_count": len(df),
                "columns": list(df.columns),
                "data": df.head(100).to_dict(orient="records"),  # First 100 rows
                "summary": self._table_summary(df)
            }
            tables.append(table_spec)

        return tables

    def _table_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for a table."""
        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(df.select_dtypes(include=['number']).columns),
            "text_columns": len(df.select_dtypes(include=['object']).columns),
            "null_count": df.isnull().sum().sum()
        }
        return summary

    def _format_insights(self, insights: List[Insight]) -> List[Dict[str, Any]]:
        """Format insights for dashboard display."""
        formatted = []

        for insight in insights[:10]:  # Top 10 insights
            formatted.append({
                "title": insight.title,
                "observation": insight.observation,
                "evidence": insight.evidence,
                "impact": insight.impact,
                "recommendation": insight.recommendation,
                "confidence": insight.confidence,
                "type": insight.investigation_type.value if hasattr(insight.investigation_type, 'value') else str(insight.investigation_type)
            })

        return formatted

    def _generate_layout(
        self,
        insights: List[Insight] = None,
        query_results: List[pd.DataFrame] = None
    ) -> List[Dict[str, Any]]:
        """Generate dashboard layout sections."""
        sections = []

        # Section 1: Executive Summary
        sections.append({
            "id": "summary",
            "title": "Executive Summary",
            "type": "summary",
            "content": "Dashboard summary and key metrics"
        })

        # Section 2: Key Metrics (KPIs)
        sections.append({
            "id": "kpis",
            "title": "Key Performance Indicators",
            "type": "kpi_grid",
            "layout": "grid_4"  # 4 columns
        })

        # Section 3: Top Insights
        if insights and len(insights) > 0:
            sections.append({
                "id": "insights",
                "title": "Top Insights",
                "type": "insights_list",
                "count": min(5, len(insights))
            })

        # Section 4: Data Tables
        if query_results and len(query_results) > 0:
            sections.append({
                "id": "tables",
                "title": "Detailed Results",
                "type": "tables",
                "table_count": len(query_results)
            })

        # Section 5: Recommendations
        sections.append({
            "id": "recommendations",
            "title": "Recommended Actions",
            "type": "recommendations",
            "source": "insights"
        })

        return sections

    def export_html(
        self,
        dashboard: Dict[str, Any],
        filename: str = "dashboard.html"
    ) -> str:
        """Export dashboard as simple HTML."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; padding: 15px; background: #fafafa; border-left: 4px solid #2196F3; }}
                .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
                .kpi-card {{ background: white; padding: 15px; border-radius: 4px; border: 1px solid #ddd; text-align: center; }}
                .kpi-value {{ font-size: 28px; font-weight: bold; color: #2196F3; }}
                .kpi-title {{ font-size: 14px; color: #666; margin-top: 10px; }}
                .table-container {{ overflow-x: auto; margin: 15px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #f0f0f0; font-weight: bold; }}
                h2 {{ color: #333; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }}
                .insight {{ background: white; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 3px solid #4CAF50; }}
                .insight-title {{ font-weight: bold; color: #333; }}
                .insight-confidence {{ display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; margin-top: 5px; }}
                .high {{ background: #4CAF50; color: white; }}
                .medium {{ background: #FF9800; color: white; }}
                .low {{ background: #f44336; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                
                <div class="section">
                    <h2>Summary</h2>
                    <p>Total Insights: {total_insights}</p>
                    <p>High Confidence: {high_conf} | Medium: {med_conf} | Low: {low_conf}</p>
                </div>
        """

        # Add KPI Cards
        if dashboard.get("kpi_cards"):
            html += '<div class="section"><h2>Key Performance Indicators</h2><div class="kpi-grid">'
            for kpi in dashboard["kpi_cards"]:
                html += f"""
                <div class="kpi-card">
                    <div class="kpi-value">{kpi['value']} {kpi['trend']}</div>
                    <div class="kpi-title">{kpi['title']}</div>
                </div>
                """
            html += "</div></div>"

        # Add Insights
        if dashboard.get("insights"):
            html += '<div class="section"><h2>Key Insights</h2>'
            for insight in dashboard["insights"][:5]:
                confidence_class = insight["confidence"].lower()
                html += f"""
                <div class="insight">
                    <div class="insight-title">{insight['title']}</div>
                    <p><strong>Observation:</strong> {insight['observation']}</p>
                    <p><strong>Recommendation:</strong> {insight['recommendation']}</p>
                    <span class="insight-confidence {confidence_class}">{insight['confidence'].upper()}</span>
                </div>
                """
            html += "</div>"

        # Add Tables
        if dashboard.get("tables"):
            html += '<div class="section"><h2>Detailed Results</h2>'
            for table in dashboard["tables"]:
                html += f"<h3>{table['title']}</h3><p>Rows: {table['row_count']}</p>"
                html += '<div class="table-container"><table><thead><tr>'
                
                # Table headers
                for col in table["columns"]:
                    html += f"<th>{col}</th>"
                html += "</tr></thead><tbody>"
                
                # Table rows
                for row in table["data"][:20]:  # First 20 rows
                    html += "<tr>"
                    for col in table["columns"]:
                        html += f"<td>{row.get(col, '')}</td>"
                    html += "</tr>"
                
                html += "</tbody></table></div>"
            html += "</div>"

        html += """
            </div>
        </body>
        </html>
        """

        # Format HTML with dashboard data
        summary = dashboard.get("summary", {})
        try:
            html = html.format(
                title=dashboard.get("title", "Analytics Dashboard"),
                total_insights=summary.get("total_insights", 0),
                high_conf=summary.get("high_confidence", 0),
                med_conf=summary.get("medium_confidence", 0),
                low_conf=summary.get("low_confidence", 0)
            )
        except KeyError:
            pass

        # Save to file
        with open(filename, "w") as f:
            f.write(html)

        return filename

    def export_json(self, dashboard: Dict[str, Any], filename: str = "dashboard.json") -> str:
        """Export dashboard as JSON."""
        with open(filename, "w") as f:
            json.dump(dashboard, f, indent=2, default=str)
        return filename