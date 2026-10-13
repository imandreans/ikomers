from pydantic import BaseModel, Field, EmailStr

class Cart(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class TokenData(BaseModel):
    username: str | None = None

class UpdateCustomer(BaseModel):
    email: EmailStr = Field(default=None)
    address: str=Field(ge=4, max_length=100, description="address's name")
    