import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import psycopg2
from psycopg2 import sql
from datetime import datetime 
from .product_model import Product
from fastapi import HTTPException
from ..customer.service import get_customer_service

"""
For Create, UPDATE, and DELETE executions, make sure the data is exist
"""

def list_products_service(conn):
    with conn.cursor() as curs:
        try:
            curs.execute("""
                SELECT product_id,
                       product_name,
                       price,
                       description,
                       quantity
                FROM products
            """)
            columns = [column[0] for column in curs.description]
            all_products = [
                dict(zip(columns, product))
                for product in curs.fetchall()
            ]
            return {"data": all_products}
        except psycopg2.DatabaseError as error:
            raise HTTPException(status_code=500, detail=str(error))

def get_product_service(conn, product_id):
    with conn.cursor() as curs:
        try:
            curs.execute("SELECT * FROM products WHERE product_id=%s" % product_id)
            product=curs.fetchone()
            return product
        except psycopg2.DatabaseError as error:
            raise HTTPException(status_code=500, detail=str(error))

def add_product_service(conn, data: Product):
    with conn.cursor() as curs:
        try:
            curs.execute(f"INSERT INTO products (title, description, price, quantity) VALUES (%s, %s, %s, %s)" % ((data.product_name), (data.description), (data.price), (data.quantity)))
            conn.commit()

            return { "message": "product is added successfully"}
        except psycopg2.DatabaseError as error:
            raise HTTPException(status_code=500, detail=str(error))

def update_product_service(conn,product_id:int, data:Product):
    new_update= data.model_dump(exclude_unset=True)

    product = get_customer_service(conn, product_id)
    if product == None:
        raise HTTPException(status_code=404, detail="Customer not found")
    update_query = sql.SQL("UPDATE products SET {data} WHERE product_id = {id}").format(
    data=sql.SQL(', ').join(
        sql.Composed([sql.Identifier(k), sql.SQL(" = "), sql.Placeholder(k)]) for k in new_update.keys()
    ),
    id=sql.Placeholder('product_id'))
    params={**new_update, "product_id":product_id}
    with conn.cursor() as curs:
            try:
                curs.execute(update_query, params)
                conn.commit()
            except psycopg2.DatabaseError as error:
                raise HTTPException(status_code=500, detail=str(error))

def delete_product_service(conn, product_id):
    with conn.cursor() as curs:
        product = get_customer_service(conn, product_id)
        if product == None:
            raise HTTPException(status_code=404, detail="Product not found")
        try:
            curs.execute("DELETE FROM products WHERE product_id=%s" % (product_id))
            conn.commit()
        except psycopg2.DatabaseError as error:
            raise HTTPException(status_code=500, detail=str(error))