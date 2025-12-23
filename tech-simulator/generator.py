from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# ---------- Helper functions ----------
def random_hire_date(start_year=2015, end_year=2025):
    year = random.randint(start_year, end_year)
    month = random.randint(1,12)
    day = random.randint(1,28)
    return datetime(year, month, day)

def random_birth_date(min_age=22, max_age=65):
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

def random_address():
    return fake.address().replace("\n", ", ")

# ---------- Employee Generator ----------
def generate_employees(num=100):
    employees = []
    for i in range(num):
        gender = random.choice(["male", "female"])
        first_name = fake.first_name_male() if gender=="male" else fake.first_name_female()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        
        hire_date = random_hire_date()
        birth_date = random_birth_date()
        seniority = random_seniority()
        status = random.choices(
            ["Active", "Terminated", "Retired"],
            weights=[0.7,0.2,0.1],
            k=1
        )[0]
        term_date = None
        if status in ["Terminated","Retired"]:
            term_year = random.randint(hire_date.year, 2025)
            term_date = datetime(term_year, random.randint(1,12), random.randint(1,28))
        
        employees.append({
            "Employee ID": f"E{i+1:04}",
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
            "Manager ID": f"E{random.randint(1,num):04}",
            "Country/Location": random_address(),
            "Last Updated Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return employees
