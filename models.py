from pydantic import BaseModel
from typing import List, Optional

# Comment: Data model for products
class Product(BaseModel):
    title: str
    price: Optional[str]
    url: Optional[str]

# Comment: Data model for brand insights response
class BrandInsights(BaseModel):
    product_catalog: List[Product]
    hero_products: List[Product]
    privacy_policy: Optional[str]
    refund_policy: Optional[str]
    faqs: List[str]
    social_handles: List[str]
    contact_details: List[str]
    about_text: Optional[str]
    important_links: List[str]
