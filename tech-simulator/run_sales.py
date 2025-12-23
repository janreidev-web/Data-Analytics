import os
import base64
import json
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
from generator import generate_sales
from sheets_writer import append_df

# --------- Config ---------
# Google Sheet ID
SPREADSHEET_ID = "1LZiH-MdlR2k6KcDhvCPUDdzauQTD_qnETpDcK62hdpA"
NUM_SALES = 5

# --------- Decode Base64 service account ---------
service_account_b64 = os.environ.get("GCP_SERVICE_ACCOUNT")
if not service_account_b64:
    raise ValueError("GCP_SERVICE_ACCOUNT env variable not found")

service_account_info = json.loads(base64.b64decode(service_account_b64))
creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)

# --------- Open spreadsheet ---------
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# --------- Setup worksheets ---------
employee_headers = ["Employee ID", "Full Name", "Employment Status", "Department", "Job Title"]
client_headers = ["Client ID", "Client Name"]
sales_headers = [
    "Sale ID", "Timestamp", "Microservice Name", "Service Category", "Client ID", "Client Name",
    "Sales Rep ID", "Contract Type", "Contract Duration", "Revenue Amount", "Currency", "Region", "Is Recurring"
]

sheet_employees = spreadsheet.worksheet("Employees") if "Employees" in [ws.title for ws in spreadsheet.worksheets()] else spreadsheet.add_worksheet("Employees", rows=100, cols=20)
sheet_clients = spreadsheet.worksheet("Clients") if "Clients" in [ws.title for ws in spreadsheet.worksheets()] else spreadsheet.add_worksheet("Clients", rows=100, cols=20)

# --------- Auto-generate headers if empty ---------
if sheet_employees.row_count == 0 or len(sheet_employees.get_all_values()) == 0:
    sheet_employees.append_row(employee_headers)
if sheet_clients.row_count == 0 or len(sheet_clients.get_all_values()) == 0:
    sheet_clients.append_row(client_headers)
sheet_sales = spreadsheet.worksheet("Sales") if "Sales" in [ws.title for ws in spreadsheet.worksheets()] else spreadsheet.add_worksheet("Sales", rows=1000, cols=20)
if sheet_sales.row_count == 0 or len(sheet_sales.get_all_values()) == 0:
    sheet_sales.append_row(sales_headers)

# --------- Read employees and clients ---------
employees = sheet_employees.get_all_records()
employees = [e for e in employees if e.get("Employment Status") == "Active"]
clients = sheet_clients.get_all_records()

# --------- Auto-generate dummy data if empty ---------
if not employees:
    employees = [{"Employee ID": "E001", "Full Name": "John Doe", "Employment Status": "Active", "Department": "Sales", "Job Title": "Sales Rep"}]
if not clients:
    clients = [{"Client ID": "C001", "Client Name": "Acme Corp"}]

# --------- Generate new sales ---------
new_sales = generate_sales(employees, clients, num_sales=NUM_SALES)

# --------- Append to Google Sheet ---------
append_df(spreadsheet, "Sales", pd.DataFrame(new_sales), sales_headers)

print(f"{len(new_sales)} sales appended successfully.")
