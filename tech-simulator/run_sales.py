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

from generate import generate_employees, generate_clients, generate_sales
from sheets_writer import append_df

# ---------------- CONFIG ----------------
SPREADSHEET_ID = "1LZiH-MdlR2k6KcDhvCPUDdzauQTD_qnETpDcK62hdpA"
NUM_SALES = 50  # number of sales to generate per run

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
    "Sales Rep ID","Contract Type","Contract Duration","Revenue Amount","Currency","Region","Is Recurring"
]

def normalize_records(records, expected_headers):
    """
    Normalize records from Google Sheets to match expected header format.
    Handles cases where sheet headers might have extra spaces or formatting.
    """
    if not records:
        return records
    
    normalized = []
    for record in records:
        normalized_record = {}
        for expected_header in expected_headers:
            # Try exact match first
            if expected_header in record:
                normalized_record[expected_header] = record[expected_header]
            else:
                # Try to find a match ignoring extra spaces
                for key in record.keys():
                    if key.strip() == expected_header.strip():
                        normalized_record[expected_header] = record[key]
                        break
                # If still not found, set empty value
                if expected_header not in normalized_record:
                    normalized_record[expected_header] = ""
        normalized.append(normalized_record)
    return normalized

# ---------------- CREATE SHEETS IF MISSING ----------------
print("Checking worksheets...")
sheet_titles = [ws.title for ws in spreadsheet.worksheets()]

sheet_employees = (spreadsheet.worksheet("Employees") if "Employees" in sheet_titles 
                   else spreadsheet.add_worksheet("Employees", rows=2000, cols=len(employee_headers)))
sheet_clients = (spreadsheet.worksheet("Clients") if "Clients" in sheet_titles 
                 else spreadsheet.add_worksheet("Clients", rows=500, cols=len(client_headers)))
sheet_sales = (spreadsheet.worksheet("Sales") if "Sales" in sheet_titles 
               else spreadsheet.add_worksheet("Sales", rows=5000, cols=len(sales_headers)))

# ---------------- AUTO-FILL HEADERS ----------------
print("Checking headers...")
if len(sheet_employees.get_all_values()) == 0:
    sheet_employees.append_row(employee_headers)
    print("✓ Added headers to Employees sheet")
    
if len(sheet_clients.get_all_values()) == 0:
    sheet_clients.append_row(client_headers)
    print("✓ Added headers to Clients sheet")
    
if len(sheet_sales.get_all_values()) == 0:
    sheet_sales.append_row(sales_headers)
    print("✓ Added headers to Sales sheet")

# ---------------- READ EXISTING DATA ----------------
print("Reading existing data...")
employees_data = sheet_employees.get_all_records()
clients_data = sheet_clients.get_all_records()

# Normalize the data to ensure correct keys
if employees_data:
    employees_data = normalize_records(employees_data, employee_headers)
if clients_data:
    clients_data = normalize_records(clients_data, client_headers)

# ---------------- AUTO-GENERATE EMPLOYEES IF EMPTY ----------------
if not employees_data:
    print("No employees found. Generating 1100 employees...")
    employees = generate_employees(total_employees=1000, num_interns=100)
    append_df(spreadsheet, "Employees", pd.DataFrame(employees), employee_headers)
    print(f"✓ Generated and saved {len(employees)} employees")
else:
    employees = employees_data
    print(f"✓ Using existing {len(employees)} employees")

# ---------------- AUTO-GENERATE CLIENTS IF EMPTY ----------------
if not clients_data:
    print("No clients found. Generating 200 clients...")
    clients = generate_clients(num_clients=200)
    append_df(spreadsheet, "Clients", pd.DataFrame(clients), client_headers)
    print(f"✓ Generated and saved {len(clients)} clients")
else:
    clients = clients_data
    print(f"✓ Using existing {len(clients)} clients")

# ---------------- GENERATE NEW SALES ----------------
print(f"Generating {NUM_SALES} new sales records...")
new_sales = generate_sales(employees, clients, num_sales=NUM_SALES)
append_df(spreadsheet, "Sales", pd.DataFrame(new_sales), sales_headers)

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"✓ {len(new_sales)} sales appended successfully at {timestamp}")
print("=" * 50)
print("SUMMARY:")
print(f"  Employees: {len(employees)}")
print(f"  Clients: {len(clients)}")
print(f"  New Sales: {len(new_sales)}")
print("=" * 50)
