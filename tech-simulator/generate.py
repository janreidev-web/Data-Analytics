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
    """Generate birth date ensuring person is within age range"""
    today = datetime.now()
    birth_year = today.year - random.randint(min_age, max_age)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime(birth_year, month, day)

def random_termination_date(hire_date):
    """
    Generate termination date that is AFTER hire date.
    Ensures minimum 30 days employment and max until today.
    """
    min_term_date = hire_date + timedelta(days=30)
    max_term_date = datetime.now()
    
    if min_term_date > max_term_date:
        return None
    
    time_between = max_term_date - min_term_date
    days_between = time_between.days
    
    if days_between <= 0:
        return None
    
    random_days = random.randrange(days_between)
    return min_term_date + timedelta(days=random_days)

def random_work_setup():
    return random.choices(["Onsite", "Hybrid", "Remote"], weights=[0.3, 0.4, 0.3])[0]

def random_work_type():
    return random.choices(["Full-Time", "Part-Time", "Contractor"], weights=[0.7, 0.2, 0.1])[0]

def random_seniority():
    return random.choices(
        ["Junior", "Mid", "Senior", "Lead", "Principal", "Executive"],
        weights=[0.3, 0.3, 0.2, 0.1, 0.05, 0.05]
    )[0]

def random_salary(seniority):
    base = {
        "Junior": 40000,
        "Mid": 60000,
        "Senior": 90000,
        "Lead": 120000,
        "Principal": 150000,
        "Executive": 200000,
        "Intern": 25000
    }
    return base.get(seniority, 50000) + random.randint(-5000, 5000)

def random_month_date(start_year=2015, end_year=2025):
    """Generate a date at the start of a random month"""
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    return datetime(year, month, 1)

