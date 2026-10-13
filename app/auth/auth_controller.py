import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from typing import Annotated

from .auth_model import RegisterRequest, Token, TokenData
from .auth_service import get_current_user, login, register
from ..db.core import connect
from ..customer.service import get_customer_service

router = APIRouter()

@router.post("/login/")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends())-> Token:
    conn = connect()
    return login(conn, form_data)

@router.post("/register/")
def create_customer(customer:RegisterRequest):
    conn = connect()
    return register(conn, customer)

@router.get("/me/")
def read_users_me(
    current_user: Annotated[TokenData, Depends(get_current_user)],
):
    conn = connect()
    current_customer = get_customer_service(conn, current_user.username)
    return {"username": current_customer[1],
            "balance": current_customer[4],
            "address": current_customer[5]}
