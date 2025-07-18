from sqlalchemy.orm import Session
from models_db import ProductDB
from models import Product

def save_products(db: Session, products: list[Product]):
    for p in products:
        db_product = ProductDB(title=p.title, price=p.price, url=p.url)
        db.add(db_product)
    db.commit()
