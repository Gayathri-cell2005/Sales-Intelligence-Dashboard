"""
generate_live_sales.py
------------------------
Simulates a live stream of incoming sales.
Run this in its own terminal window — it will keep inserting a new
random sale into MySQL every few seconds, forever (until you stop it
with Ctrl+C). Keep this running WHILE your Streamlit dashboard is open
so you can watch the numbers update live.

This is the "real-time" part of the project: in a real company this
script would be replaced by an actual point-of-sale system sending
live transactions. Here, we simulate that behavior.
"""

import time
import random
from datetime import datetime
import mysql.connector
from config import DB_CONFIG

# Same reference data used to build the original dataset, so new
# "live" sales look consistent with the historical data.
PRODUCTS = {
    "Laptop": ("Electronics", 55000),
    "Smartphone": ("Electronics", 25000),
    "Headphones": ("Electronics", 2000),
    "Smartwatch": ("Electronics", 6000),
    "Office Chair": ("Furniture", 7500),
    "Study Table": ("Furniture", 5500),
    "Bookshelf": ("Furniture", 4000),
    "Running Shoes": ("Fashion", 3200),
    "T-Shirt": ("Fashion", 800),
    "Backpack": ("Fashion", 1800),
    "Coffee Maker": ("Appliances", 3500),
    "Microwave Oven": ("Appliances", 8500),
    "Air Fryer": ("Appliances", 6500),
    "Notebook Set": ("Stationery", 250),
    "Pen Pack": ("Stationery", 100),
}
REGIONS = ["North", "South", "East", "West"]
PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]
SALES_REPS = ["Aarav", "Diya", "Rohan", "Priya", "Karan", "Sneha", "Vikram", "Anjali"]


def generate_one_sale():
    product = random.choice(list(PRODUCTS.keys()))
    category, base_price = PRODUCTS[product]
    price = round(base_price * random.uniform(0.9, 1.1), 2)
    quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 12, 8, 5])[0]

    return {
        "sale_date": datetime.now(),
        "product": product,
        "category": category,
        "unit_price": price,
        "quantity": quantity,
        "total_amount": round(price * quantity, 2),
        "region": random.choice(REGIONS),
        "payment_method": random.choice(PAYMENT_METHODS),
        "sales_rep": random.choice(SALES_REPS),
    }


def run_simulation(interval_seconds=5):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO sales
        (sale_date, product, category, unit_price, quantity, total_amount, region, payment_method, sales_rep)
        VALUES (%(sale_date)s, %(product)s, %(category)s, %(unit_price)s, %(quantity)s,
                %(total_amount)s, %(region)s, %(payment_method)s, %(sales_rep)s)
    """

    print("Starting live sales simulation. Press Ctrl+C to stop.\n")
    try:
        while True:
            sale = generate_one_sale()
            cursor.execute(insert_query, sale)
            conn.commit()
            print(
                f"[{sale['sale_date'].strftime('%H:%M:%S')}] New sale -> "
                f"{sale['product']} x{sale['quantity']} = Rs.{sale['total_amount']} ({sale['region']})"
            )
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nStopping simulation.")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_simulation(interval_seconds=5)