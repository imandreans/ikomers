import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from fastapi import APIRouter
from .model import Cart, UpdateCustomer
from ..auth.auth_service import CurrentUser, RegisterRequest
from . import service
from ..db.core import Conn

router = APIRouter(
    prefix="/customer",
    tags=["Customers"]
)

@router.patch("/update/")
def update_customer(conn:Conn, current_user: CurrentUser, customer: UpdateCustomer):
    service.update_customer_service(conn, current_user, customer)

# @router.delete("/delete/{customer_id}")
# def delete_customer(conn:Conn, current_user: CurrentUser):
#     service.delete_customer_service(conn, current_user)

# @router.get("/customers")
# def list_customers(conn:Conn):
#     service.list_customers_service(conn)

@router.get("/ordered_items/")
def get_ordered_items(conn:Conn, current_user: CurrentUser):
    return service.get_ordered_items(conn, current_user)

@router.post("/purchase_items/")
def purchase_items(conn:Conn, current_user: CurrentUser, cart:list[Cart]):
    return service.purcashe_items(conn, current_user, cart)