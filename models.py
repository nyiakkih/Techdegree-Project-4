from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine("sqlite:///inventory.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Brands(Base):
    __tablename__ = "brands"

    brand_id = Column(Integer, primary_key=True)
    brand_name = Column(String)
    products = relationship("Product", back_populates="brands")

    def __repr__(self):
        return f"\nBrand ID: {self.brand_id}\nBrand: {self.brand_name}"

class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String)
    product_quantity = Column(Integer)
    product_price = Column(Integer)
    date_updated = Column(Date)
    brand_id = Column(Integer, ForeignKey("brands.brand_id"))
    brands = relationship("Brands", back_populates="products")

    def __repr__(self):
        return f"""
        \nProduct ID: {self.product_id}\r
        Product: {self.product_name}\r
        Quantity: {self.product_quantity}\r
        Price: {self.product_price}\r
        Date: {self.date_updated}\r
        Brand ID: {self.brand_id}
        """

if __name__ == "__main__":
    Base.metadata.create_all(engine)