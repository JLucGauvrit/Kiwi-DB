#!/bin/bash
set -e

echo "Loading Sakila database schema..."
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" sakila < /docker-entrypoint-initdb.d/sakila-schema.sql

echo "Loading Sakila database data..."
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" sakila < /docker-entrypoint-initdb.d/sakila-data.sql

echo "Sakila database loaded successfully!"