# ----------------- GENERATORS -----------------
def generate_employees(total_employees=1000, num_interns=100):
    employees = []

    print(f"  Generating {total_employees} regular employees...")
    for i in range(total_employees):
        if (i + 1) % 250 == 0:
            print(f"    → Progress: {i+1}/{total_employees}")
            
        gender = random.choice(["male", "female"])
        first_name = fake.first_name_male() if gender == "male" else fake.first_name_female()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        
        hire_date = random_date(2015, 2025)
        birth_date = random_birth_date(min_age=20, max_age=65)
        seniority = random_seniority()
        
        status = random.choices(
            ["Active", "Terminated", "Retired"],
            weights=[0.75, 0.20, 0.05]
        )[0]
        
        term_date = None
        if status in ["Terminated", "Retired"]:
            term_date = random_termination_date(hire_date)
            if term_date is None:
                status = "Active"

        employees.append({
            "Employee ID": f"E{i+1:05}",
            "Full Name": full_name,
            "Gender": gender.title(),
            "Email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "Employment Status": status,
            "Hire Date": hire_date.strftime("%Y-%m-%d"),
            "Termination/Retirement Date": term_date.strftime("%Y-%m-%d") if term_date else "",
            "Birth Date": birth_date.strftime("%Y-%m-%d"),
            "Department": random.choice(["Engineering", "Sales", "Marketing", "Product", "HR", "Finance", "Support"]),
            "Job Title": random.choice(["Engineer", "Manager", "Analyst", "Designer", "Support"]),
            "Seniority Level": seniority,
            "Salary": random_salary(seniority),
            "Work Setup": random_work_setup(),
            "Work Type": random_work_type(),
            "Manager ID": f"E{random.randint(1, total_employees):05}",
            "Country/Location": random.choice(["USA", "UK", "Germany", "India", "Australia", "Canada", "Brazil", "Japan", "Singapore", "France"]),
            "Last Updated Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    print(f"  Generating {num_interns} interns...")
    for j in range(num_interns):
        gender = random.choice(["male", "female"])
        first_name = fake.first_name_male() if gender == "male" else fake.first_name_female()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        
        birth_date = random_birth_date(min_age=20, max_age=25)
        hire_date = random_date(2022, 2025)
        
        status = random.choices(["Active", "Terminated"], weights=[0.7, 0.3])[0]
        
        term_date = None
        if status == "Terminated":
            min_days = 90
            max_days = 365
            potential_term_date = hire_date + timedelta(days=random.randint(min_days, max_days))
            
            if potential_term_date <= datetime.now():
                term_date = potential_term_date
            else:
                status = "Active"

        employees.append({
            "Employee ID": f"I{j+1:04}",
            "Full Name": full_name,
            "Gender": gender.title(),
            "Email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "Employment Status": status,
            "Hire Date": hire_date.strftime("%Y-%m-%d"),
            "Termination/Retirement Date": term_date.strftime("%Y-%m-%d") if term_date else "",
            "Birth Date": birth_date.strftime("%Y-%m-%d"),
            "Department": random.choice(["Engineering", "Sales", "Marketing", "Product", "HR", "Finance", "Support"]),
            "Job Title": "Intern",
            "Seniority Level": "Intern",
            "Salary": random_salary("Intern"),
            "Work Setup": random_work_setup(),
            "Work Type": "Part-Time",
            "Manager ID": f"E{random.randint(1, total_employees):05}",
            "Country/Location": random.choice(["USA", "UK", "Germany", "India", "Australia", "Canada", "Brazil", "Japan", "Singapore", "France"]),
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
            "Founded Date": random_date(1990, 2024).strftime("%Y-%m-%d"),
            "Country/Location": random.choice(["USA", "UK", "Germany", "India", "Australia", "Canada", "Brazil", "Japan", "Singapore", "France"])
        })
    return clients

def generate_sales(employees, clients, num_sales=50, start_sale_id=1):
    """
    Generate sales records with detailed quantifiable values.
    """
    sales = []
    
    print(f"  Generating {num_sales:,} sales transactions...")
    
    # Filter only active employees
    active_employees = [emp for emp in employees if emp.get("Employment Status") == "Active"]
    
    if not active_employees:
        print("  ⚠️  Warning: No active employees found, using all employees")
        active_employees = employees
    
    print(f"  Using {len(active_employees):,} active employees for sales generation")
    
    num_employees = len(active_employees)
    num_clients = len(clients)
    
    # Service pricing tiers
    service_pricing = {
        "Auth API": {"base": 50, "range": (10, 100)},
        "Payment Service": {"base": 100, "range": (50, 200)},
        "Analytics API": {"base": 75, "range": (25, 150)},
        "Messaging API": {"base": 60, "range": (20, 120)}
    }
    
    for i in range(num_sales):
        if num_sales >= 10000 and (i + 1) % 10000 == 0:
            print(f"    → Progress: {i+1:,}/{num_sales:,} ({(i+1)/num_sales*100:.1f}%)")
        
        employee = active_employees[random.randint(0, num_employees - 1)]
        client = clients[random.randint(0, num_clients - 1)]
        
        # Generate sale date
        employee_hire_str = employee.get("Hire Date", "2015-01-01")
        employee_hire = datetime.strptime(employee_hire_str, "%Y-%m-%d")
        
        min_sale_date = employee_hire + timedelta(days=30)
        max_sale_date = datetime.now()
        
        if min_sale_date > max_sale_date:
            sale_date = employee_hire
        else:
            time_between = max_sale_date - min_sale_date
            days_between = max(1, time_between.days)
            random_days = random.randrange(days_between)
            sale_date = min_sale_date + timedelta(days=random_days)
        
        # Service details
        service_name = random.choice(["Auth API", "Payment Service", "Analytics API", "Messaging API"])
        pricing = service_pricing[service_name]
        
        # Quantity and pricing
        quantity = random.randint(1, 100)  # Number of API calls/licenses/units
        unit_cost = round(random.uniform(*pricing["range"]), 2)
        
        # Calculate costs and revenue
        subtotal = round(quantity * unit_cost, 2)
        discount_percent = random.choices([0, 5, 10, 15, 20], weights=[0.4, 0.2, 0.2, 0.15, 0.05])[0]
        discount_amount = round(subtotal * (discount_percent / 100), 2)
        
        # Tax rate varies by region
        tax_rate = random.choice([0, 5, 7.5, 10, 15, 20])  # Different tax rates
        tax_amount = round((subtotal - discount_amount) * (tax_rate / 100), 2)
        
        total_amount = round(subtotal - discount_amount + tax_amount, 2)
        
        # Commission for sales rep (5-15% of total)
        commission_rate = round(random.uniform(5, 15), 2)
        commission_amount = round(total_amount * (commission_rate / 100), 2)
        
        # Handle dict keys
        employee_id = employee.get("Employee ID", "")
        client_id = client.get("Client ID", "")
        client_name = client.get("Client Name", "")
        location = employee.get("Country/Location", "")
        
        sales.append({
            "Sale ID": f"S{start_sale_id + i:06}",
            "Timestamp": sale_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Microservice Name": service_name,
            "Service Category": random.choice(["API", "Platform", "Analytics"]),
            "Client ID": client_id,
            "Client Name": client_name,
            "Sales Rep ID": employee_id,
            "Contract Type": random.choice(["Subscription", "One-Time"]),
            "Contract Duration": random.choice(["Monthly", "Annual", "Quarterly"]),
            "Quantity": quantity,
            "Unit Cost": unit_cost,
            "Subtotal": subtotal,
            "Discount Percent": discount_percent,
            "Discount Amount": discount_amount,
            "Tax Rate": tax_rate,
            "Tax Amount": tax_amount,
            "Total Amount": total_amount,
            "Commission Rate": commission_rate,
            "Commission Amount": commission_amount,
            "Currency": "USD",
            "Region": location,
            "Is Recurring": random.choice([True, False]),
            "Payment Method": random.choice(["Credit Card", "Bank Transfer", "PayPal", "Wire Transfer", "Check"]),
            "Payment Status": random.choices(["Paid", "Pending", "Overdue"], weights=[0.8, 0.15, 0.05])[0]
        })
    
    print(f"  ✓ Generated {num_sales:,} sales transactions")
    return sales

def generate_operating_costs(num_months=120, start_year=2015):
    """
    Generate monthly operating costs from 2015 to present.
    Includes: rent, utilities, salaries, software, marketing, etc.
    """
    costs = []
    
    print(f"  Generating {num_months} months of operating costs...")
    
    # Base costs that will grow over time (inflation ~3% per year)
    base_costs = {
        "Office Rent": 15000,
        "Utilities - Electricity": 2500,
        "Utilities - Water": 500,
        "Utilities - Internet": 1500,
        "Utilities - Phone": 800,
        "Cloud Hosting": 8000,
        "Software Licenses": 5000,
        "Office Supplies": 1200,
        "Equipment & Hardware": 3000,
        "Marketing & Advertising": 10000,
        "Insurance": 2000,
        "Legal & Professional Fees": 3500,
        "Travel & Transportation": 4000,
        "Training & Development": 2500,
        "Maintenance & Repairs": 1500,
        "Security Services": 1000,
        "Cleaning Services": 800,
        "Food & Catering": 2000,
        "Recruitment": 3000,
        "Miscellaneous": 1000
    }
    
    current_date = datetime(start_year, 1, 1)
    
    for i in range(num_months):
        if (i + 1) % 24 == 0:
            print(f"    → Progress: {i+1}/{num_months} months")
        
        # Calculate years elapsed for inflation adjustment
        years_elapsed = (current_date.year - start_year) + (current_date.month / 12)
        inflation_multiplier = (1.03 ** years_elapsed)  # 3% annual inflation
        
        # Generate costs for each category
        for category, base_amount in base_costs.items():
            # Apply inflation
            adjusted_base = base_amount * inflation_multiplier
            
            # Add random variation (±20%)
            variation = random.uniform(0.8, 1.2)
            actual_amount = round(adjusted_base * variation, 2)
            
            # Determine cost type
            if "Utilities" in category or category in ["Office Rent", "Cloud Hosting", "Software Licenses", "Insurance"]:
                cost_type = "Fixed"
            else:
                cost_type = "Variable"
            
            costs.append({
                "Cost ID": f"OC{len(costs)+1:07}",
                "Date": current_date.strftime("%Y-%m-%d"),
                "Year": current_date.year,
                "Month": current_date.month,
                "Month Name": current_date.strftime("%B"),
                "Category": category,
                "Cost Type": cost_type,
                "Amount": actual_amount,
                "Currency": "USD",
                "Vendor": fake.company() if category not in ["Office Rent", "Utilities - Electricity", "Utilities - Water"] else "N/A",
                "Payment Method": random.choice(["Bank Transfer", "Credit Card", "Check", "Direct Debit"]),
                "Payment Status": random.choices(["Paid", "Pending"], weights=[0.95, 0.05])[0],
                "Notes": "",
                "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Move to next month
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        # Stop if we've reached current month
        if current_date > datetime.now():
            break
    
    print(f"  ✓ Generated {len(costs):,} operating cost records")
    return costs
