import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# ================= CONFIG ================= #
CONFIG = {
    "EMPLOYEE_MIN": 1000,
    "EMPLOYEE_MAX": 1500,
    "SALES_MIN": 5,
    "SALES_MAX": 20,
    "START_YEAR": 2015,
    "END_YEAR": 2025,
    "CURRENCY": "USD"
}

# ================= UTILITIES ================= #
def random_date(start_year, end_year):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )

def random_syllable():
    consonants = "bcdfghjklmnpqrstvwxyz"
    vowels = "aeiou"
    return random.choice(consonants) + random.choice(vowels)

def generate_name():
    male = random.random() > 0.5
    first = ("Jo" if male else "A") + random_syllable() + ("n" if male else "a")
    last = "Mc" + random_syllable() + random_syllable()
    return f"{first} {last}", ("Male" if male else "Female")

# ================= DEPARTMENTS ================= #
def generate_departments():
    departments = [
        "Engineering", "Platform", "Sales", "Marketing",
        "Product", "Support", "Finance", "HR"
    ]
    return pd.DataFrame([{
        "Department ID": f"DPT-{i+1}",
        "Department Name": name,
        "Annual Budget": random.randint(5_000_000, 15_000_000),
        "Location": "Global",
        "Created Date": random_date(2015, 2020)
    } for i, name in enumerate(departments)])

# ================= SERVICES ================= #
def generate_services():
    services = [
        ("Authentication API", "Security", 500),
        ("Payment Processing", "API", 1200),
        ("Notification Service", "Platform", 300),
        ("Data Analytics API", "Analytics", 2000),
        ("Cloud Storage", "Infrastructure", 1500),
        ("Monitoring Service", "Infrastructure", 800)
    ]

    return pd.DataFrame([{
        "Service ID": f"SVC-{i+1}",
        "Service Name": s[0],
        "Category": s[1],
        "Base Price": s[2],
        "Min Contract": s[2] * 5,
        "Max Contract": s[2] * 50
    } for i, s in enumerate(services)])

# ================= CLIENTS ================= #
def generate_clients(n=200):
    regions = ["NA", "EU", "APAC"]
    return pd.DataFrame([{
        "Client ID": f"CL-{i+1}",
        "Client Name": f"ClientCorp-{i+1}",
        "Region": random.choice(regions)
    } for i in range(n)])

# ================= EMPLOYEES ================= #
def generate_employees():
    count = random.randint(CONFIG["EMPLOYEE_MIN"], CONFIG["EMPLOYEE_MAX"])
    seniority_dist = ["Junior"] * 55 + ["Mid"] * 20 + ["Senior"] * 15 + ["Lead"] * 8 + ["Principal"] * 2

    salary_map = {
        "Junior": 60000,
        "Mid": 90000,
        "Senior": 130000,
        "Lead": 160000,
        "Principal": 190000
    }

    employees = []
    for i in range(count):
        name, gender = generate_name()
        seniority = random.choice(seniority_dist)
        hire_date = random_date(2015, 2023)

        employees.append({
            "Employee ID": f"EMP-{i+1}",
            "Name": name,
            "Gender": gender,
            "Email": name.replace(" ", ".").lower() + "@company.com",
            "Department": "Engineering",
            "Job Title": f"{seniority} Engineer",
            "Seniority": seniority,
            "Status": "Active",
            "Hire Date": hire_date,
            "End Date": None,
            "Salary": salary_map[seniority] + random.randint(0, 20000),
            "Work Setup": random.choice(["Remote", "Hybrid", "Onsite"]),
            "Work Type": "Full-Time",
            "Manager ID": None,
            "Country": "USA",
            "Last Updated": datetime.now()
        })

    return pd.DataFrame(employees)

# ================= SALES ================= #
def generate_sales(employees, services, clients):
    active_sales = employees[employees["Status"] == "Active"]
    rows = []

    for _ in range(random.randint(CONFIG["SALES_MIN"], CONFIG["SALES_MAX"])):
        svc = services.sample(1).iloc[0]
        client = clients.sample(1).iloc[0]
        rep = active_sales.sample(1).iloc[0]

        revenue = random.randint(svc["Min Contract"], svc["Max Contract"])

        rows.append({
            "Sale ID": f"SALE-{int(datetime.now().timestamp())}-{random.randint(100,999)}",
            "Timestamp": datetime.now(),
            "Service": svc["Service Name"],
            "Category": svc["Category"],
            "Client": client["Client Name"],
            "Sales Rep ID": rep["Employee ID"],
            "Contract Type": "Subscription",
            "Duration": random.choice(["Monthly", "Annual", "Multi-Year"]),
            "Revenue": revenue,
            "Currency": CONFIG["CURRENCY"],
            "Region": client["Region"],
            "Is Recurring": True
        })

    return pd.DataFrame(rows)

# ================= RUN ONCE ================= #
if __name__ == "__main__":
    departments = generate_departments()
    services = generate_services()
    clients = generate_clients()
    employees = generate_employees()
    sales = generate_sales(employees, services, clients)

    departments.to_csv("departments.csv", index=False)
    services.to_csv("services.csv", index=False)
    clients.to_csv("clients.csv", index=False)
    employees.to_csv("employees.csv", index=False)
    sales.to_csv("sales.csv", index=False)

    print("Data generation complete.")
