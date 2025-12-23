import random
from datetime import datetime, timedelta

# Example microservices
MICROSERVICES = [
    {"name": "Authentication API", "category": "API", "base_price": 100},
    {"name": "Payment Processing Service", "category": "Platform", "base_price": 500},
    {"name": "Notification Service", "category": "API", "base_price": 150},
    {"name": "Data Analytics API", "category": "Analytics", "base_price": 1000},
    {"name": "Cloud Storage Service", "category": "Infrastructure", "base_price": 2000},
    {"name": "Monitoring & Observability Service", "category": "Infrastructure", "base_price": 1200},
]

CONTRACT_TYPES = ["Subscription", "One-Time", "Usage-Based"]
CONTRACT_DURATIONS = ["Monthly", "Annual", "Multi-Year"]
CURRENCIES = ["USD", "EUR", "GBP"]
REGIONS = ["North America", "Europe", "Asia-Pacific"]

def generate_sales(employees, clients, num_sales=10):
    """
    Generate a list of simulated sales records.
    employees: list of dicts with active employee IDs
    clients: list of dicts with client IDs
    num_sales: number of sales to generate
    """
    sales = []
    for _ in range(num_sales):
        service = random.choice(MICROSERVICES)
        employee = random.choice(employees)
        client = random.choice(clients)

        sale = {
            "Sale ID": f"S{random.randint(100000,999999)}",
            "Timestamp": (datetime.now() - timedelta(days=random.randint(0, 5))).isoformat(),
            "Microservice Name": service["name"],
            "Service Category": service["category"],
            "Client ID": client["Client ID"],
            "Client Name": client["Client Name"],
            "Sales Rep ID": employee["Employee ID"],
            "Contract Type": random.choice(CONTRACT_TYPES),
            "Contract Duration": random.choice(CONTRACT_DURATIONS),
            "Revenue Amount": round(service["base_price"] * random.uniform(0.8, 2.0), 2),
            "Currency": random.choice(CURRENCIES),
            "Region": random.choice(REGIONS),
            "Is Recurring": random.choice([True, False]),
        }
        sales.append(sale)
    return sales
