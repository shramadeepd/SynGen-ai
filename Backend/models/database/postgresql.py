"""
Real database models for DataCo Supply Chain Dataset
Based on the actual CSV structure with 180,519 records
"""
import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, ForeignKey, 
    Boolean, Numeric, DateTime, Text, Index
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://syngen_user:syngen_password@localhost:5432/syngen_ai")

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# ===============================
# NORMALIZED DATABASE MODELS
# ===============================

class PaymentType(Base):
    __tablename__ = 'payment_types'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # DEBIT, TRANSFER, CASH, etc.
    
    orders = relationship('Order', back_populates='payment_type')

class DeliveryStatus(Base):
    __tablename__ = 'delivery_statuses'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # Advance shipping, Late delivery, etc.
    
    orders = relationship('Order', back_populates='delivery_status')

class ShippingMode(Base):
    __tablename__ = 'shipping_modes'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # Standard Class, Express, etc.
    
    orders = relationship('Order', back_populates='shipping_mode')

class OrderStatus(Base):
    __tablename__ = 'order_statuses'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # COMPLETE, PENDING, CLOSED, etc.
    
    orders = relationship('Order', back_populates='order_status')

class Market(Base):
    __tablename__ = 'markets'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # Pacific Asia, Europe, etc.
    
    orders = relationship('Order', back_populates='market')

class CustomerSegment(Base):
    __tablename__ = 'customer_segments'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # Consumer, Home Office, Corporate
    
    customers = relationship('Customer', back_populates='segment')

class Category(Base):
    __tablename__ = 'categories'
    
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    products = relationship('Product', back_populates='category')

class Department(Base):
    __tablename__ = 'departments'
    
    department_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    products = relationship('Product', back_populates='department')

class Country(Base):
    __tablename__ = 'countries'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    customers = relationship('Customer', back_populates='country')
    orders = relationship('Order', back_populates='order_country')

class State(Base):
    __tablename__ = 'states'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)
    
    country = relationship('Country')
    customers = relationship('Customer', back_populates='state')
    orders = relationship('Order', back_populates='order_state')

class Customer(Base):
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(200), index=True)
    password = Column(String(255))  # In real app, this should be hashed
    segment_id = Column(Integer, ForeignKey('customer_segments.id'))
    
    # Address information
    city = Column(String(100))
    country_id = Column(Integer, ForeignKey('countries.id'))
    state_id = Column(Integer, ForeignKey('states.id'))
    street = Column(String(255))
    zipcode = Column(String(20))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    
    # Business metrics
    sales_per_customer = Column(Float)
    
    # Relationships
    segment = relationship('CustomerSegment', back_populates='customers')
    country = relationship('Country', back_populates='customers')
    state = relationship('State', back_populates='customers')
    orders = relationship('Order', back_populates='customer')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_customer_email', 'email'),
        Index('idx_customer_name', 'first_name', 'last_name'),
        Index('idx_customer_location', 'city', 'country_id'),
    )

class Product(Base):
    __tablename__ = 'products'
    
    product_id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, unique=True, index=True)  # Product Card Id
    name = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    price = Column(Float, nullable=False)
    status = Column(Integer)  # 0 or 1 in the data
    category_id = Column(Integer, ForeignKey('categories.category_id'))
    department_id = Column(Integer, ForeignKey('departments.department_id'))
    
    category = relationship('Category', back_populates='products')
    department = relationship('Department', back_populates='products')
    order_items = relationship('OrderItem', back_populates='product')
    
    __table_args__ = (
        Index('idx_product_name', 'name'),
        Index('idx_product_category', 'category_id'),
        Index('idx_product_price', 'price'),
    )

class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    
    # Dates
    order_date = Column(DateTime, nullable=False)
    shipping_date = Column(DateTime)
    
    # Shipping information
    days_for_shipping_real = Column(Integer)
    days_for_shipment_scheduled = Column(Integer)
    late_delivery_risk = Column(Boolean, default=False)
    
    # Financial metrics
    benefit_per_order = Column(Float)
    order_profit_per_order = Column(Float)
    
    # Status and logistics
    payment_type_id = Column(Integer, ForeignKey('payment_types.id'))
    delivery_status_id = Column(Integer, ForeignKey('delivery_statuses.id'))
    shipping_mode_id = Column(Integer, ForeignKey('shipping_modes.id'))
    order_status_id = Column(Integer, ForeignKey('order_statuses.id'))
    market_id = Column(Integer, ForeignKey('markets.id'))
    
    # Order destination
    order_city = Column(String(100))
    order_country_id = Column(Integer, ForeignKey('countries.id'))
    order_state_id = Column(Integer, ForeignKey('states.id'))
    order_region = Column(String(100))
    order_zipcode = Column(String(20))
    
    # Relationships
    customer = relationship('Customer', back_populates='orders')
    payment_type = relationship('PaymentType', back_populates='orders')
    delivery_status = relationship('DeliveryStatus', back_populates='orders')
    shipping_mode = relationship('ShippingMode', back_populates='orders')
    order_status = relationship('OrderStatus', back_populates='orders')
    market = relationship('Market', back_populates='orders')
    order_country = relationship('Country', back_populates='orders')
    order_state = relationship('State', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')
    
    __table_args__ = (
        Index('idx_order_date', 'order_date'),
        Index('idx_order_customer', 'customer_id'),
        Index('idx_order_status', 'order_status_id'),
        Index('idx_order_delivery', 'delivery_status_id'),
    )

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    
    # Pricing and discounts
    product_price = Column(Float)
    discount = Column(Float)
    discount_rate = Column(Float)
    quantity = Column(Integer)
    
    # Financial calculations
    sales = Column(Float)  # Sales amount
    total = Column(Float)  # Order Item Total
    profit_ratio = Column(Float)
    
    # Relationships
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')
    
    __table_args__ = (
        Index('idx_order_item_order', 'order_id'),
        Index('idx_order_item_product', 'product_id'),
    )

class PolicyDocument(Base):
    """Table to store policy documents extracted from PDFs"""
    __tablename__ = 'policy_documents'
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    title = Column(String(500))
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default='policy')
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    file_size = Column(Integer)
    page_count = Column(Integer)
    
    __table_args__ = (
        Index('idx_policy_filename', 'filename'),
        Index('idx_policy_title', 'title'),
        Index('idx_policy_type', 'content_type'),
    )

# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()