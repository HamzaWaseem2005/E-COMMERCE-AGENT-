import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("orders.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_name TEXT,
    product_name TEXT,
    quantity INTEGER,
    total_price REAL,
    order_status TEXT,
    order_date TEXT,
    delivery_date TEXT,
    tracking_number TEXT
)
""")

names = ["Ali Khan", "Sara Ahmed", "Bilal Raza", "Ayesha Malik", "Usman Tariq", "Zainab Noor", "Hamza Ali", "Fatima Bibi"]
products = ["Wireless Mouse", "Mechanical Keyboard", "Gaming Headset", "Type-C Cable", "Laptop Stand", "Bluetooth Speaker", "Webcam 1080p"]
statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]

base_date = datetime(2026, 9, 1)

for i in range(1, 101):
    order_id = f"ORD-{1000 + i}"
    customer_name = random.choice(names)
    product_name = random.choice(products)
    quantity = random.randint(1, 3)
    total_price = round(quantity * random.uniform(15.0, 85.0), 2)
    order_status = random.choice(statuses)
    
    o_date = base_date + timedelta(days=random.randint(0, 5))
    d_date = o_date + timedelta(days=random.randint(3, 7))
    
    order_date_str = o_date.strftime("%Y-%m-%d")
    delivery_date_str = d_date.strftime("%Y-%m-%d")
    tracking_number = f"TRK-{random.randint(100000, 999999)}"
    
    cursor.execute("""
    INSERT OR REPLACE INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (order_id, customer_name, product_name, quantity, total_price, order_status, order_date_str, delivery_date_str, tracking_number))

conn.commit()
conn.close()

print("DataBase is successfully created")