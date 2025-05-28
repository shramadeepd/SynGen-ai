#!/usr/bin/env python3
"""
Complete Database Setup for SynGen AI
Sets up SQLite database with real data from CSV and MongoDB for documents
"""

import sqlite3
import pandas as pd
import json
import os
from pathlib import Path
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self, db_path: str = "/mnt/d/Coding/SynGen-ai/syngen_ai.db"):
        """Initialize database setup"""
        self.db_path = db_path
        self.csv_path = "/mnt/d/Coding/SynGen-ai/Supply_chain_database(dataco-supply-chain-dataset)/DataCoSupplyChainDataset.csv"
        self.docs_path = "/mnt/d/Coding/SynGen-ai/Document_Repository(dataco-global-policy-dataset)"
        
    def create_tables(self):
        """Create all required tables"""
        logger.info("Creating database tables...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables with proper schema
        tables = {
            'customers': '''
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT UNIQUE,
                    segment TEXT,
                    city TEXT,
                    state TEXT,
                    country TEXT,
                    zipcode TEXT,
                    sales_per_customer REAL
                )
            ''',
            'products': '''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY,
                    product_name TEXT,
                    category_name TEXT,
                    product_price REAL,
                    product_status TEXT,
                    department_name TEXT
                )
            ''',
            'orders': '''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY,
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
                    order_item_id INTEGER PRIMARY KEY,
                    order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER,
                    product_price REAL,
                    discount_rate REAL,
                    sales REAL,
                    profit_ratio REAL,
                    total REAL,
                    FOREIGN KEY (order_id) REFERENCES orders (order_id),
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            ''',
            'policy_documents': '''
                CREATE TABLE IF NOT EXISTS policy_documents (
                    doc_id INTEGER PRIMARY KEY,
                    filename TEXT,
                    title TEXT,
                    content TEXT,
                    category TEXT,
                    created_at TEXT
                )
            '''
        }
        
        for table_name, sql in tables.items():
            cursor.execute(sql)
            logger.info(f"Created table: {table_name}")
        
        conn.commit()
        conn.close()
        logger.info("All tables created successfully")
    
    def load_csv_data(self):
        """Load supply chain data from CSV"""
        logger.info("Loading CSV data...")
        
        if not os.path.exists(self.csv_path):
            logger.error(f"CSV file not found: {self.csv_path}")
            return False
        
        # Read CSV with proper encoding
        df = pd.read_csv(self.csv_path, encoding='latin1')
        logger.info(f"Loaded {len(df)} rows from CSV")
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Process customers
            customers = df[['Customer Id', 'Customer Fname', 'Customer Lname', 'Customer Email', 
                           'Customer Segment', 'Customer City', 'Customer State', 'Customer Country',
                           'Customer Zipcode', 'Sales per customer']].drop_duplicates(subset=['Customer Id'])
            
            customers.columns = ['customer_id', 'first_name', 'last_name', 'email', 'segment',
                               'city', 'state', 'country', 'zipcode', 'sales_per_customer']
            
            customers.to_sql('customers', conn, if_exists='replace', index=False)
            logger.info(f"Loaded {len(customers)} customers")
            
            # Process products
            products = df[['Product Card Id', 'Product Name', 'Category Name', 'Product Price',
                          'Product Status', 'Department Name']].drop_duplicates(subset=['Product Card Id'])
            
            products.columns = ['product_id', 'product_name', 'category_name', 'product_price',
                              'product_status', 'department_name']
            
            products.to_sql('products', conn, if_exists='replace', index=False)
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
            
            orders.to_sql('orders', conn, if_exists='replace', index=False)
            logger.info(f"Loaded {len(orders)} orders")
            
            # Process order items
            order_items = df[['Order Item Id', 'Order Id', 'Product Card Id', 'Order Item Quantity',
                            'Order Item Product Price', 'Order Item Discount Rate', 'Sales',
                            'Order Item Profit Ratio', 'Order Item Total']]
            
            order_items.columns = ['order_item_id', 'order_id', 'product_id', 'quantity',
                                 'product_price', 'discount_rate', 'sales', 'profit_ratio', 'total']
            
            order_items.to_sql('order_items', conn, if_exists='replace', index=False)
            logger.info(f"Loaded {len(order_items)} order items")
            
            conn.commit()
            logger.info("CSV data loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            return False
        finally:
            conn.close()
    
    def load_policy_documents(self):
        """Load policy documents"""
        logger.info("Loading policy documents...")
        
        if not os.path.exists(self.docs_path):
            logger.error(f"Documents directory not found: {self.docs_path}")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            doc_count = 0
            for file_path in Path(self.docs_path).glob("*.pdf"):
                # For now, just store metadata - in production you'd extract PDF content
                doc_data = {
                    'filename': file_path.name,
                    'title': file_path.stem.replace('_', ' ').title(),
                    'content': f"Policy document: {file_path.stem}. Contains supply chain policies and procedures.",
                    'category': 'policy',
                    'created_at': '2024-01-01'
                }
                
                cursor.execute('''
                    INSERT INTO policy_documents (filename, title, content, category, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (doc_data['filename'], doc_data['title'], doc_data['content'], 
                     doc_data['category'], doc_data['created_at']))
                
                doc_count += 1
            
            conn.commit()
            logger.info(f"Loaded {doc_count} policy documents")
            return True
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            return False
        finally:
            conn.close()
    
    def verify_data(self):
        """Verify loaded data"""
        logger.info("Verifying loaded data...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tables = ['customers', 'products', 'orders', 'order_items', 'policy_documents']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logger.info(f"{table}: {count:,} records")
        
        # Test some sample queries
        cursor.execute("SELECT SUM(sales) FROM order_items")
        total_sales = cursor.fetchone()[0]
        logger.info(f"Total sales: ${total_sales:,.2f}")
        
        cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM customers")
        customer_count = cursor.fetchone()[0]
        logger.info(f"Unique customers: {customer_count:,}")
        
        conn.close()
        logger.info("Data verification completed")
    
    def setup(self):
        """Complete database setup"""
        logger.info("Starting complete database setup...")
        
        self.create_tables()
        
        if self.load_csv_data():
            logger.info("✅ CSV data loaded successfully")
        else:
            logger.error("❌ CSV data loading failed")
            return False
        
        if self.load_policy_documents():
            logger.info("✅ Policy documents loaded successfully")
        else:
            logger.error("❌ Policy documents loading failed")
            return False
        
        self.verify_data()
        logger.info("🎉 Database setup completed successfully!")
        return True

if __name__ == "__main__":
    setup = DatabaseSetup()
    setup.setup()