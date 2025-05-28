#!/usr/bin/env python3
"""
PostgreSQL Database Setup for SynGen AI
Sets up PostgreSQL database with real data from CSV
"""

import asyncio
import pandas as pd
import os
import logging
from pathlib import Path
from typing import Dict, List, Any
from services.database.postgres_manager import postgres_manager, execute_sql_query

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLSetup:
    def __init__(self):
        """Initialize database setup"""
        self.csv_path = "/mnt/d/Coding/SynGen-ai/Supply_chain_database(dataco-supply-chain-dataset)/DataCoSupplyChainDataset.csv"
        
    async def create_tables(self):
        """Create all required tables in PostgreSQL"""
        logger.info("Creating PostgreSQL tables...")
        
        # Create tables with proper schema
        tables = {
            'customers': '''
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id SERIAL PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT UNIQUE,
                    segment TEXT,
                    city TEXT,
                    state TEXT,
                    country TEXT,
                    zipcode TEXT,
                    sales_per_customer DECIMAL(10,2)
                )
            ''',
            'products': '''
                CREATE TABLE IF NOT EXISTS products (
                    product_id SERIAL PRIMARY KEY,
                    product_name TEXT,
                    category_name TEXT,
                    product_price DECIMAL(10,2),
                    product_status TEXT,
                    department_name TEXT
                )
            ''',
            'orders': '''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    customer_id INTEGER,
                    order_date TEXT,
                    shipping_date TEXT,
                    order_city TEXT,
                    order_state TEXT,
                    order_country TEXT,
                    order_region TEXT,
                    shipping_mode TEXT,
                    delivery_status TEXT,
                    days_for_shipping_real INTEGER,
                    days_for_shipment_scheduled INTEGER,
                    late_delivery_risk INTEGER,
                    order_status TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            ''',
            'order_items': '''
                CREATE TABLE IF NOT EXISTS order_items (
                    order_item_id SERIAL PRIMARY KEY,
                    order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER,
                    product_price DECIMAL(10,2),
                    discount_rate DECIMAL(5,4),
                    sales DECIMAL(10,2),
                    profit_ratio DECIMAL(5,4),
                    total DECIMAL(10,2),
                    FOREIGN KEY (order_id) REFERENCES orders (order_id),
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            '''
        }
        
        for table_name, sql in tables.items():
            try:
                await execute_sql_query(sql)
                logger.info(f"Created table: {table_name}")
            except Exception as e:
                logger.error(f"Error creating table {table_name}: {e}")
                return False
        
        logger.info("All tables created successfully")
        return True
    
    async def load_csv_data(self):
        """Load supply chain data from CSV into PostgreSQL"""
        logger.info("Loading CSV data...")
        
        if not os.path.exists(self.csv_path):
            logger.error(f"CSV file not found: {self.csv_path}")
            return False
        
        try:
            # Read CSV with proper encoding
            df = pd.read_csv(self.csv_path, encoding='latin1')
            logger.info(f"Loaded {len(df)} rows from CSV")
            
            # Process customers
            customers = df[['Customer Id', 'Customer Fname', 'Customer Lname', 'Customer Email', 
                           'Customer Segment', 'Customer City', 'Customer State', 'Customer Country',
                           'Customer Zipcode', 'Sales per customer']].drop_duplicates(subset=['Customer Id'])
            
            customers.columns = ['customer_id', 'first_name', 'last_name', 'email', 'segment',
                               'city', 'state', 'country', 'zipcode', 'sales_per_customer']
            
            # Clear existing data
            await execute_sql_query("TRUNCATE TABLE order_items, orders, customers, products CASCADE")
            
            # Insert customers
            for _, row in customers.iterrows():
                await execute_sql_query("""
                    INSERT INTO customers (customer_id, first_name, last_name, email, segment, city, state, country, zipcode, sales_per_customer)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (customer_id) DO NOTHING
                """, (int(row['customer_id']), row['first_name'], row['last_name'], row['email'], 
                     row['segment'], row['city'], row['state'], row['country'], row['zipcode'], 
                     float(row['sales_per_customer']) if pd.notna(row['sales_per_customer']) else 0.0))
            
            logger.info(f"Loaded {len(customers)} customers")
            
            # Process products
            products = df[['Product Card Id', 'Product Name', 'Category Name', 'Product Price',
                          'Product Status', 'Department Name']].drop_duplicates(subset=['Product Card Id'])
            
            products.columns = ['product_id', 'product_name', 'category_name', 'product_price',
                              'product_status', 'department_name']
            
            # Insert products
            for _, row in products.iterrows():
                await execute_sql_query("""
                    INSERT INTO products (product_id, product_name, category_name, product_price, product_status, department_name)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (product_id) DO NOTHING
                """, (int(row['product_id']), row['product_name'], row['category_name'], 
                     float(row['product_price']) if pd.notna(row['product_price']) else 0.0,
                     row['product_status'], row['department_name']))
            
            logger.info(f"Loaded {len(products)} products")
            
            # Process orders
            orders = df[['Order Id', 'Customer Id', 'order date (DateOrders)', 'shipping date (DateOrders)',
                        'Order City', 'Order State', 'Order Country', 'Order Region', 'Shipping Mode',
                        'Delivery Status', 'Days for shipping (real)', 'Days for shipment (scheduled)',
                        'Late_delivery_risk', 'Order Status']].drop_duplicates(subset=['Order Id'])
            
            orders.columns = ['order_id', 'customer_id', 'order_date', 'shipping_date', 'order_city',
                            'order_state', 'order_country', 'order_region', 'shipping_mode',
                            'delivery_status', 'days_for_shipping_real', 'days_for_shipment_scheduled',
                            'late_delivery_risk', 'order_status']
            
            # Insert orders
            for _, row in orders.iterrows():
                await execute_sql_query("""
                    INSERT INTO orders (order_id, customer_id, order_date, shipping_date, order_city,
                                      order_state, order_country, order_region, shipping_mode,
                                      delivery_status, days_for_shipping_real, days_for_shipment_scheduled,
                                      late_delivery_risk, order_status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    ON CONFLICT (order_id) DO NOTHING
                """, (int(row['order_id']), int(row['customer_id']), row['order_date'], row['shipping_date'],
                     row['order_city'], row['order_state'], row['order_country'], row['order_region'],
                     row['shipping_mode'], row['delivery_status'], 
                     int(row['days_for_shipping_real']) if pd.notna(row['days_for_shipping_real']) else 0,
                     int(row['days_for_shipment_scheduled']) if pd.notna(row['days_for_shipment_scheduled']) else 0,
                     int(row['late_delivery_risk']) if pd.notna(row['late_delivery_risk']) else 0,
                     row['order_status']))
            
            logger.info(f"Loaded {len(orders)} orders")
            
            # Process order items
            order_items = df[['Order Item Id', 'Order Id', 'Product Card Id', 'Order Item Quantity',
                            'Order Item Product Price', 'Order Item Discount Rate', 'Sales',
                            'Order Item Profit Ratio', 'Order Item Total']]
            
            order_items.columns = ['order_item_id', 'order_id', 'product_id', 'quantity',
                                 'product_price', 'discount_rate', 'sales', 'profit_ratio', 'total']
            
            # Insert order items
            for _, row in order_items.iterrows():
                await execute_sql_query("""
                    INSERT INTO order_items (order_item_id, order_id, product_id, quantity,
                                           product_price, discount_rate, sales, profit_ratio, total)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (order_item_id) DO NOTHING
                """, (int(row['order_item_id']), int(row['order_id']), int(row['product_id']),
                     int(row['quantity']) if pd.notna(row['quantity']) else 0,
                     float(row['product_price']) if pd.notna(row['product_price']) else 0.0,
                     float(row['discount_rate']) if pd.notna(row['discount_rate']) else 0.0,
                     float(row['sales']) if pd.notna(row['sales']) else 0.0,
                     float(row['profit_ratio']) if pd.notna(row['profit_ratio']) else 0.0,
                     float(row['total']) if pd.notna(row['total']) else 0.0))
            
            logger.info(f"Loaded {len(order_items)} order items")
            logger.info("CSV data loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            return False
    
    async def verify_data(self):
        """Verify loaded data"""
        logger.info("Verifying loaded data...")
        
        tables = ['customers', 'products', 'orders', 'order_items']
        
        for table in tables:
            try:
                result = await execute_sql_query(f"SELECT COUNT(*) as count FROM {table}")
                count = result[0]['count']
                logger.info(f"{table}: {count:,} records")
            except Exception as e:
                logger.error(f"Error counting {table}: {e}")
        
        try:
            # Test some sample queries
            result = await execute_sql_query("SELECT SUM(sales) as total_sales FROM order_items")
            total_sales = result[0]['total_sales']
            logger.info(f"Total sales: ${total_sales:,.2f}")
            
            result = await execute_sql_query("SELECT COUNT(DISTINCT customer_id) as customer_count FROM customers")
            customer_count = result[0]['customer_count']
            logger.info(f"Unique customers: {customer_count:,}")
            
        except Exception as e:
            logger.error(f"Error running verification queries: {e}")
        
        logger.info("Data verification completed")
    
    async def setup(self):
        """Complete database setup"""
        logger.info("Starting complete PostgreSQL database setup...")
        
        # Initialize the database connection
        await postgres_manager.initialize()
        
        if not await self.create_tables():
            logger.error("❌ Table creation failed")
            return False
        
        if await self.load_csv_data():
            logger.info("✅ CSV data loaded successfully")
        else:
            logger.error("❌ CSV data loading failed")
            return False
        
        await self.verify_data()
        logger.info("🎉 PostgreSQL database setup completed successfully!")
        return True

async def main():
    setup = PostgreSQLSetup()
    await setup.setup()

if __name__ == "__main__":
    asyncio.run(main())