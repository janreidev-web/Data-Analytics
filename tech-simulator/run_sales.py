import os
import base64
import json
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
from faker import Faker
import random
from datetime import datetime
from generator import generate_sales  # This will now use our updated generator
from sheets_writer import append_df

fake = Faker()

# ----------------- Config -----------------
SPREADSHEET_ID = "1LZiH-MdlR2k6KcDhvCPUDdzauQTD_qnETpDcK62hdpA"
NUM_SALES = 5

# ----------------- Decode Base64 service account -----------------
service_account_b64 = os.environ.get("GCP_SERVICE_ACCOUNT")
if not service_account_b64:
    raise ValueError("GCP_SERVICE_ACCOUNT env variable not found")

service_account_info = json.loads(base64.b64decode(service_account_b64))
creds = Credentials.from_service_account_info(service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)

# ----------------- Open spreadsheet -----------------
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# ----------------- Headers -----------------
employee_headers = [
    "Employee ID", "Full Name", "Gender", "Email", "Employment Status", "Hire Date",
    "Termination/Retirement Date", "Birth Date", "Department", "Job Title", "Seniority Level",
    "Salary", "Work Setup", "Work Type", "Manager ID", "Country/Location", "Last Updated Timestamp"
]
client_headers = ["Client ID", "Client Name"]
sales_headers = [
    "Sale ID", "Timestamp", "Microservice Name", "Service Category", "Client ID", "Client Name",
    "Sales Rep ID", "Contract Type", "Contract Duration", "Revenue Amount", "Currency", "Region", "Is Recurring"
]

# ----------------- Create sheets if not exist -----------------
sheet_employees = spreadsheet.worksheet("Employees") if "Employees" in [ws.title for ws in spreadsheet.worksheets()] else spreadsheet.add_worksheet("Employees", rows=200, cols=len(employee_headers))
sheet_clients = spreadsheet.worksheet("Clients") if "Clients" in [ws.title for ws in spreadsheet.worksheets()] else spreadsheet.add_worksheet("Clients", rows=50, cols=len(client_headers))
sheet_sales = spreadsheet.worksheet("Sales") if "Sales" in [ws.title for ws in spreadsheet.worksheets()] else spreadsheet.add_worksheet("Sales", rows=1000, cols=len(sales_headers))

# ----------------- Auto-fill headers if empty -----------------
if len(sheet_employees.get_all_values()) == 0:
    sheet_employees.append_row(employee_headers)
if len(sheet_clients.get_all_values()) == 0:
    sheet_clients.append_row(client_headers)
if len(sheet_sales.get_all_values()) == 0:
    sheet_sales.append_row(sales_headers)

# ----------------- Read employees and clients -----------------
employees = sheet_employees.get_all_records()
employees = [e for e in employees if e.get("Employment Status") == "Active"]

clients = sheet_clients.get_all_records()

# ----------------- Auto-generate dummy employees if empty -----------------
if not employees:
    employees = []
    for i in range(50):  # Generate 50 employees
        gender = random.choice(["male", "female"])
        first_name = fake.first_name_male() if gender=="male" else fake.first_name_female()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        hire_date = fake.date_between(start_date='-10y', end_date='today')
        birth_date = fake.date_of_birth(minimum_age=22, maximum_age=65)
        seniority = random.choice(["Junior","Mid","Senior","Lead","Executive"])
        status = "Active"
        employees.append({
            "Employee ID": f"E{i+1:04}",
            "Full Name": full_name,
            "Gender": gender.title(),
            "Email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "Employment Status": status,
            "Hire Date": hire_date.strftime("%Y-%m-%d"),
            "Termination/Retirement Date": "",
            "Birth Date": birth_date.strftime("%Y-%m-%d"),
            "Department": random.choice(["Sales","Engineering","Marketing","Product","HR","Finance","Support"]),
            "Job Title": random.choice(["Manager","Analyst","Engineer","Designer","Support"]),
            "Seniority Level": seniority,
            "Salary": random.randint(40000,200000),
            "Work Setup": random.choice(["Onsite","Hybrid","Remote"]),
            "Work Type": random.choice(["Full-Time","Part-Time","Contractor"]),
            "Manager ID": f"E{random.randint(1,50):04}",
            "Country/Location": fake.address().replace("\n",", "),
            "Last Updated Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    append_df(spreadsheet, "Employees", pd.DataFrame(employees), employee_headers)

# ----------------- Auto-generate clients if empty -----------------
if not clients:
    clients = []
    for i in range(20):
        clients.append({
            "Client ID": f"C{i+1:03}",
            "Client Name": fake.company()
        })
    append_df(spreadsheet, "Clients", pd.DataFrame(clients), client_headers)

# ----------------- Generate new sales -----------------
new_sales = generate_sales(employees, clients, num_sales=NUM_SALES)

# ----------------- Append sales -----------------
append_df(spreadsheet, "Sales", pd.DataFrame(new_sales), sales_headers)

print(f"{len(new_sales)} sales appended successfully.")
