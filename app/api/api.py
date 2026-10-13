from fastapi import FastAPI
from ..auth.auth_controller import router as auth_router
from ..product.product_controller import router as product_router
from ..customer.controller import router as customer_router

def register_routers(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(product_router)
    app.include_router(customer_router)
    