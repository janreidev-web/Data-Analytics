import os
import sys
import base64
import random
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
from google.cloud import bigquery

# ---------------- CONFIG ----------------
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "tech-data-simulator")
DATASET = os.environ.get("BQ_DATASET", "tech_analytics")

EMPLOYEES_TABLE = f"{PROJECT_ID}.{DATASET}.employees"
CLIENTS_TABLE = f"{PROJECT_ID}.{DATASET}.clients"
SALES_TABLE = f"{PROJECT_ID}.{DATASET}.sales"
COSTS_TABLE = f"{PROJECT_ID}.{DATASET}.operating_costs"

INITIAL_EMPLOYEES = 1000
INITIAL_INTERNS = 100
INITIAL_CLIENTS = 500
INITIAL_SALES = int(os.environ.get("INITIAL_SALES", "100000"))
SALES_PER_RUN = 1000

fake = Faker()

# ---------------- AUTH ----------------
if "GCP_SERVICE_ACCOUNT" in os.environ:
    sa_json = base64.b64decode(os.environ["GCP_SERVICE_ACCOUNT"])
    with open("gcp-key.json", "wb") as f:
        f.write(sa_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-key.json"

client = bigquery.Client(project=PROJECT_ID)

# ---------------- HELPERS ----------------
def table_has_data(table_id):
    try:
        df = client.query(f"SELECT COUNT(1) AS cnt FROM `{table_id}`").to_dataframe()
        return df['cnt'][0] > 0
    except Exception:
        return False

def append_df_bq(df, table_id, write_disposition="WRITE_APPEND"):
    job_config = bigquery.LoadJobConfig(write_disposition=write_disposition, autodetect=True)
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"✓ Loaded {len(df):,} rows → {table_id}")

# ---------------- RANDOM GENERATORS ----------------
def random_date(start_year=2015, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end-start).days))

def random_birth_date(min_age=20, max_age=65):
    today = datetime.now()
    birth_year = today.year - random.randint(min_age, max_age)
    return datetime(birth_year, random.randint(1,12), random.randint(1,28))

def random_termination_date(hire_date):
    min_date = hire_date + timedelta(days=30)
    max_date = datetime.now()
    if min_date > max_date:
        return None
    return min_date + timedelta(days=random.randint(0, (max_date-min_date).days))

def random_work_setup():
    return random.choices(["Onsite", "Hybrid", "Remote"], weights=[0.3,0.4,0.3])[0]

def random_work_type():
    return random.choices(["Full-Time", "Part-Time", "Contractor"], weights=[0.7,0.2,0.1])[0]

def random_seniority():
    return random.choices(["Junior","Mid","Senior","Lead","Principal","Executive"],
                          weights=[0.3,0.3,0.2,0.1,0.05,0.05])[0]

def random_salary(seniority):
    base = {"Junior":40000,"Mid":60000,"Senior":90000,"Lead":120000,
            "Principal":150000,"Executive":200000,"Intern":25000}
    return base.get(seniority,50000)+random.randint(-5000,5000)

