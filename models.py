from sqlalchemy import (create_engine, Column, 
                        Integer, String, Date)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Brands(Base):
    __tablename__ = 'brands'

    brand_id = Column(Integer, primary_key=True)
    brand_name = Column(String)

    def __repr__(self):
        return f'Brand ID: {self.brand_id} Brand: {self.brand_name}'

class Product(Base):
    __tablename__ = 'product'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    product_quantity = Column(Integer)
    product_price = Column(Integer)
    date_updated = Column(Date)
    brand_id = Column(Integer)

    def __repr__(self):
        return f'Product ID: {self.product_id} Product: {self.product_name} Quantity: {self.product_quantity} Price: {self.product_price} Date: {self.date_updated} Brand ID: {self.brand_id}'