#!/usr/bin/env python3
"""
SynGen AI Data Loader
Loads CSV supply chain data into PostgreSQL database
"""

import pandas as pd
import psycopg2
import psycopg2.extras
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DB_URL = os.getenv("DATABASE_URL", "postgresql://syngen_user:syngen_password@localhost:5432/syngen_ai")

def get_connection():
    """Get database connection"""
    return psycopg2.connect(DB_URL)

def load_csv_data():
    """Load supply chain data from CSV"""
    print("Loading CSV data...")
    
    # Read the CSV file with proper encoding
    csv_path = "/mnt/d/Coding/SynGen-ai/Supply_chain_database(dataco-supply-chain-dataset)/DataCoSupplyChainDataset.csv"
    df = pd.read_csv(csv_path, encoding='latin1')
    
    print(f"Loaded {len(df)} rows from CSV")
    print(f"Columns: {list(df.columns)}")
    
    return df

def create_lookup_tables(conn, df):
    """Create and populate lookup tables"""
    cur = conn.cursor()
    
    # Countries
    print("Creating countries...")
    countries = df['Customer Country'].dropna().unique()
    for i, country in enumerate(countries, 1):
        cur.execute(
            "INSERT INTO countries (country_id, country_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (i, country)
        )
    
    # Get country mapping
    cur.execute("SELECT country_id, country_name FROM countries")
    country_map = {name: id for id, name in cur.fetchall()}
    
    # States
    print("Creating states...")
    states_data = df[['Customer State', 'Customer Country', 'Order Region']].dropna().drop_duplicates()
    state_id = 1
    state_map = {}
    for _, row in states_data.iterrows():
        state_name = row['Customer State']
        country_name = row['Customer Country']
        region = row['Order Region']
        country_id = country_map.get(country_name)
        
        if country_id and state_name not in state_map:
            cur.execute(
                "INSERT INTO states (state_id, state_name, region, country_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (state_id, state_name, region, country_id)
            )
            state_map[state_name] = state_id
            state_id += 1
    
    # Cities
    print("Creating cities...")
    cities_data = df[['Customer City', 'Customer State', 'Latitude', 'Longitude']].dropna().drop_duplicates()
    city_id = 1
    city_map = {}
    for _, row in cities_data.iterrows():
        city_name = row['Customer City']
        state_name = row['Customer State']
        lat = row['Latitude']
        lon = row['Longitude']
        state_id = state_map.get(state_name)
        
        if state_id and city_name not in city_map:
            cur.execute(
                "INSERT INTO cities (city_id, city_name, latitude, longitude, state_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (city_id, city_name, lat, lon, state_id)
            )
            city_map[city_name] = city_id
            city_id += 1
    
    # Categories
    print("Creating categories...")
    categories = df[['Category Id', 'Category Name']].dropna().drop_duplicates()
    for _, row in categories.iterrows():
        cur.execute(
            "INSERT INTO categories (category_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (int(row['Category Id']), row['Category Name'])
        )
    
    # Departments
    print("Creating departments...")
    departments = df[['Department Id', 'Department Name']].dropna().drop_duplicates()
    for _, row in departments.iterrows():
        cur.execute(
            "INSERT INTO departments (department_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (int(row['Department Id']), row['Department Name'])
        )
    
    # Payment Types
    print("Creating payment types...")
    payment_types = df['Type'].dropna().unique()
    for i, ptype in enumerate(payment_types, 1):
        cur.execute(
            "INSERT INTO payment_types (payment_type_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (i, ptype)
        )
    
    # Get payment type mapping
    cur.execute("SELECT payment_type_id, name FROM payment_types")
    payment_map = {name: id for id, name in cur.fetchall()}
    
    # Delivery Statuses
    print("Creating delivery statuses...")
    delivery_statuses = df['Delivery Status'].dropna().unique()
    for i, status in enumerate(delivery_statuses, 1):
        cur.execute(
            "INSERT INTO delivery_statuses (delivery_status_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (i, status)
        )
    
    # Get delivery status mapping
    cur.execute("SELECT delivery_status_id, name FROM delivery_statuses")
    delivery_map = {name: id for id, name in cur.fetchall()}
    
    # Shipping Modes
    print("Creating shipping modes...")
    shipping_modes = df['Shipping Mode'].dropna().unique()
    for i, mode in enumerate(shipping_modes, 1):
        cur.execute(
            "INSERT INTO shipping_modes (shipping_mode_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (i, mode)
        )
    
    # Get shipping mode mapping
    cur.execute("SELECT shipping_mode_id, name FROM shipping_modes")
    shipping_map = {name: id for id, name in cur.fetchall()}
    
    # Markets
    print("Creating markets...")
    markets = df['Market'].dropna().unique()
    for i, market in enumerate(markets, 1):
        cur.execute(
            "INSERT INTO markets (market_id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (i, market)
        )
    
    # Get market mapping
    cur.execute("SELECT market_id, name FROM markets")
    market_map = {name: id for id, name in cur.fetchall()}
    
    conn.commit()
    
    return {
        'country_map': country_map,
        'state_map': state_map, 
        'city_map': city_map,
        'payment_map': payment_map,
        'delivery_map': delivery_map,
        'shipping_map': shipping_map,
        'market_map': market_map
    }

