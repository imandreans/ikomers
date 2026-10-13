SELECT * FROM orders;

-- Show the product in ordered items or payment

WITH ordered_products AS (
SELECT od.order_id, p.product_name, od.quantity, od.price FROM order_items as od JOIN products as p 
ON od.product_id = p.product_id
), customer_order AS (
    SELECT o.order_id, c.customer_id FROM orders as o JOIN customers as c ON c.customer_id = o.customer_id
) SELECT op.order_id, co.customer_id, op.product_name, op.quantity, op.price FROM ordered_products as op JOIN customer_order as co ON op.order_id = co.order_id;

SELECT op.*, py.payment_date, py.payment_method FROM ordered_products as op 
JOIN payment as py ON op.order_id = py.order_id WHERE op.order_id=2;

-- SELECT o.order_id, o.already_paid, py.payment_date, py.amount FROM orders as o JOIN payment as py 
-- ON o.order_id = py.order_id WHERE o.order_id=2;