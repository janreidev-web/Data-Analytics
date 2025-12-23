from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# ----------------- HELPER FUNCTIONS -----------------
def random_date(start_year=2015, end_year=2025):
    """Generate random date between start_year and end_year"""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    
    return start_date + timedelta(days=random_days)

def random_birth_date(min_age=20, max_age=65):
    today = datetime.now()
    birth_year = today.year - random.randint(min_age, max_age)
    month = random.randint(1,12)
    day = random.randint(1,28)
    return datetime(birth_year, month, day)

def random_work_setup():
    return random.choices(["Onsite", "Hybrid", "Remote"], weights=[0.3,0.4,0.3])[0]

def random_work_type():
    return random.choices(["Full-Time","Part-Time","Contractor"], weights=[0.7,0.2,0.1])[0]

def random_seniority():
    return random.choices(
        ["Junior", "Mid", "Senior", "Lead", "Principal", "Executive"],
        weights=[0.3,0.3,0.2,0.1,0.05,0.05]
    )[0]

def random_salary(seniority):
    base = {"Junior":40000, "Mid":60000, "Senior":90000, "Lead":120000, "Principal":150000, "Executive":200000}
    return base.get(seniority,50000) + random.randint(-5000,5000)

# ----------------- GENERATORS -----------------
def generate_employees(total_employees=1000, num_interns=100):
    employees = []

    print(f"  Generating {total_employees} regular employees...")
    for i in range(total_employees):
        if (i + 1) % 250 == 0:
            print(f"    → Progress: {i+1}/{total_employees}")
            
        gender = random.choice(["male", "female"])
        first_name = fake.first_name_male() if gender=="male" else fake.first_name_female()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        hire_date = random_date()
        birth_date = random_birth_date()
        seniority = random_seniority()
        status = random.choices(["Active","Terminated","Retired"], weights=[0.7,0.2,0.1])[0]
        term_date = None
        if status in ["Terminated","Retired"]:
            term_date = random_date(hire_date.year, 2025)

        employees.append({
            "Employee ID": f"E{i+1:05}",
            "Full Name": full_name,
            "Gender": gender.title(),
            "Email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "Employment Status": status,
            "Hire Date": hire_date.strftime("%Y-%m-%d"),
            "Termination/Retirement Date": term_date.strftime("%Y-%m-%d") if term_date else "",
            "Birth Date": birth_date.strftime("%Y-%m-%d"),
            "Department": random.choice(["Engineering","Sales","Marketing","Product","HR","Finance","Support"]),
            "Job Title": random.choice(["Engineer","Manager","Analyst","Designer","Support"]),
            "Seniority Level": seniority,
            "Salary": random_salary(seniority),
            "Work Setup": random_work_setup(),
            "Work Type": random_work_type(),
            "Manager ID": f"E{random.randint(1,total_employees):05}",
            "Country/Location": random.choice(["USA","UK","Germany","India","Australia","Canada","Brazil","Japan","Singapore","France"]),
            "Last Updated Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    print(f"  Generating {num_interns} interns...")
    for j in range(num_interns):
        gender = random.choice(["male", "female"])
        first_name = fake.first_name_male() if gender=="male" else fake.first_name_female()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        birth_date = random_birth_date(min_age=20, max_age=25)
        hire_date = random_date(2022, 2025)

        employees.append({
            "Employee ID": f"I{j+1:04}",
            "Full Name": full_name,
            "Gender": gender.title(),
            "Email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "Employment Status": "Active",
            "Hire Date": hire_date.strftime("%Y-%m-%d"),
            "Termination/Retirement Date": "",
            "Birth Date": birth_date.strftime("%Y-%m-%d"),
            "Department": random.choice(["Engineering","Sales","Marketing","Product","HR","Finance","Support"]),
            "Job Title": "Intern",
            "Seniority Level": "Intern",
            "Salary": random.randint(15000,30000),
            "Work Setup": random_work_setup(),
            "Work Type": "Part-Time",
            "Manager ID": f"E{random.randint(1,total_employees):05}",
            "Country/Location": random.choice(["USA","UK","Germany","India","Australia","Canada","Brazil","Japan","Singapore","France"]),
            "Last Updated Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return employees

def generate_clients(num_clients=50):
    clients = []
    print(f"  Generating {num_clients} clients...")
    for i in range(num_clients):
        if (i + 1) % 100 == 0:
            print(f"    → Progress: {i+1}/{num_clients}")
            
        clients.append({
            "Client ID": f"C{i+1:03}",
            "Client Name": fake.company(),
            "Founded Date": random_date().strftime("%Y-%m-%d"),
            "Country/Location": random.choice(["USA","UK","Germany","India","Australia","Canada","Brazil","Japan","Singapore","France"])
        })
    return clients

def generate_sales(employees, clients, num_sales=50, start_sale_id=1):
    """
    Generate sales records from employees and clients.
    Optimized for large datasets with progress tracking.
    """
    sales = []
    
    print(f"  Generating {num_sales:,} sales transactions...")
    
    # Pre-compute employee and client indices for faster random selection
    num_employees = len(employees)
    num_clients = len(clients)
    
    for i in range(num_sales):
        # Progress indicator for large datasets
        if num_sales >= 10000 and (i + 1) % 10000 == 0:
            print(f"    → Progress: {i+1:,}/{num_sales:,} ({(i+1)/num_sales*100:.1f}%)")
        
        employee = employees[random.randint(0, num_employees - 1)]
        client = clients[random.randint(0, num_clients - 1)]
        sale_date = random_date(2015, 2025)
        
        # Handle dict keys
        employee_id = employee.get("Employee ID", "")
        client_id = client.get("Client ID", "")
        client_name = client.get("Client Name", "")
        location = employee.get("Country/Location", "")
        
        sales.append({
            "Sale ID": f"S{start_sale_id + i:06}",  # Changed to 6 digits for 100k+ sales
            "Timestamp": sale_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Microservice Name": random.choice(["Auth API","Payment Service","Analytics API","Messaging API"]),
            "Service Category": random.choice(["API","Platform","Analytics"]),
            "Client ID": client_id,
            "Client Name": client_name,
            "Sales Rep ID": employee_id,
            "Contract Type": random.choice(["Subscription","One-Time"]),
            "Contract Duration": random.choice(["Monthly","Annual"]),
            "Revenue Amount": round(random.uniform(1000,10000),2),
            "Currency": "USD",
            "Region": location,
            "Is Recurring": random.choice([True, False])
        })
    
    print(f"  ✓ Generated {num_sales:,} sales transactions")
    return sales
