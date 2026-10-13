import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from fastapi import APIRouter, status
from .product_model import Product
from . import product_service
from ..db.core import connect

router = APIRouter(
    prefix="/product",
    tags=["Products"]
)

@router.get("/")
def list_products():
    conn = connect()
    return product_service.list_products_service(conn)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(product:Product):
    conn = connect()
    return product_service.add_product_service(conn,product)

@router.patch("/{product_id}")
def update_product(product_id: int, product:Product):
    conn = connect()
    return product_service.update_product_service(conn, product_id, product)

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int):
    conn = connect()
    return product_service.delete_product_service(conn, product_id)
