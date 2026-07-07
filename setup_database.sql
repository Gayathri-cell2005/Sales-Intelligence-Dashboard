-- ============================================
-- Real-Time Sales Intelligence Dashboard
-- Database Setup Script
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS sales_intelligence;
USE sales_intelligence;

-- Create the sales table
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_date DATETIME NOT NULL,
    product VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    region VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    sales_rep VARCHAR(100) NOT NULL
);

-- Index for faster date-based queries (used heavily by the dashboard)
CREATE INDEX idx_sale_date ON sales(sale_date);
CREATE INDEX idx_region ON sales(region);
CREATE INDEX idx_category ON sales(category);