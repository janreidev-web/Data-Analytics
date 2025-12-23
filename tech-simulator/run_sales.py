import os
import base64
import json
import gspread
from google.oauth2.service_account import Credentials
from generator import generate_sales

# Read Base64 secret (set as environment variable in GitHub Actions)
service_account_b64 = os.environ.get("GCP_SERVICE_ACCOUNT")
if not service_account_b64:
    raise ValueError("GCP_SERVICE_ACCOUNT environment variable not found")

# Decode JSON credentials
service_account_info = json.loads(base64.b64decode(service_account_b64))

# Authenticate
creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)

# Google Sheet ID
SPREADSHEET_ID = "1LZiH-MdlR2k6KcDhvCPUDdzauQTD_qnETpDcK62hdpA"

# Open sheets
sheet_sales = client.open_by_key(SPREADSHEET_ID).worksheet("Sales")
sheet_employees = client.open_by_key(SPREADSHEET_ID).worksheet("Employees")
sheet_clients = client.open_by_key(SPREADSHEET_ID).worksheet("Clients")

# Read employees and clients
employees = sheet_employees.get_all_records()
employees = [e for e in employees if e["Employment Status"] == "Active"]
clients = sheet_clients.get_all_records()

# Generate new sales
new_sales = generate_sales(employees, clients, num_sales=5)

# Append to sheet
for sale in new_sales:
    sheet_sales.append_row(list(sale.values()))

print(f"{len(new_sales)} sales appended successfully.")
