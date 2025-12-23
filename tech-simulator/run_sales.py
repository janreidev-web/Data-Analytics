import os
import sys
import base64
import json
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime

# Add tech-simulator folder to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from generate import generate_employees, generate_clients, generate_sales, generate_operating_costs
from sheets_writer import append_df

# ---------------- CONFIG ----------------
SPREADSHEET_ID = "1LZiH-MdlR2k6KcDhvCPUDdzauQTD_qnETpDcK62hdpA"

# Configure based on initialization vs ongoing runs
INITIAL_EMPLOYEES = 1000
INITIAL_INTERNS = 100
INITIAL_CLIENTS = 500
INITIAL_SALES = int(os.environ.get('INITIAL_SALES', '10000'))  # Configurable via env var

# For ongoing runs
SALES_PER_RUN = 1000

# --------- Decode Base64 service account ---------
service_account_b64 = os.environ.get("GCP_SERVICE_ACCOUNT")
if not service_account_b64:
    raise ValueError("GCP_SERVICE_ACCOUNT env variable not found")

service_account_info = json.loads(base64.b64decode(service_account_b64))
creds = Credentials.from_service_account_info(
    service_account_info, 
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)

# --------- Open spreadsheet ---------
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# ---------------- HEADERS ----------------
employee_headers = [
    "Employee ID","Full Name","Gender","Email","Employment Status","Hire Date",
    "Termination/Retirement Date","Birth Date","Department","Job Title","Seniority Level",
    "Salary","Work Setup","Work Type","Manager ID","Country/Location","Last Updated Timestamp"
]

client_headers = ["Client ID","Client Name","Founded Date","Country/Location"]

sales_headers = [
    "Sale ID","Timestamp","Microservice Name","Service Category","Client ID","Client Name",
    "Sales Rep ID","Contract Type","Contract Duration","Quantity","Unit Cost","Subtotal",
    "Discount Percent","Discount Amount","Tax Rate","Tax Amount","Total Amount",
    "Commission Rate","Commission Amount","Currency","Region","Is Recurring",
    "Payment Method","Payment Status"
]

operating_cost_headers = [
    "Cost ID","Date","Year","Month","Month Name","Category","Cost Type","Amount",
    "Currency","Vendor","Payment Method","Payment Status","Last Updated"
]

def normalize_records(records, expected_headers):
    """Normalize records from Google Sheets"""
    if not records:
        return records
    
    normalized = []
    for record in records:
        normalized_record = {}
        for expected_header in expected_headers:
            if expected_header in record:
                normalized_record[expected_header] = record[expected_header]
            else:
                for key in record.keys():
                    if key.strip() == expected_header.strip():
                        normalized_record[expected_header] = record[key]
                        break
                if expected_header not in normalized_record:
                    normalized_record[expected_header] = ""
        normalized.append(normalized_record)
    return normalized

def ensure_headers(sheet, headers):
    """Ensure the sheet has proper headers"""
    all_values = sheet.get_all_values()
    
    if len(all_values) == 0:
        sheet.append_row(headers)
        print(f"  → Added headers to '{sheet.title}'")
        return True
    
    first_row = all_values[0] if all_values else []
    
    if first_row != headers:
        sheet.update('A1', [headers])
        print(f"  → Updated headers in '{sheet.title}'")
        return True
    
    return False

def get_next_sale_id(sheet_sales):
    """Get the next Sale ID"""
    all_records = sheet_sales.get_all_records()
    if not all_records:
        return 1
    
    max_id = 0
    for record in all_records:
        sale_id = record.get('Sale ID', '')
        if sale_id and sale_id.startswith('S'):
            try:
                num = int(sale_id[1:])
                max_id = max(max_id, num)
            except:
                pass
    
    return max_id + 1

def append_large_dataset(spreadsheet, sheet_name, df, headers, batch_size=10000):
    """Append large datasets in batches"""
    ws = spreadsheet.worksheet(sheet_name)
    df = df[headers]
    
    total_rows = len(df)
    print(f"  Appending {total_rows:,} rows to '{sheet_name}' in batches of {batch_size:,}...")
    
    for i in range(0, total_rows, batch_size):
        batch_df = df.iloc[i:i+batch_size]
        values = batch_df.values.tolist()
        
        if values:
            ws.append_rows(values, value_input_option='USER_ENTERED')
            print(f"    → Batch {i//batch_size + 1}: Appended {len(values):,} rows ({i+len(values):,}/{total_rows:,})")
    
    print(f"  ✓ Completed appending {total_rows:,} rows to '{sheet_name}'")

# ---------------- CREATE SHEETS IF MISSING ----------------
print("=" * 60)
print("TECH DATA SIMULATOR - COMPREHENSIVE BUSINESS DATA")
print("=" * 60)
print("Checking worksheets...")
sheet_titles = [ws.title for ws in spreadsheet.worksheets()]

sheet_employees = (spreadsheet.worksheet("Employees") if "Employees" in sheet_titles 
                   else spreadsheet.add_worksheet("Employees", rows=5000, cols=len(employee_headers)))
