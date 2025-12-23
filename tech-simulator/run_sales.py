from generator import generate_sales
from sheets_writer import append_df
import pandas as pd

SHEET_ID = "1LZiH-MdlR2k6KcDhvCPUDdzauQTD_qnETpDcK62hdpA"

employees = pd.read_csv("employees.csv")
services = pd.read_csv("services.csv")
clients = pd.read_csv("clients.csv")

sales = generate_sales(employees, services, clients)
append_df(SHEET_ID, "Sales", sales)
