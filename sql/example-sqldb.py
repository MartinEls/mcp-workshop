import sqlite3
import random
from datetime import datetime, timedelta

# Create/connect to the database
conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

# Create customers table
cursor.execute('''
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    joined_date TEXT NOT NULL,
    is_premium BOOLEAN DEFAULT 0
)
''')

# Create products table
cursor.execute('''
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    category TEXT NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0
)
''')

# Create orders table
cursor.execute('''
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
)
''')

# Create order_items table
cursor.execute('''
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price_per_unit REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
)
''')

# Sample data
customers = [
    (1, 'John Smith', 'john.smith@example.com', '2023-01-15', 1),
    (2, 'Emma Wilson', 'emma.wilson@example.com', '2023-02-20', 0),
    (3, 'Michael Johnson', 'michael.johnson@example.com', '2023-03-10', 1),
    (4, 'Sarah Brown', 'sarah.brown@example.com', '2023-04-05', 0),
    (5, 'David Lee', 'david.lee@example.com', '2023-05-12', 1),
    (6, 'Jennifer Garcia', 'jennifer.garcia@example.com', '2023-06-18', 0),
    (7, 'Robert Martinez', 'robert.martinez@example.com', '2023-07-22', 1),
    (8, 'Lisa Anderson', 'lisa.anderson@example.com', '2023-08-30', 0),
    (9, 'James Taylor', 'james.taylor@example.com', '2023-09-14', 1),
    (10, 'Patricia Thomas', 'patricia.thomas@example.com', '2023-10-25', 0)
]

products = [
    (1, 'Laptop Pro', 'High-performance laptop for professionals', 1299.99, 'Electronics', 45),
    (2, 'Smartphone X', 'Latest smartphone with advanced features', 799.99, 'Electronics', 120),
    (3, 'Wireless Headphones', 'Noise-cancelling wireless headphones', 199.99, 'Electronics', 75),
    (4, 'Cotton T-shirt', 'Comfortable cotton t-shirt', 24.99, 'Clothing', 200),
    (5, 'Jeans', 'Classic blue jeans', 49.99, 'Clothing', 150),
    (6, 'Running Shoes', 'Lightweight running shoes', 89.99, 'Footwear', 80),
    (7, 'Yoga Mat', 'Non-slip yoga mat', 29.99, 'Fitness', 100),
    (8, 'Blender', 'High-speed blender for smoothies', 69.99, 'Kitchen', 60),
    (9, 'Coffee Maker', 'Programmable coffee maker', 79.99, 'Kitchen', 50),
    (10, 'Desk Lamp', 'Adjustable LED desk lamp', 34.99, 'Home', 90),
    (11, 'Backpack', 'Durable backpack for everyday use', 39.99, 'Accessories', 110),
    (12, 'Water Bottle', 'Insulated stainless steel water bottle', 19.99, 'Accessories', 180)
]

# Insert sample data
cursor.executemany('INSERT INTO customers VALUES (?, ?, ?, ?, ?)', customers)
cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)', products)

# Generate random orders and order items
order_id = 1
order_item_id = 1
orders_data = []
order_items_data = []

# Generate a starting date 6 months ago
start_date = datetime.now() - timedelta(days=180)

for _ in range(50):  # Generate 50 orders
    customer_id = random.randint(1, 10)
    days_offset = random.randint(0, 180)  # Random day within the last 6 months
    order_date = (start_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
    
    # Random number of items per order (1-4)
    num_items = random.randint(1, 4)
    total_amount = 0
    
    # Status options with weights (more completed than others)
    statuses = ['Completed', 'Completed', 'Completed', 'Processing', 'Shipped', 'Cancelled']
    status = random.choice(statuses)
    
    # Create order items
    order_items_for_this_order = []
    
    # Select random products
    selected_products = random.sample(range(1, 13), num_items)
    
    for product_id in selected_products:
        # Find product info
        product = next((p for p in products if p[0] == product_id), None)
        if product:
            quantity = random.randint(1, 3)
            price_per_unit = product[3]  # Price from products data
            item_total = quantity * price_per_unit
            total_amount += item_total
            
            order_items_data.append((order_item_id, order_id, product_id, quantity, price_per_unit))
            order_item_id += 1
    
    # Round total to 2 decimal places
    total_amount = round(total_amount, 2)
    orders_data.append((order_id, customer_id, order_date, total_amount, status))
    order_id += 1

# Insert orders and order items
cursor.executemany('INSERT INTO orders VALUES (?, ?, ?, ?, ?)', orders_data)
cursor.executemany('INSERT INTO order_items VALUES (?, ?, ?, ?, ?)', order_items_data)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database 'ecommerce.db' created successfully with sample data!")