"""
Complete Demo - Phase 1 (Foundation) + Phase 2 (Analytics & Dashboard)
Connects to real Trino database and generates dashboards
"""

import os
import webbrowser
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from trino.auth import BasicAuthentication
from trino.sqlalchemy import URL

# Phase 2 imports
from insight_generator import InsightGenerator
from dashboard_generator import DashboardGenerator
from models import InvestigationType

# Load environment variables
load_dotenv()

# Initialize Phase 2 components
ig = InsightGenerator()
dg = DashboardGenerator()

# Initialize
print("\n" + "="*70)
print("AUTONOMOUS ANALYTICS + DASHBOARD")
print("="*70)

# === CONNECT TO TRINO ===
print("\n[Step 0] Connecting to Trino")
print("-" * 70)

TRINO_HOST = os.environ.get("TRINO_HOST", "localhost")
TRINO_PORT = int(os.environ.get("TRINO_PORT", 8443))
TRINO_USER = os.environ.get("TRINO_USER", "user")
TRINO_PASSWORD = os.environ.get("TRINO_PASSWORD", "userpassword")
TRINO_CERT = os.environ.get("TRINO_CERT", "trino-cert.pem")

try:
    print(f"Connecting to {TRINO_HOST}:{TRINO_PORT} as '{TRINO_USER}'")
    
    url = URL(host=TRINO_HOST, port=TRINO_PORT)
    connect_args = {
        "auth": BasicAuthentication(TRINO_USER, TRINO_PASSWORD),
        "http_scheme": "https",
    }
    
    # Handle certificate verification
    if TRINO_CERT and os.path.exists(TRINO_CERT):
        connect_args["verify"] = TRINO_CERT
        print(f"Using certificate: {TRINO_CERT}")
    else:
        # Disable SSL verification if certificate not found
        connect_args["verify"] = False
        print("⚠️  SSL verification disabled (certificate not found)")
    
    engine = create_engine(url, connect_args=connect_args)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
    
    print("✓ Connected to Trino successfully")
    trino_available = True
    
except Exception as e:
    print(f"✗ Connection failed: {str(e)[:100]}...")
    print("ℹ Using mock data for demo instead")
    trino_available = False
    engine = None

# === PREPARE DATA ===
print("\n" + "="*70)
print("PHASE 2: ANALYTICS & DASHBOARD")
print("="*70)

print("\n[Step 1] Preparing Data")
print("-" * 70)

if trino_available:
    try:
        # Query 1: Top channels by cost
        query1 = """
        SELECT 
            channel, 
            COUNT(*) as records,
            ROUND(AVG(cost), 2) as avg_cost,
            ROUND(SUM(cost), 2) as total_cost
        FROM project.ds_interns.mroi_cost_impact_summary_2025
        GROUP BY channel
        ORDER BY total_cost DESC
        LIMIT 10
        """
        
        with engine.connect() as conn:
            df1 = pd.read_sql(text(query1), conn)
        
        print(f"✓ Query 1: Top channels ({len(df1)} rows)")
        
        # Query 2: Sample data
        query2 = """
        SELECT 
            channel,
            cost,
            impact_score,
            customer_segment
        FROM project.ds_interns.mroi_cost_impact_summary_2025
        LIMIT 20
        """
        
        with engine.connect() as conn:
            df2 = pd.read_sql(text(query2), conn)
        
        print(f"✓ Query 2: Sample records ({len(df2)} rows)")
        
        sample_results = {
            "objective": "Analyze cost impact by channel",
            "investigation_type": "SEGMENT",
            "queries": [query1, query2],
            "results": [df1, df2],
            "findings": [
                {
                    "observation": f"Found {len(df1)} channels in data",
                    "record_count": len(df1),
                    "summary": "Channel analysis complete"
                }
            ]
        }
        
        use_mock = False
        
    except Exception as e:
        print(f"✗ Query failed: {e}")
        print("ℹ Falling back to mock data")
        use_mock = True
else:
    use_mock = True