sheet_clients = (spreadsheet.worksheet("Clients") if "Clients" in sheet_titles 
                 else spreadsheet.add_worksheet("Clients", rows=2000, cols=len(client_headers)))
sheet_sales = (spreadsheet.worksheet("Sales") if "Sales" in sheet_titles 
               else spreadsheet.add_worksheet("Sales", rows=500000, cols=len(sales_headers)))
sheet_operating_costs = (spreadsheet.worksheet("Operating Costs") if "Operating Costs" in sheet_titles 
                        else spreadsheet.add_worksheet("Operating Costs", rows=10000, cols=len(operating_cost_headers)))

# ---------------- ENSURE PROPER HEADERS ----------------
print("Ensuring proper headers...")
ensure_headers(sheet_employees, employee_headers)
ensure_headers(sheet_clients, client_headers)
ensure_headers(sheet_sales, sales_headers)
ensure_headers(sheet_operating_costs, operating_cost_headers)

# ---------------- READ EXISTING DATA ----------------
print("Reading existing data...")
employees_data = sheet_employees.get_all_records()
clients_data = sheet_clients.get_all_records()
existing_sales = sheet_sales.get_all_records()
existing_costs = sheet_operating_costs.get_all_records()

# Normalize the data
if employees_data:
    employees_data = normalize_records(employees_data, employee_headers)
if clients_data:
    clients_data = normalize_records(clients_data, client_headers)

# ---------------- AUTO-GENERATE EMPLOYEES ----------------
if not employees_data:
    print(f"\n📊 Generating {INITIAL_EMPLOYEES + INITIAL_INTERNS} employees...")
    employees = generate_employees(total_employees=INITIAL_EMPLOYEES, num_interns=INITIAL_INTERNS)
    append_df(spreadsheet, "Employees", pd.DataFrame(employees), employee_headers)
    print(f"✓ Generated and saved {len(employees)} employees")
else:
    employees = employees_data
    print(f"✓ Using existing {len(employees)} employees")

# ---------------- AUTO-GENERATE CLIENTS ----------------
if not clients_data:
    print(f"\n📊 Generating {INITIAL_CLIENTS} clients...")
    clients = generate_clients(num_clients=INITIAL_CLIENTS)
    append_df(spreadsheet, "Clients", pd.DataFrame(clients), client_headers)
    print(f"✓ Generated and saved {len(clients)} clients")
else:
    clients = clients_data
    print(f"✓ Using existing {len(clients)} clients")

# ---------------- AUTO-GENERATE OPERATING COSTS ----------------
if not existing_costs:
    print(f"\n💰 Generating operating costs (2015-present)...")
    operating_costs = generate_operating_costs(num_months=120, start_year=2015)
    
    costs_df = pd.DataFrame(operating_costs)
    if len(operating_costs) >= 1000:
        append_large_dataset(spreadsheet, "Operating Costs", costs_df, operating_cost_headers, batch_size=5000)
    else:
        append_df(spreadsheet, "Operating Costs", costs_df, operating_cost_headers)
    
    print(f"✓ Generated and saved {len(operating_costs):,} operating cost records")
else:
    print(f"✓ Using existing {len(existing_costs):,} operating cost records")

# ---------------- GENERATE SALES ----------------
if not existing_sales:
    num_sales = INITIAL_SALES
    print(f"\n🚀 INITIAL LOAD: Generating {num_sales:,} sales transactions...")
else:
    num_sales = SALES_PER_RUN
    print(f"\n📈 INCREMENTAL UPDATE: Adding {num_sales:,} new sales...")

next_sale_id = get_next_sale_id(sheet_sales)

print(f"\nGenerating sales data...")
new_sales = generate_sales(employees, clients, num_sales=num_sales, start_sale_id=next_sale_id)

print("Sorting sales by timestamp...")
sales_df = pd.DataFrame(new_sales)
sales_df['Timestamp'] = pd.to_datetime(sales_df['Timestamp'])
sales_df = sales_df.sort_values('Timestamp')
sales_df['Timestamp'] = sales_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

if num_sales >= 10000:
    append_large_dataset(spreadsheet, "Sales", sales_df, sales_headers, batch_size=10000)
else:
    append_df(spreadsheet, "Sales", sales_df, sales_headers)

# ---------------- SUMMARY ----------------
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print("\n" + "=" * 60)
print("✅ EXECUTION COMPLETE")
print("=" * 60)
print(f"Timestamp: {timestamp}")
print(f"Employees: {len(employees):,}")
print(f"Clients: {len(clients):,}")
print(f"Operating Cost Records: {len(existing_costs) if existing_costs else len(operating_costs):,}")
print(f"New Sales: {len(new_sales):,}")
print(f"Sale ID Range: S{next_sale_id:06} - S{next_sale_id + num_sales - 1:06}")
print(f"Total Sales in Sheet: {len(existing_sales) + len(new_sales):,}")
print("=" * 60)
