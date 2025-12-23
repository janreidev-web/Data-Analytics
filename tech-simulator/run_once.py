from generator import (
    generate_departments,
    generate_services,
    generate_clients,
    generate_employees
)
from sheets_writer import write_df

SHEET_ID = "YOUR_SPREADSHEET_ID"

write_df(SHEET_ID, "Departments", generate_departments())
write_df(SHEET_ID, "Services", generate_services())
write_df(SHEET_ID, "Clients", generate_clients())
write_df(SHEET_ID, "Employees", generate_employees())