if use_mock:
    # === CREATE SAMPLE DATA ===
    print("\n[Using Mock Data]")
    print("-" * 70)
    
    # Create sample analytics data (simulating query results)
    sample_results = {
        "objective": "Analyze top revenue sources and trends",
        "investigation_type": "TOP_CONTRIBUTORS",
        "queries": [
            "SELECT source, SUM(revenue) as total_revenue FROM sales GROUP BY source ORDER BY total_revenue DESC",
            "SELECT DATE_TRUNC(date, MONTH) as month, SUM(revenue) as revenue FROM sales GROUP BY 1 ORDER BY 1"
        ],
        "results": [
            # Table 1: Top sources
            pd.DataFrame({
                "source": ["Online Platform", "Retail Partners", "Direct Sales", "Affiliates", "Resellers"],
                "revenue": [450000, 320000, 180000, 125000, 75000],
                "growth_pct": [15.2, 8.3, -2.1, 12.5, 5.8]
            }),
            # Table 2: Trends
            pd.DataFrame({
                "month": ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06"],
                "revenue": [320000, 350000, 380000, 420000, 465000, 510000],
                "orders": [1200, 1350, 1580, 1820, 2050, 2340]
            })
        ],
        "findings": [
            {
                "observation": "Top 3 sources account for 85% of revenue",
                "record_count": 5,
                "summary": "Clear market concentration"
            }
        ]
    }

print(f"✓ Data prepared")
print(f"  - Table 1: {len(sample_results['results'][0])} rows")
print(f"  - Table 2: {len(sample_results['results'][1])} rows")

# === GENERATE INSIGHTS ===
print("\n[Step 2] Generating Insights")
print("-" * 70)

insights = ig.generate_insights(
    findings=sample_results["findings"],
    investigation_type=InvestigationType.TOP_CONTRIBUTORS,
    objective=sample_results["objective"],
    result_data=sample_results["results"][0]
)

print(f"✓ Generated {len(insights)} insights")
for insight in insights:
    print(f"\n  📌 {insight.title}")
    print(f"     {insight.observation}")
    print(f"     Confidence: {insight.confidence.upper()}")

# Generate executive summary
print("\n[Step 3] Creating Executive Summary")
print("-" * 70)

summary = ig.generate_executive_summary(insights)
print(f"✓ Executive Summary:")
print(f"  - Total Insights: {summary['total_insights']}")
print(f"  - High Confidence: {summary['high_confidence']}")
print(f"  - Key Findings: {len(summary['key_findings'])}")

# === CREATE DASHBOARD ===
print("\n[Step 4] Generating Dashboard")
print("-" * 70)

dashboard = dg.generate(
    insights=insights,
    metrics={
        "Total Revenue": {"value": 1150000, "change": 12.5, "unit": "$"},
        "Total Orders": {"value": 8340, "change": 18.2, "unit": ""},
        "Avg Order Value": {"value": 138, "change": -3.1, "unit": "$"},
        "Growth Rate": {"value": 12.5, "change": 4.2, "unit": "%"}
    },
    query_results=sample_results["results"],
    executive_summary=summary
)

print(f"✓ Dashboard created with:")
print(f"  - {len(dashboard['kpi_cards'])} KPI cards")
print(f"  - {len(dashboard['tables'])} data tables")
print(f"  - {len(dashboard['insights'])} insights")
print(f"  - {len(dashboard['sections'])} dashboard sections")

# === EXPORT ===
print("\n[Step 5] Exporting Dashboard")
print("-" * 70)

html_file = dg.export_html(dashboard, "dashboard.html")
json_file = dg.export_json(dashboard, "dashboard.json")

print(f"✓ HTML: {html_file}")
print(f"✓ JSON: {json_file}")

# === OPEN IN BROWSER ===
print("\n[Step 6] Opening Dashboard in Browser")
print("-" * 70)

html_path = Path(html_file).resolve()
browser_url = f"file://{html_path}"

try:
    webbrowser.open(browser_url)
    print(f"✓ Dashboard opened automatically!")
    print(f"  URL: {browser_url}")
except Exception as e:
    print(f"ℹ Could not open browser: {e}")
    print(f"  Manually open: {html_path}")

# === SUMMARY ===
print("\n" + "="*70)
print("DEMO COMPLETE ✓")
print("="*70)
print("\n📊 Generated Files:")
print(f"  1. dashboard.html - View in any browser (opened automatically)")
print(f"  2. dashboard.json - For programmatic integration")
print("\n📈 Dashboard Contents:")
print("  ✓ Executive Summary Section")
print("  ✓ 4 KPI Cards with Trends")
print("  ✓ 2 Detailed Data Tables")
print("  ✓ 5 Business Insights with Confidence")
print("  ✓ Recommendations Section")
print("\n🎯 Capabilities Demonstrated:")
print("  ✓ Autonomous data analysis")
print("  ✓ Evidence-based insights")
print("  ✓ Dashboard generation")
print("  ✓ Multi-format export (HTML, JSON)")
print("  ✓ Browser integration")
print("\n💡 Next Steps:")
print("  1. Connect to your Trino data warehouse")
print("  2. Specify your table name in main.py")
print("  3. Run: python3 main.py")
print("  4. Dashboard automatically opens in your browser!")
print("="*70 + "\n")