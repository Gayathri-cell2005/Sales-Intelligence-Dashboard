"""
load_data.py
-------------
Reads sales_data.csv and loads it into the MySQL 'sales' table.
Run this ONCE after setting up the database (setup_database.sql)
to populate it with historical data.
"""

import mysql.connector
import pandas as pd
from config import DB_CONFIG

def load_csv_to_mysql(csv_path="sales_data.csv"):
    # Step 1: Read the CSV using pandas
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")

    # Step 2: Connect to MySQL
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Step 3: Clear existing data (so re-running this script doesn't duplicate rows)
    cursor.execute("TRUNCATE TABLE sales")

    # Step 4: Insert each row
    insert_query = """
        INSERT INTO sales
        (sale_date, product, category, unit_price, quantity, total_amount, region, payment_method, sales_rep)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    rows_to_insert = [
        (
            row.sale_date,
            row.product,
            row.category,
            row.unit_price,
            row.quantity,
            row.total_amount,
            row.region,
            row.payment_method,
            row.sales_rep,
        )
        for row in df.itertuples(index=False)
    ]

    cursor.executemany(insert_query, rows_to_insert)
    conn.commit()
    print(f"Inserted {cursor.rowcount} rows into the 'sales' table.")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    load_csv_to_mysql()