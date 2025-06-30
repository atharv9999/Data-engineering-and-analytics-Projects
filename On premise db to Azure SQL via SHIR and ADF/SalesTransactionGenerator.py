import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

db_config = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "a4$f8#",
    "port": 5432
}

# Connect to PostgreSQL
conn = psycopg2.connect(**db_config)
cur = conn.cursor()

payment_types = ['Cash', 'Card', 'UPI', 'Wallet']
statuses = ['Completed', 'Returned', 'Cancelled']

num_records = 10    #adding new rows to test CDC logic with getting last uploaded time and storing metadata

for _ in range(num_records):
    customer_id = random.randint(1, 50)
    product_id = random.randint(1, 100)
    store_id = random.randint(1, 10)
    quantity = random.randint(1, 10)
    unit_price = round(random.uniform(100, 1000), 2)
    discount = round(random.uniform(0, 20), 2)  # e.g., 12.5%
    gross_total = unit_price * quantity
    discount_amount = gross_total * (discount / 100)
    total_amount = round(gross_total - discount_amount, 2)

    payment_type = random.choice(payment_types)
    status = random.choice(statuses)
    remarks = fake.sentence()
    
    sale_date = fake.date_time_between(start_date='-60d', end_date='now')

    cur.execute("""
        INSERT INTO sales (
            sale_date, customer_id, product_id, store_id,
            quantity, unit_price, discount, total_amount,
            payment_type, status, remarks
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        sale_date, customer_id, product_id, store_id,
        quantity, unit_price, discount, total_amount,
        payment_type, status, remarks
    ))

conn.commit()
cur.close()
conn.close()

print(f"{num_records} fake sales records inserted successfully.")
