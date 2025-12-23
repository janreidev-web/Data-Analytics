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
creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
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

# ---------------- CREATE SHEETS IF MISSING ----------------
sheet_titles = [ws.title for ws in spreadsheet.worksheets()]
sheet_employees = spreadsheet.worksheet("Employees") if "Employees" in sheet_titles else spreadsheet.add_worksheet("Employees", rows=2000, cols=len(employee_headers))
sheet_clients = spreadsheet.worksheet("Clients") if "Clients" in sheet_titles else spreadsheet.add_worksheet("Clients", rows=500, cols=len(client_headers))
sheet_sales = spreadsheet.worksheet("Sales") if "Sales" in sheet_titles else spreadsheet.add_worksheet("Sales", rows=5000, cols=len(sales_headers))

# ---------------- AUTO-FILL HEADERS ----------------
if len(sheet_employees.get_all_values()) == 0:
    sheet_employees.append_row(employee_headers)
if len(sheet_clients.get_all_values()) == 0:
    sheet_clients.append_row(client_headers)
if len(sheet_sales.get_all_values()) == 0:
    sheet_sales.append_row(sales_headers)

# ---------------- READ EXISTING DATA ----------------
employees = sheet_employees.get_all_records()
clients = sheet_clients.get_all_records()

# ---------------- AUTO-GENERATE EMPLOYEES IF EMPTY ----------------
if not employees:
    employees = generate_employees(total_employees=1000, num_interns=100)
    append_df(spreadsheet, "Employees", pd.DataFrame(employees), employee_headers)

# ---------------- AUTO-GENERATE CLIENTS IF EMPTY ----------------
if not clients:
    clients = generate_clients(num_clients=200)
    append_df(spreadsheet, "Clients", pd.DataFrame(clients), client_headers)

# ---------------- GENERATE NEW SALES ----------------
new_sales = generate_sales(employees, clients, num_sales=NUM_SALES)
append_df(spreadsheet, "Sales", pd.DataFrame(new_sales), sales_headers)

print(f"{len(new_sales)} sales appended successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