# ---------------- DATA GENERATORS ----------------
def generate_employees(total_employees=1000, num_interns=100):
    employees = []
    for i in range(total_employees):
        gender = random.choice(["male","female"])
        first = fake.first_name_male() if gender=="male" else fake.first_name_female()
        last = fake.last_name()
        full = f"{first} {last}"
        hire = random_date(2015,2025)
        birth = random_birth_date()
        seniority = random_seniority()
        status = random.choices(["Active","Terminated","Retired"], weights=[0.75,0.2,0.05])[0]
        term = random_termination_date(hire) if status in ["Terminated","Retired"] else None
        if term is None and status!="Active":
            status="Active"
        employees.append({
            "Employee ID": f"E{i+1:05}",
            "Full Name": full,
            "Gender": gender.title(),
            "Email": f"{first.lower()}.{last.lower()}@example.com",
            "Employment Status": status,
            "Hire Date": hire.strftime("%Y-%m-%d"),
            "Termination Date": term.strftime("%Y-%m-%d") if term else "",
            "Birth Date": birth.strftime("%Y-%m-%d"),
            "Department": random.choice(["Engineering","Sales","Marketing","Product","HR","Finance","Support"]),
            "Job Title": random.choice(["Engineer","Manager","Analyst","Designer","Support"]),
            "Seniority Level": seniority,
            "Salary": random_salary(seniority),
            "Work Setup": random_work_setup(),
            "Work Type": random_work_type(),
            "Manager ID": f"E{random.randint(1,total_employees):05}",
            "Country": random.choice(["USA","UK","Germany","India","Australia","Canada","Brazil","Japan","Singapore","France", "Philippines"]),
            "Last Updated Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    for j in range(num_interns):
        gender = random.choice(["male","female"])
        first = fake.first_name_male() if gender=="male" else fake.first_name_female()
        last = fake.last_name()
        full = f"{first} {last}"
        hire = random_date(2022,2025)
        birth = random_birth_date(20,25)
        status = random.choices(["Active","Terminated"], weights=[0.7,0.3])[0]
        term = hire+timedelta(days=random.randint(90,365)) if status=="Terminated" else None
        if term and term>datetime.now(): status="Active"
        employees.append({
            "Employee ID": f"I{j+1:04}",
            "Full Name": full,
            "Gender": gender.title(),
            "Email": f"{first.lower()}.{last.lower()}@example.com",
            "Employment Status": status,
            "Hire Date": hire.strftime("%Y-%m-%d"),
            "Termination/Retirement Date": term.strftime("%Y-%m-%d") if term else "",
            "Birth Date": birth.strftime("%Y-%m-%d"),
            "Department": random.choice(["Engineering","Sales","Marketing","Product","HR","Finance","Support"]),
            "Job Title": "Intern",
            "Seniority Level": "Intern",
            "Salary": random_salary("Intern"),
            "Work Setup": random_work_setup(),
            "Work Type": "Part-Time",
            "Manager ID": f"E{random.randint(1,total_employees):05}",
            "Country": random.choice(["USA","UK","Germany","India","Australia","Canada","Brazil","Japan","Singapore","France", "Phhilippines"]),
            "Last Updated Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return employees

def generate_clients(num_clients=100):
    clients=[]
    for i in range(num_clients):
        clients.append({
            "Client ID": f"C{i+1:03}",
            "Client Name": fake.company(),
            "Founded Date": random_date(1990,2024).strftime("%Y-%m-%d"),
            "Country": random.choice(["USA","UK","Germany","India","Australia","Canada","Brazil","Japan","Singapore","France"])
        })
    return clients

def generate_operating_costs(num_months=120, start_year=2015):
    costs=[]
    base_costs={"Office Rent":15000,"Utilities":5300,"Cloud Hosting":8000,"Software Licenses":5000,
                "Office Supplies":1200,"Equipment & Hardware":3000,"Marketing & Advertising":10000,
                "Insurance":2000,"Legal & Professional Fees":3500,"Travel & Transportation":4000,
                "Training & Development":2500,"Maintenance & Repairs":1500,"Security Services":1000,
                "Cleaning Services":800,"Food & Catering":2000,"Recruitment":3000,"Miscellaneous":1000}
    current=datetime(start_year,1,1)
    for _ in range(num_months):
        years_elapsed = (current.year - start_year) + current.month/12
        inflation = 1.03**years_elapsed
        for cat, amt in base_costs.items():
            actual = round(amt*inflation*random.uniform(0.8,1.2),2)
            cost_type = "Fixed" if cat in ["Utilities","Office Rent","Cloud Hosting","Software Licenses","Insurance"] else "Variable"
            costs.append({
                "Cost ID": f"OC{len(costs)+1:07}",
                "Date": current.strftime("%Y-%m-%d"),
                "Year": current.year,
                "Month": current.month,
                "Month Name": current.strftime("%B"),
                "Category": cat,
                "Cost Type": cost_type,
                "Amount": actual,
                "Currency": "USD",
                "Vendor": fake.company() if cost_type=="Variable" else "N/A",
                "Payment Method": random.choice(["Bank Transfer","Credit Card","Check","Direct Debit"]),
                "Payment Status": random.choices(["Paid","Pending"], weights=[0.95,0.05])[0],
                "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        current += timedelta(days=30)
        if current>datetime.now(): break
    return costs

def generate_sales(employees, clients, num_sales=50):
    sales=[]
    active_emp=[e for e in employees if e["Employment Status"]=="Active"]
    if not active_emp: active_emp=employees
    pricing={"Auth API":(10,100),"Payment Service":(50,200),"Analytics API":(25,150),"Messaging API":(20,120)}
    for i in range(num_sales):
        emp=random.choice(active_emp)
        cli=random.choice(clients)
        hire=datetime.strptime(emp["Hire Date"],"%Y-%m-%d")
        sale_date=hire + timedelta(days=random.randint(30,(datetime.now()-hire).days))
        svc=random.choice(list(pricing.keys()))
        qty=random.randint(1,100)
        unit=round(random.uniform(*pricing[svc]),2)
        subtotal=round(qty*unit,2)
        discount=random.choice([0,5,10,15,20])
        discount_amt=round(subtotal*(discount/100),2)
        tax=random.choice([0,5,7.5,10,15,20])
        tax_amt=round((subtotal-discount_amt)*(tax/100),2)
        total=round(subtotal-discount_amt+tax_amt,2)
        commission=round(total*random.uniform(0.05,0.15),2)
        sales.append({
            "Sale ID": f"S{i+1:06}",
            "Timestamp": sale_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Microservice Name": svc,
            "Service Category": random.choice(["API","Platform","Analytics"]),
            "Client ID": cli["Client ID"],
            "Client Name": cli["Client Name"],
            "Sales Rep ID": emp["Employee ID"],
            "Contract Type": random.choice(["Subscription","One-Time"]),
            "Contract Duration": random.choice(["Monthly","Annual","Quarterly"]),
            "Quantity": qty,
            "Unit Cost": unit,
            "Subtotal": subtotal,
            "Discount Percent": discount,
            "Discount Amount": discount_amt,
            "Tax Rate": tax,
            "Tax Amount": tax_amt,
            "Total Amount": total,
            "Commission Rate": round(random.uniform(5,15),2),
            "Commission Amount": commission,
            "Currency": "USD",
            "Region": emp["Country/Location"],
            "Is Recurring": random.choice([True,False]),
            "Payment Method": random.choice(["Credit Card","Bank Transfer","PayPal","Wire Transfer","Check"]),
            "Payment Status": random.choices(["Paid","Pending","Overdue"], weights=[0.8,0.15,0.05])[0]
        })
    return sales

# ---------------- MAIN ----------------
if __name__=="__main__":
    # Employees
    if not table_has_data(EMPLOYEES_TABLE):
        emps = generate_employees(INITIAL_EMPLOYEES, INITIAL_INTERNS)
        append_df_bq(pd.DataFrame(emps), EMPLOYEES_TABLE)
    else:
        emps_df = client.query(f"SELECT * FROM `{EMPLOYEES_TABLE}`").to_dataframe()
        emps = emps_df.to_dict("records")

    # Clients
    if not table_has_data(CLIENTS_TABLE):
        cls = generate_clients(INITIAL_CLIENTS)
        append_df_bq(pd.DataFrame(cls), CLIENTS_TABLE)
    else:
        cls_df = client.query(f"SELECT * FROM `{CLIENTS_TABLE}`").to_dataframe()
        cls = cls_df.to_dict("records")

    # Operating Costs
    if not table_has_data(COSTS_TABLE):
        costs = generate_operating_costs()
        append_df_bq(pd.DataFrame(costs), COSTS_TABLE)

    # Sales
    num_sales = INITIAL_SALES if not table_has_data(SALES_TABLE) else SALES_PER_RUN
    sales = generate_sales(emps, cls, num_sales)
    append_df_bq(pd.DataFrame(sales), SALES_TABLE)

    print(f"✅ Data load complete at {datetime.now()}")
