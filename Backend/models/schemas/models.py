from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, ForeignKey, Boolean, Numeric
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
import datetime

# -------------------------------
# DATABASE & SESSION SETUP
# -------------------------------
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://syngen_user:syngen_password@localhost:5432/syngen_ai")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # remove for true PostgreSQL
)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
Base = declarative_base()

# -------------------------------
# ORM MODELS
# -------------------------------

class Country(Base):
    __tablename__ = 'countries'
    country_id   = Column(Integer, primary_key=True, index=True)
    country_name = Column(String(100), nullable=False)

    states = relationship('State', back_populates='country')


class State(Base):
    __tablename__ = 'states'
    state_id   = Column(Integer, primary_key=True, index=True)
    state_name = Column(String(100), nullable=False)
    region     = Column(String(100))
    country_id = Column(Integer, ForeignKey('countries.country_id'), nullable=False)

    country = relationship('Country', back_populates='states')
    cities  = relationship('City', back_populates='state')


class City(Base):
    __tablename__ = 'cities'
    city_id    = Column(Integer, primary_key=True, index=True)
    city_name  = Column(String(100), nullable=False)
    latitude   = Column(Numeric(9,6))
    longitude  = Column(Numeric(9,6))
    state_id   = Column(Integer, ForeignKey('states.state_id'), nullable=False)

    state     = relationship('State', back_populates='cities')
    addresses = relationship('Address', back_populates='city')


class Address(Base):
    __tablename__ = 'addresses'
    address_id = Column(Integer, primary_key=True, index=True)
    street     = Column(String(255))
    zipcode    = Column(String(20))
    city_id    = Column(Integer, ForeignKey('cities.city_id'), nullable=False)

    city      = relationship('City', back_populates='addresses')
    customers = relationship('Customer', back_populates='address')
    orders    = relationship('Order', back_populates='shipping_address')


class Customer(Base):
    __tablename__ = 'customers'
    customer_id        = Column(Integer, primary_key=True, index=True)
    first_name         = Column(String(50))
    last_name          = Column(String(50))
    email              = Column(String(100), unique=True, index=True)
    password           = Column(String(255))
    segment            = Column(String(50))
    sales_per_customer = Column(Float)
    address_id         = Column(Integer, ForeignKey('addresses.address_id'), nullable=False)

    address = relationship('Address', back_populates='customers')
    orders  = relationship('Order', back_populates='customer')


class PaymentType(Base):
    __tablename__ = 'payment_types'
    payment_type_id = Column(Integer, primary_key=True, index=True)
    name            = Column(String(50), nullable=False)

    orders = relationship('Order', back_populates='payment_type')


class DeliveryStatus(Base):
    __tablename__ = 'delivery_statuses'
    delivery_status_id = Column(Integer, primary_key=True, index=True)
    name               = Column(String(50), nullable=False)

    orders = relationship('Order', back_populates='delivery_status')


class ShippingMode(Base):
    __tablename__ = 'shipping_modes'
    shipping_mode_id = Column(Integer, primary_key=True, index=True)
    name             = Column(String(50), nullable=False)

    orders = relationship('Order', back_populates='shipping_mode')


class Market(Base):
    __tablename__ = 'markets'
    market_id = Column(Integer, primary_key=True, index=True)
    name      = Column(String(100), nullable=False)

    orders = relationship('Order', back_populates='market')


class Category(Base):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)

    products = relationship('Product', back_populates='category')


class Department(Base):
    __tablename__ = 'departments'
    department_id = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)

    products = relationship('Product', back_populates='department')


class Product(Base):
    __tablename__ = 'products'
    product_id    = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    description   = Column(String)
    image_url     = Column(String(255))
    price         = Column(Float, nullable=False)
    status        = Column(String(50))
    category_id   = Column(Integer, ForeignKey('categories.category_id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.department_id'), nullable=False)

    category    = relationship('Category', back_populates='products')
    department  = relationship('Department', back_populates='products')
    order_items = relationship('OrderItem', back_populates='product')


class Order(Base):
    __tablename__ = 'orders'
    order_id            = Column(Integer, primary_key=True, index=True)
    customer_id         = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    order_date          = Column(Date, default=datetime.date.today)
    shipping_date       = Column(Date)
    scheduled_days      = Column(Integer)
    actual_days         = Column(Integer)
    benefit_per_order   = Column(Float)
    late_delivery_risk  = Column(Boolean)
    payment_type_id     = Column(Integer, ForeignKey('payment_types.payment_type_id'), nullable=False)
    delivery_status_id  = Column(Integer, ForeignKey('delivery_statuses.delivery_status_id'), nullable=False)
    shipping_mode_id    = Column(Integer, ForeignKey('shipping_modes.shipping_mode_id'), nullable=False)
    market_id           = Column(Integer, ForeignKey('markets.market_id'))
    shipping_address_id = Column(Integer, ForeignKey('addresses.address_id'), nullable=False)

    customer         = relationship('Customer', back_populates='orders')
    payment_type     = relationship('PaymentType', back_populates='orders')
    delivery_status  = relationship('DeliveryStatus', back_populates='orders')
    shipping_mode    = relationship('ShippingMode', back_populates='orders')
    market           = relationship('Market', back_populates='orders')
    shipping_address = relationship('Address', back_populates='orders')
    order_items      = relationship('OrderItem', back_populates='order')


class OrderItem(Base):
    __tablename__ = 'order_items'
    order_item_id   = Column(Integer, primary_key=True, index=True)
    order_id        = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    product_id      = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    product_price   = Column(Float)
    quantity        = Column(Integer)
    discount_amount = Column(Float)
    discount_rate   = Column(Float)
    sales           = Column(Float)
    total           = Column(Float)
    profit_ratio    = Column(Float)

    order   = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')

# -------------------------------
# CREATE TABLES
# -------------------------------
Base.metadata.create_all(bind=engine)
