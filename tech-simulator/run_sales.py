import os
import sys
import base64
import json
import pandas as pd
from datetime import datetime
from google.cloud import bigquery

# Add folder to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from generate import (
    generate_employees,
    generate_clients,
    generate_sales,
    generate_operating_costs
)

# ---------------- CONFIG ----------------
PROJECT_ID = "your-gcp-project-id"
DATASET = "tech_analytics"

EMPLOYEES_TABLE = f"{PROJECT_ID}.{DATASET}.employees"
CLIENTS_TABLE = f"{PROJECT_ID}.{DATASET}.clients"
SALES_TABLE = f"{PROJECT_ID}.{DATASET}.sales"
COSTS_TABLE = f"{PROJECT_ID}.{DATASET}.operating_costs"

INITIAL_EMPLOYEES = 1000
INITIAL_INTERNS = 100
INITIAL_CLIENTS = 500
INITIAL_SALES = int(os.environ.get("INITIAL_SALES", "100000"))
SALES_PER_RUN = 1000

# ---------------- BigQuery Client ----------------
client = bigquery.Client()

def table_has_data(table_id):
    query = f"SELECT COUNT(1) AS cnt FROM `{table_id}`"
    return list(client.query(query))[0].cnt > 0

def append_df(df, table_id):
    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            autodetect=True
        )
    )
    job.result()
    print(f"✓ Loaded {len(df):,} rows → {table_id}")

# ---------------- EMPLOYEES ----------------
if not table_has_data(EMPLOYEES_TABLE):
    print("📊 Generating employees...")
    employees = generate_employees(INITIAL_EMPLOYEES, INITIAL_INTERNS)
    append_df(pd.DataFrame(employees), EMPLOYEES_TABLE)
else:
    print("✓ Employees already exist")

# ---------------- CLIENTS ----------------
if not table_has_data(CLIENTS_TABLE):
    print("📊 Generating clients...")
    clients = generate_clients(INITIAL_CLIENTS)
    append_df(pd.DataFrame(clients), CLIENTS_TABLE)
else:
    clients = list(client.query(f"SELECT * FROM `{CLIENTS_TABLE}`"))
    print("✓ Clients already exist")

# ---------------- OPERATING COSTS ----------------
if not table_has_data(COSTS_TABLE):
    print("💰 Generating operating costs...")
    costs = generate_operating_costs()
    append_df(pd.DataFrame(costs), COSTS_TABLE)
else:
    print("✓ Operating costs already exist")

# ---------------- SALES ----------------
if not table_has_data(SALES_TABLE):
    num_sales = INITIAL_SALES
    print(f"🚀 Initial sales load: {num_sales:,}")
else:
    num_sales = SALES_PER_RUN
    print(f"📈 Incremental sales load: {num_sales:,}")

employees_df = client.query(f"SELECT * FROM `{EMPLOYEES_TABLE}`").to_dataframe()
clients_df = client.query(f"SELECT * FROM `{CLIENTS_TABLE}`").to_dataframe()

sales = generate_sales(
    employees_df.to_dict("records"),
    clients_df.to_dict("records"),
    num_sales=num_sales
)

sales_df = pd.DataFrame(sales)
sales_df["Timestamp"] = pd.to_datetime(sales_df["Timestamp"])

append_df(sales_df, SALES_TABLE)

# ---------------- SUMMARY ----------------
print("\n" + "=" * 60)
print("✅ BIGQUERY LOAD COMPLETE")
print("=" * 60)
print(f"Timestamp: {datetime.now()}")
print(f"New Sales: {len(sales_df):,}")
print("=" * 60)
