CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    category VARCHAR(50)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

INSERT INTO users (username, email) VALUES
    ('john_doe', 'john@example.com'),
    ('jane_smith', 'jane@example.com'),
    ('bob_wilson', 'bob@example.com'),
    ('alice_martin', 'alice@example.com'),
    ('charlie_brown', 'charlie@example.com');

INSERT INTO products (name, price, stock, category) VALUES
    ('Laptop Dell XPS 13', 1299.99, 15, 'Electronics'),
    ('iPhone 15 Pro', 999.99, 30, 'Electronics'),
    ('Nike Air Max', 129.99, 50, 'Shoes'),
    ('Sony WH-1000XM5', 349.99, 25, 'Electronics'),
    ('Samsung Galaxy S24', 899.99, 20, 'Electronics'),
    ('Adidas Ultraboost', 179.99, 40, 'Shoes'),
    ('MacBook Pro 14"', 1999.99, 10, 'Electronics'),
    ('AirPods Pro', 249.99, 100, 'Electronics');

INSERT INTO orders (user_id, product_id, quantity, status) VALUES
    (1, 1, 1, 'completed'),
    (2, 2, 1, 'pending'),
    (3, 3, 2, 'completed'),
    (4, 5, 1, 'shipped'),
    (5, 7, 1, 'pending');