from sqlalchemy import Column, Integer, String, Float
from database import Base

class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(String)
    url = Column(String)
