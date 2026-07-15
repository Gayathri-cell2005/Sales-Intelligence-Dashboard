"""
setup_cloud_db.py
-------------------
One-time script to create the 'sales' table schema on the Aiven cloud
MySQL instance (inside the existing 'defaultdb' database).

Run this once: python setup_cloud_db.py
"""

import mysql.connector
from config import DB_CONFIG

statements = [
    """
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INT PRIMARY KEY AUTO_INCREMENT,
        sale_date DATETIME NOT NULL,
        product VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        unit_price DECIMAL(10, 2) NOT NULL,
        quantity INT NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        region VARCHAR(50) NOT NULL,
        payment_method VARCHAR(50) NOT NULL,
        sales_rep VARCHAR(100) NOT NULL
    )
    """,
    "CREATE INDEX idx_sale_date ON sales(sale_date)",
    "CREATE INDEX idx_region ON sales(region)",
    "CREATE INDEX idx_category ON sales(category)",
]

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

for stmt in statements:
    print(f"Running: {stmt.strip()[:60]}...")
    cursor.execute(stmt)

conn.commit()
cursor.close()
conn.close()
print("\n✅ 'sales' table created successfully on Aiven MySQL (defaultdb).")