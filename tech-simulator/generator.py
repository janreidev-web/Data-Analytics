import random
from datetime import datetime, timedelta

def generate_sales(employees, clients, num_sales=5):
    """Generate simulated sales data"""
    if not employees or not clients:
        return []

    microservices = [
        {"name": "Authentication API", "category": "API", "base_price": 500},
        {"name": "Payment Processing Service", "category": "Platform", "base_price": 1500},
        {"name": "Notification Service", "category": "API", "base_price": 700},
        {"name": "Data Analytics API", "category": "Analytics", "base_price": 2000},
        {"name": "Cloud Storage Service", "category": "Infrastructure", "base_price": 1200},
        {"name": "Monitoring & Observability Service", "category": "Infrastructure", "base_price": 1000},
    ]

    sales = []
    for i in range(num_sales):
        employee = random.choice(employees)
        client = random.choice(clients)
        service = random.choice(microservices)
        revenue = service["base_price"] * random.randint(1, 5)
        sale_date = datetime.now() - timedelta(days=random.randint(0, 365*5))
        sale = {
            "Sale ID": f"S{random.randint(10000,99999)}",
            "Timestamp": sale_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Microservice Name": service["name"],
            "Service Category": service["category"],
            "Client ID": client.get("Client ID", f"C{random.randint(100,999)}"),
            "Client Name": client.get("Client Name", "Unknown"),
            "Sales Rep ID": employee.get("Employee ID", f"E{random.randint(100,999)}"),
            "Contract Type": random.choice(["Subscription", "One-Time", "Usage-Based"]),
            "Contract Duration": random.choice(["Monthly", "Annual", "Multi-Year"]),
            "Revenue Amount": revenue,
            "Currency": "USD",
            "Region": random.choice(["NA", "EU", "APAC"]),
            "Is Recurring": random.choice([True, False])
        }
        sales.append(sale)
    return sales