def create_addresses_and_customers(conn, df, mappings):
    """Create addresses and customers"""
    cur = conn.cursor()
    
    print("Creating addresses and customers...")
    
    # Create addresses first
    address_data = df[['Customer Street', 'Customer Zipcode', 'Customer City']].dropna().drop_duplicates()
    address_id = 1
    address_map = {}
    
    for _, row in address_data.iterrows():
        street = row['Customer Street']
        zipcode = row['Customer Zipcode']
        city_name = row['Customer City']
        city_id = mappings['city_map'].get(city_name)
        
        if city_id:
            address_key = f"{street}_{zipcode}_{city_name}"
            if address_key not in address_map:
                cur.execute(
                    "INSERT INTO addresses (address_id, street, zipcode, city_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                    (address_id, street, zipcode, city_id)
                )
                address_map[address_key] = address_id
                address_id += 1
    
    conn.commit()
    
    # Create customers
    customer_data = df[['Customer Id', 'Customer Fname', 'Customer Lname', 'Customer Email', 
                       'Customer Password', 'Customer Segment', 'Sales per customer',
                       'Customer Street', 'Customer Zipcode', 'Customer City']].dropna().drop_duplicates('Customer Id')
    
    for _, row in customer_data.iterrows():
        customer_id = int(row['Customer Id'])
        first_name = row['Customer Fname']
        last_name = row['Customer Lname']
        email = row['Customer Email'] if row['Customer Email'] != 'XXXXXXXXX' else f"customer{customer_id}@example.com"
        password = row['Customer Password'] if row['Customer Password'] != 'XXXXXXXXX' else 'password123'
        segment = row['Customer Segment']
        sales_per_customer = float(row['Sales per customer']) if pd.notna(row['Sales per customer']) else None
        
        # Get address
        address_key = f"{row['Customer Street']}_{row['Customer Zipcode']}_{row['Customer City']}"
        address_id = address_map.get(address_key)
        
        if address_id:
            cur.execute(
                """INSERT INTO customers (customer_id, first_name, last_name, email, password, 
                   segment, sales_per_customer, address_id) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (customer_id, first_name, last_name, email, password, segment, sales_per_customer, address_id)
            )
    
    conn.commit()

def create_products(conn, df):
    """Create products"""
    cur = conn.cursor()
    
    print("Creating products...")
    
    product_data = df[['Product Card Id', 'Product Name', 'Product Description', 'Product Image',
                      'Product Price', 'Product Status', 'Product Category Id', 'Department Id']].dropna().drop_duplicates('Product Card Id')
    
    for _, row in product_data.iterrows():
        product_id = int(row['Product Card Id'])
        name = row['Product Name']
        description = row['Product Description'] if pd.notna(row['Product Description']) else None
        image_url = row['Product Image'] if pd.notna(row['Product Image']) else None
        price = float(row['Product Price']) if pd.notna(row['Product Price']) else 0.0
        status = row['Product Status'] if pd.notna(row['Product Status']) else 'Available'
        category_id = int(row['Product Category Id'])
        department_id = int(row['Department Id'])
        
        cur.execute(
            """INSERT INTO products (product_id, name, description, image_url, price, status, 
               category_id, department_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
            (product_id, name, description, image_url, price, status, category_id, department_id)
        )
    
    conn.commit()

def create_orders_and_items(conn, df, mappings):
    """Create orders and order items"""
    cur = conn.cursor()
    
    print("Creating orders and order items...")
    
    # Group by order to create orders first
    order_groups = df.groupby('Order Id')
    
    for order_id, order_group in order_groups:
        order_row = order_group.iloc[0]  # Get first row for order details
        
        customer_id = int(order_row['Order Customer Id'])
        order_date = pd.to_datetime(order_row['order date (DateOrders)']).date()
        shipping_date = pd.to_datetime(order_row['shipping date (DateOrders)']).date() if pd.notna(order_row['shipping date (DateOrders)']) else None
        scheduled_days = int(order_row['Days for shipment (scheduled)']) if pd.notna(order_row['Days for shipment (scheduled)']) else None
        actual_days = int(order_row['Days for shipping (real)']) if pd.notna(order_row['Days for shipping (real)']) else None
        benefit_per_order = float(order_row['Benefit per order']) if pd.notna(order_row['Benefit per order']) else None
        late_delivery_risk = bool(order_row['Late_delivery_risk']) if pd.notna(order_row['Late_delivery_risk']) else False
        
        # Get foreign key IDs
        payment_type_id = mappings['payment_map'].get(order_row['Type'])
        delivery_status_id = mappings['delivery_map'].get(order_row['Delivery Status'])
        shipping_mode_id = mappings['shipping_map'].get(order_row['Shipping Mode'])
        market_id = mappings['market_map'].get(order_row['Market'])
        
        # Use customer address as shipping address for simplicity
        cur.execute("SELECT address_id FROM customers WHERE customer_id = %s", (customer_id,))
        result = cur.fetchone()
        shipping_address_id = result[0] if result else None
        
        if all([payment_type_id, delivery_status_id, shipping_mode_id, shipping_address_id]):
            # Insert order
            cur.execute(
                """INSERT INTO orders (order_id, customer_id, order_date, shipping_date, scheduled_days,
                   actual_days, benefit_per_order, late_delivery_risk, payment_type_id, delivery_status_id,
                   shipping_mode_id, market_id, shipping_address_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (order_id, customer_id, order_date, shipping_date, scheduled_days, actual_days,
                 benefit_per_order, late_delivery_risk, payment_type_id, delivery_status_id,
                 shipping_mode_id, market_id, shipping_address_id)
            )
            
            # Insert order items
            for _, item_row in order_group.iterrows():
                try:
                    order_item_id = int(item_row['Order Item Id'])
                    product_id = int(item_row['Order Item Cardprod Id'])
                    
                    # Check if product exists first
                    cur.execute("SELECT 1 FROM products WHERE product_id = %s", (product_id,))
                    if not cur.fetchone():
                        print(f"Warning: Product {product_id} not found, skipping order item {order_item_id}")
                        continue
                    
                    product_price = float(item_row['Order Item Product Price']) if pd.notna(item_row['Order Item Product Price']) else None
                    quantity = int(item_row['Order Item Quantity']) if pd.notna(item_row['Order Item Quantity']) else 1
                    discount_amount = float(item_row['Order Item Discount']) if pd.notna(item_row['Order Item Discount']) else 0.0
                    discount_rate = float(item_row['Order Item Discount Rate']) if pd.notna(item_row['Order Item Discount Rate']) else 0.0
                    sales = float(item_row['Sales']) if pd.notna(item_row['Sales']) else None
                    total = float(item_row['Order Item Total']) if pd.notna(item_row['Order Item Total']) else None
                    profit_ratio = float(item_row['Order Item Profit Ratio']) if pd.notna(item_row['Order Item Profit Ratio']) else None
                    
                    cur.execute(
                        """INSERT INTO order_items (order_item_id, order_id, product_id, product_price,
                           quantity, discount_amount, discount_rate, sales, total, profit_ratio)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                        (order_item_id, order_id, product_id, product_price, quantity, discount_amount,
                         discount_rate, sales, total, profit_ratio)
                    )
                except Exception as e:
                    print(f"Error inserting order item {item_row.get('Order Item Id', 'unknown')}: {e}")
                    continue
    
    conn.commit()

def main():
    """Main function to load all data"""
    try:
        # Load CSV data
        df = load_csv_data()
        
        # Connect to database
        print("Connecting to database...")
        conn = get_connection()
        
        # Create lookup tables
        mappings = create_lookup_tables(conn, df)
        
        # Create addresses and customers
        create_addresses_and_customers(conn, df, mappings)
        
        # Create products
        create_products(conn, df)
        
        # Create orders and order items
        create_orders_and_items(conn, df, mappings)
        
        print("Data loading completed successfully!")
        
        # Print some statistics
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM customers")
        print(f"Customers loaded: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM products")
        print(f"Products loaded: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM orders")
        print(f"Orders loaded: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM order_items")
        print(f"Order items loaded: {cur.fetchone()[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

if __name__ == "__main__":
    main()