import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from .model import Cart, UpdateCustomer
from fastapi import HTTPException, status
from ..auth.auth_model import TokenData
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from app.db.core import Conn
 
def list_customers_service(conn: Conn):
        with conn.cursor() as curs:
            try:
                curs.execute("SELECT * FROM customers")
                all_customers = curs.fetchall()
                return {"message": "customer's data is fetched successfully",
                    "data": all_customers}
            except (HTTPException, psycopg2.DatabaseError) as error:
                raise HTTPException(status_code=500, detail=str(error)) 

def get_customer_service(conn: Conn, username):
    with conn.cursor() as curs:
        try:
            curs.execute(f"SELECT * FROM customers WHERE username='{username}'")
            customer=curs.fetchone()
            return customer
        except psycopg2.DatabaseError as error:
            raise HTTPException(status_code=500, detail=str(error))

def update_customer_service(conn: Conn, current_user: TokenData, data:UpdateCustomer):
    new_update=data.model_dump(exclude_unset=True)
    customer_id = get_customer_service(conn, current_user.username)[0]
    if customer_id == None:
        raise HTTPException(status_code=404, detail="Customer not found")
    update_query = sql.SQL("UPDATE customers SET {data} WHERE customer_id = {id}").format(
    data=sql.SQL(', ').join(
        sql.Composed([sql.Identifier(k), sql.SQL(" = "), sql.Placeholder(k)]) for k in new_update.keys()
    ),
    id=sql.Placeholder('customer_id'))

    params={**new_update, "customer_id":customer_id}
    with conn.cursor() as curs:
            try:
                curs.execute(update_query, params)
                conn.commit()
            except (HTTPException, psycopg2.DatabaseError) as error:
                raise HTTPException(status_code=500, detail=str(error))

def delete_customer_service(conn: Conn, current_user: TokenData):
    with conn.cursor() as curs:
        try:
            customer_id = get_customer_service(conn, current_user.username)[0]
            if customer_id == None:
                raise HTTPException(status_code=404, detail="Customer not found")
            curs.execute("DELETE FROM customers WHERE customer_id=%s" % (customer_id))
            conn.commit()
            return {"message": "customer is deleted",}
        except (HTTPException, psycopg2.DatabaseError) as error:
            raise HTTPException(status_code=500, detail=str(error))

def get_ordered_items(conn: Conn, current_user: TokenData):
    with conn.cursor() as curs:
        try:
            customer_id = get_customer_service(conn, current_user.username)[0]
            query=f"""
                    WITH ordered_products AS (
                    SELECT od.order_id, p.product_name, od.quantity, od.price FROM order_items as od JOIN products as p 
                    ON od.product_id = p.product_id
                    ), customer_order AS (
                        SELECT o.order_id, c.customer_id FROM orders as o JOIN customers as c ON c.customer_id = o.customer_id
                    ) SELECT op.order_id, co.customer_id, op.product_name, op.quantity, op.price 
                    FROM ordered_products as op JOIN customer_order as co ON op.order_id = co.order_id WHERE co.customer_id=%s;
                    """ % (customer_id)
            if customer_id == None:
                raise HTTPException(status_code=404, detail="Customer not found")
            curs.execute(query)
            all_purchased_items = curs.fetchall()
            # print(*all_purchased_items, sep="\n")
            return {"data": all_purchased_items,"message": "Order is fetched successfully",}
        except (HTTPException, psycopg2.DatabaseError) as error:
            raise HTTPException(status_code=500, detail=str(error))

def check_balance(conn: Conn, current_user: TokenData, total_price:int):
    with conn.cursor() as curs:
        customer_id = get_customer_service(conn, current_user.username)[0]
        if customer_id == None:
            raise HTTPException(status_code=404, detail="Customer not found")

        curs.execute("SELECT balance FROM customers WHERE customer_id=%s" % (customer_id))
        current_balance=curs.fetchone()
        if int(current_balance[0])> total_price:
            return True
        return False
       

def purcashe_items(conn: Conn, current_customer: TokenData, data:Cart):
    cart = [i.model_dump() for i in data]
    with conn.cursor() as curs:
        try:
            customer_id = get_customer_service(conn, current_customer.username)[0]
            if customer_id == None:
                raise HTTPException(status_code=404, detail="Customer not found")
            product_ids=[product["product_id"] for product in cart]
            curs.execute(f"SELECT product_id, price FROM products WHERE product_id=ANY(%s);", (product_ids,),)
            # print([i[0] for i in curs.fetchall()])
            prices=dict(curs.fetchall())
            total_price=sum(int(prices[product["product_id"]]) * product["quantity"] for product in cart)
            if check_balance(conn, current_customer, total_price)==False:
                return HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Your balance is too low to complete this purchase.")

            curs.execute("INSERT INTO orders (customer_id, total_price) VALUES (%s, %s) RETURNING order_id" % (customer_id, total_price))
            order_id = curs.fetchone()[0]
            
            execute_values(curs, "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES %s",[
                (order_id, product["product_id"], product["quantity"],  int(prices[product["product_id"]])) for product in cart
            ])

            curs.execute(f"UPDATE customers SET balance=balance-{total_price} WHERE customer_id={customer_id}")

            conn.commit()

            return {"message": "products are successfully purcashed"}
        except (HTTPException, psycopg2.DatabaseError) as error:
            raise HTTPException(status_code=500, detail=str(error))

# get_customer_service(connect(), "andrean")