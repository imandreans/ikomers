SELECT * FROM orders;


-- CREATE TABLE products (
--     product_id SERIAL PRIMARY KEY,
--     product_name VARCHAR(100) NOT NULL,
--     price DECIMAL(10, 2) NOT NULL,
--     quantity INT NOT NULL,
--     description TEXT
-- );

-- CREATE TABLE customers (
--     customer_id SERIAL PRIMARY KEY,
--     username VARCHAR(100) NOT NULL,
--     email VARCHAR(100),
--     password VARCHAR(255) NOT NULL,
--     balance DECIMAL(10, 2) NOT NULL,
--     address TEXT
-- );

-- CREATE TABLE orders (
--  order_id SERIAL PRIMARY KEY,
--  customer_id INTEGER REFERENCES customers(customer_id),
--  total_price INTEGER NOT NULL
-- ); 

-- CREATE TABLE order_items (
--  order_item_id SERIAL PRIMARY KEY,
--  order_id INTEGER REFERENCES orders(order_id),
--  product_id INTEGER REFERENCES products(product_id),
--  quantity INTEGER NOT NULL,
--  price INTEGER NOT NULL
-- );

-- CREATE TABLE payment (
--  payment_id SERIAL PRIMARY KEY,
--  order_id INTEGER REFERENCES orders(order_id),
--  payment_date TIMESTAMP,
--  amount INTEGER NOT NULL,
--  payment_method VARCHAR(100)
-- );