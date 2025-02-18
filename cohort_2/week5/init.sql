-- Create stock table
CREATE TABLE IF NOT EXISTS stock (
    product_id INTEGER,
    size TEXT,
    color TEXT, 
    quantity INTEGER
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    date DATETIME,
    total_amount DECIMAL(10,2),
    FOREIGN KEY (user_email) REFERENCES users(email)
);

-- Create sales table (now with order_id and item details)
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    size TEXT,
    color TEXT,
    quantity INTEGER,
    price_per_unit DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    name TEXT,
    gender TEXT,
    date_of_birth DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
