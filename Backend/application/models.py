from pydantic import BaseModel, Field
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

DATABASE_URL = "postgres://neondb_owner:npg_f9UzQpMWc3Dr@ep-plain-wind-a1hcrp8w-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"  # Change to PostgreSQL/MySQL URL in production
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    password = Column(String)
    segment = Column(String)
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    country = Column(String)

    orders = relationship('Order', back_populates='customer')


class Order(Base):
    __tablename__ = 'orders'
    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey('customers.id'))
    city = Column(String)
    state = Column(String)
    country = Column(String)
    region = Column(String)
    zipcode = Column(String)
    order_date = Column(Date)
    status = Column(String)
    delivery_status = Column(String)
    late_delivery_risk = Column(Integer)
    shipping_date = Column(Date)
    shipping_mode = Column(String)

    customer = relationship('Customer', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')


class Product(Base):
    __tablename__ = 'products'
    id = Column(String, primary_key=True)
    category_id = Column(String)
    name = Column(String)
    description = Column(String)
    image = Column(String)
    price = Column(Float)
    status = Column(String)
    category_id_ref = Column(String, ForeignKey('categories.id'))
    department_id = Column(String, ForeignKey('departments.id'))

    order_items = relationship('OrderItem', back_populates='product')
    category = relationship('Category', back_populates='products')
    department = relationship('Department', back_populates='products')


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, ForeignKey('orders.id'))
    product_id = Column(String, ForeignKey('products.id'))
    product_price = Column(Float)
    quantity = Column(Integer)
    discount = Column(Float)
    discount_rate = Column(Float)
    profit_ratio = Column(Float)
    sales = Column(Float)
    total = Column(Float)
    profit_per_order = Column(Float)

    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')


class Category(Base):
    __tablename__ = 'categories'
    id = Column(String, primary_key=True)
    name = Column(String)
    products = relationship('Product', back_populates='category')


class Department(Base):
    __tablename__ = 'departments'
    id = Column(String, primary_key=True)
    name = Column(String)
    products = relationship('Product', back_populates='department')
    
    
Base.metadata.create_all(bind=engine)