from pydantic import BaseModel, Field, EmailStr

class RegisterRequest(BaseModel):
    username: str=Field(min_length=4, max_length=100, description="customer's name")
    email: EmailStr = Field(default=None)
    password: str=Field(min_length=4)
    balance: int = Field(ge=0, description="Customer's Balance")
    address: str=Field(min_length=4, max_length=100, description="customer's name")


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    
class CustomerInDB(RegisterRequest):
    hashed_password: str