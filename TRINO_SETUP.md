# Trino Connection Setup Guide

## Quick Start

The system is now configured to connect to your Trino database. Here's how to set it up:

### Step 1: Create .env file

Copy the example file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Trino credentials:

```
TRINO_HOST=trino.c-9-209-20-147.wdc.compute.c.ibm.com
TRINO_PORT=443
TRINO_USER=your_username
TRINO_PASSWORD=your_password
TRINO_CERT=/path/to/your/cert.pem
```

### Step 2: Get Your Certificate

For HTTPS connections, you need the Trino certificate. Place it in your project directory:

```bash
# Example: if certificate is in Downloads
cp ~/downloads/trino-prod.client.bundle.pem ./trino-cert.pem
```

Update `.env`:
```
TRINO_CERT=trino-cert.pem
```

### Step 3: Run the Dashboard

```bash
python3 main.py
```

This will:
1 Connect to your Trino database. 
2 Query your data (project.ds_interns.mroi_cost_impact_summary_2025). 
3 Generate analytics insights. 
4 Create dashboard. 
5 Open dashboard.html in your browser automatically. 

## How It Works

### Connection Method

The system uses SQLAlchemy with Trino's official connector:

```python
from sqlalchemy import create_engine, text
from trino.auth import BasicAuthentication
from trino.sqlalchemy import URL

url = URL(host=TRINO_HOST, port=TRINO_PORT)
connect_args = {
    "auth": BasicAuthentication(TRINO_USER, TRINO_PASSWORD),
    "http_scheme": "https",
    "verify": TRINO_CERT,  # Certificate path
}
engine = create_engine(url, connect_args=connect_args)

# Execute queries
with engine.connect() as conn:
    df = pd.read_sql(text(query), conn)
```

### Queries Executed

When you run `python3 main.py`, it executes:

**Query 1 - Top channels by cost:**
```sql
SELECT 
    channel, 
    COUNT(*) as records,
    ROUND(AVG(cost), 2) as avg_cost,
    ROUND(SUM(cost), 2) as total_cost
FROM project.ds_interns.mroi_cost_impact_summary_2025
GROUP BY channel
ORDER BY total_cost DESC
LIMIT 10
```

**Query 2 - Sample data:**
```sql
SELECT 
    channel,
    cost,
    impact_score,
    customer_segment
FROM project.ds_interns.mroi_cost_impact_summary_2025
LIMIT 20
```

### Fallback to Mock Data

If connection fails, the system automatically:
1. Logs the connection error
2. Falls back to mock sample data
3. Generates dashboard with mock data
4. Opens dashboard in browser

This way you can always see the dashboard working, even without database access.

## Troubleshooting

### Issue: SSL Certificate Error

**Error:** `SSLError(SSLError(9, '[X509] PEM lib'))`

**Solutions:**

1. **Verify certificate path:**
   ```bash
   ls -la trino-cert.pem
   ```

2. **Update .env with correct path:**
   ```
   TRINO_CERT=/full/path/to/trino-cert.pem
   ```

3. **Check certificate format:**
   ```bash
   openssl x509 -in trino-cert.pem -text -noout
   ```

4. **Disable SSL verification (development only):**
   In `.env`:
   ```
   TRINO_CERT=
   ```
   Then modify main.py to set `"verify": False`

### Issue: Connection Timeout

**Error:** `Max retries exceeded`

**Solutions:**

1. Verify Trino is running:
   ```bash
   ping trino.c-9-209-20-147.wdc.compute.c.ibm.com
   ```

2. Check firewall/network:
   ```bash
   telnet trino.c-9-209-20-147.wdc.compute.c.ibm.com 443
   ```

3. Verify credentials in `.env`

### Issue: Authentication Failed

**Error:** `TrinoConnectionError` during auth

**Solutions:**

1. Verify username and password in `.env`
2. Check if credentials have TRINO_HOST permissions
3. Verify USER environment (user, admin, etc.)

### Issue: Query Error

**Error:** `TrinoException: ...`

**Solutions:**

1. Verify table exists:
   ```sql
   SHOW TABLES FROM project.ds_interns;
   ```

2. Check table name:
   ```sql
   SELECT COUNT(*) FROM project.ds_interns.mroi_cost_impact_summary_2025;
   ```

3. Modify queries in main.py if needed

## Modifying Queries

To query different data, edit `main.py`:

Find this section:
```python
if trino_available:
    try:
        # Query 1: Top channels by cost
        query1 = """
        SELECT ...
        """
```

Replace with your own queries. Example:

```python
query1 = """
SELECT 
    your_column,
    COUNT(*) as count,
    SUM(your_metric) as total
FROM your_schema.your_table
GROUP BY your_column
ORDER BY total DESC
LIMIT 10
"""
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| TRINO_HOST | Trino server hostname | trino.c-9-209-20-147.wdc.compute.c.ibm.com |
| TRINO_PORT | Trino server port | 443 |
| TRINO_USER | Username for authentication | your_username |
| TRINO_PASSWORD | Password for authentication | your_password |
| TRINO_CERT | Path to SSL certificate | /path/to/cert.pem |

## Testing Connection

To test your Trino connection without running the full dashboard:

```python
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from trino.auth import BasicAuthentication
from trino.sqlalchemy import URL

load_dotenv()

TRINO_HOST = os.environ.get("TRINO_HOST")
TRINO_PORT = int(os.environ.get("TRINO_PORT", 443))
TRINO_USER = os.environ.get("TRINO_USER")
TRINO_PASSWORD = os.environ.get("TRINO_PASSWORD")
TRINO_CERT = os.environ.get("TRINO_CERT")

url = URL(host=TRINO_HOST, port=TRINO_PORT)
connect_args = {
    "auth": BasicAuthentication(TRINO_USER, TRINO_PASSWORD),
    "http_scheme": "https",
    "verify": TRINO_CERT if TRINO_CERT else False,
}

engine = create_engine(url, connect_args=connect_args)

# Test connection
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
     Connection successful!")print("
except Exception as e:
    print( Connection failed: {e}")f"

# Test query
try:
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT * FROM project.ds_interns.mroi_cost_impact_summary_2025 LIMIT 5"),
            conn
        )
    print( Query successful! Got {len(df)} rows")f"
    print(df)
except Exception as e:
    print( Query failed: {e}")f"
```

## Dashboard Output

Once connected and running, you'll get:

1. **dashboard.html** - Styled dashboard with:
   - KPI cards with trends
   - Data tables from your queries
   - Business insights
   - Executive summary

2. **dashboard.json** - Machine-readable format for:
   - API integration
   - Further processing
   - Programmatic access

Both files are generated automatically and the HTML opens in your browser.

## Next Steps

1 Set up .env file with credentials. 
2 Place certificate in project directory. 
3 Run: `python3 main.py`. 
4 Dashboard opens automatically. 
5 Customize queries as needed. 
6 Share dashboard.html with stakeholders. 

## Support

For issues with Trino connection, check:
- Credentials in .env
- Certificate path and format
- Trino server status
- Network/firewall
- Query syntax and table names

For dashboard customization:
- Edit main.py queries
- Modify sample_results structure
- Update dashboard generation parameters
