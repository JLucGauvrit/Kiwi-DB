-- Schéma de la table customers (adapté au dataset Olist)

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix VARCHAR(10),
    customer_city VARCHAR(100),
    customer_state VARCHAR(2)
);

CREATE INDEX idx_customer_city ON customers(customer_city);
CREATE INDEX idx_customer_state ON customers(customer_state);
