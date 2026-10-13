from pydantic import BaseModel, Field

class Product(BaseModel):
    product_name: str=Field(min_length=4, max_length=100, description="Product's name")
    price: int= Field(gt=0, description="Product's price")
    quantity: int=Field(gt=0)
    description: str=Field(min_length=12, max_length=100)
