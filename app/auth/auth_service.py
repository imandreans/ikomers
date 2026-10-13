import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
import psycopg2
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from dotenv import load_dotenv
from ..customer.service import get_customer_service
from .auth_model import TokenData, Token, RegisterRequest
from ..db.core import Conn
import os

load_dotenv(override=True)

SECRET_KEY= os.getenv("SECRET_KEY")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

password_hash= PasswordHash.recommended()

DUMMY_HASH=password_hash.hash("dummypassword")

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def authenticate_user(conn: Conn, username: str, plain_password: str):
    customer = get_customer_service(conn, username)
    hashed_password=customer[3] if customer else DUMMY_HASH

    if not customer or not verify_password(plain_password, hashed_password):
        return False
    return customer

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode=data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt=jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(conn: Conn, token):
    credential_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credential_exception
    
    customer = get_customer_service(conn, username=token_data.username)
    if customer is None:
        raise credential_exception
    
    return token_data

security = OAuth2PasswordBearer(tokenUrl="/login/", scopes={})

def get_current_user(conn: Conn, token: str = Depends(security)) -> TokenData:
    return verify_token(conn, token)

CurrentUser = Annotated[TokenData, Depends(get_current_user)]

def login(conn: Conn, form_data:Annotated[OAuth2PasswordRequestForm, Depends()]):
    customer = authenticate_user(conn, form_data.username, form_data.password)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": customer[1], "balance": int(customer[4])}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

def register(conn: Conn, data:RegisterRequest):
    with conn.cursor() as curs:
        try:
            """Should check the email also. Username and email need to be unique value"""
            customer = get_customer_service(conn, data.username)
            if customer:
                raise HTTPException(status_code=409, detail="user has already existed!")
            password = get_password_hash(data.password)
            curs.execute("INSERT INTO customers (username, email, password, balance, address) VALUES ('%s', '%s', '%s', %s, '%s')" % ((data.username), (data.email), (password), (data.balance), (data.address)))
            conn.commit()
            return {"message" : "New user is created successfully"}
        except psycopg2.DatabaseError as error:
            raise HTTPException(status_code=500, detail=str(error))