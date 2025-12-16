-- ============================================
-- Normalized ERP Database Schema with Sample Data
-- Following 3NF (Third Normal Form)
-- ============================================

DROP DATABASE IF EXISTS erp_demo;
CREATE DATABASE erp_demo;
USE erp_demo;

-- ============================================
-- 1. VENDORS TABLE
-- ============================================
CREATE TABLE vendors (
    vendor_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_name VARCHAR(255) NOT NULL,
    vendor_code VARCHAR(50) UNIQUE NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    tax_id VARCHAR(50),
    payment_terms VARCHAR(100),
    credit_limit DECIMAL(15, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_vendor_name (vendor_name),
    INDEX idx_country (country),
    INDEX idx_is_active (is_active)
);

-- ============================================
-- 2. CUSTOMERS TABLE
-- ============================================
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(255) NOT NULL,
    customer_code VARCHAR(50) UNIQUE NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    customer_type ENUM('Individual', 'Corporate', 'Government') DEFAULT 'Individual',
    credit_limit DECIMAL(15, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer_name (customer_name),
    INDEX idx_country (country)
);

-- ============================================
-- 3. PRODUCTS TABLE
-- ============================================
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(255) NOT NULL,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(100),
    unit_of_measure VARCHAR(50),
    unit_price DECIMAL(15, 2) NOT NULL,
    cost_price DECIMAL(15, 2),
    stock_quantity INT DEFAULT 0,
    reorder_level INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_name (product_name),
    INDEX idx_category (category)
);

-- ============================================
-- 4. PURCHASE ORDERS (From Vendors)
-- ============================================
CREATE TABLE purchase_orders (
    po_id INT PRIMARY KEY AUTO_INCREMENT,
    po_number VARCHAR(50) UNIQUE NOT NULL,
    vendor_id INT NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    status ENUM('Pending', 'Approved', 'Received', 'Cancelled') DEFAULT 'Pending',
    subtotal DECIMAL(15, 2) DEFAULT 0,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    shipping_cost DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) DEFAULT 0,
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    INDEX idx_vendor_id (vendor_id),
    INDEX idx_order_date (order_date),
    INDEX idx_status (status)
);

-- ============================================
-- 5. PURCHASE ORDER ITEMS
-- ============================================
CREATE TABLE purchase_order_items (
    po_item_id INT PRIMARY KEY AUTO_INCREMENT,
    po_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    tax_rate DECIMAL(5, 2) DEFAULT 0,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) NOT NULL,
    received_quantity INT DEFAULT 0,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_po_id (po_id),
    INDEX idx_product_id (product_id)
);

-- ============================================
-- 6. SALES ORDERS (To Customers)
-- ============================================
CREATE TABLE sales_orders (
    so_id INT PRIMARY KEY AUTO_INCREMENT,
    so_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE,
    status ENUM('Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    subtotal DECIMAL(15, 2) DEFAULT 0,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    shipping_cost DECIMAL(15, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) DEFAULT 0,
    payment_status ENUM('Pending', 'Partial', 'Paid') DEFAULT 'Pending',
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_order_date (order_date),
    INDEX idx_status (status)
);

-- ============================================
-- 7. SALES ORDER ITEMS
-- ============================================
CREATE TABLE sales_order_items (
    so_item_id INT PRIMARY KEY AUTO_INCREMENT,
    so_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    tax_rate DECIMAL(5, 2) DEFAULT 0,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) NOT NULL,
    FOREIGN KEY (so_id) REFERENCES sales_orders(so_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_so_id (so_id),
    INDEX idx_product_id (product_id)
);

-- ============================================
-- 8. VENDOR PAYMENTS (Revenue for Vendors)
-- ============================================
CREATE TABLE vendor_payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    vendor_id INT NOT NULL,
    po_id INT,
    payment_date DATE NOT NULL,
    payment_method ENUM('Cash', 'Check', 'Wire Transfer', 'Credit Card') DEFAULT 'Wire Transfer',
    amount DECIMAL(15, 2) NOT NULL,
    reference_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id),
    INDEX idx_vendor_id (vendor_id),
    INDEX idx_payment_date (payment_date)
);

-- ============================================
-- 9. CUSTOMER PAYMENTS (Revenue for Company)
-- ============================================
CREATE TABLE customer_payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    so_id INT,
    payment_date DATE NOT NULL,
    payment_method ENUM('Cash', 'Check', 'Wire Transfer', 'Credit Card', 'Online') DEFAULT 'Online',
    amount DECIMAL(15, 2) NOT NULL,
    reference_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (so_id) REFERENCES sales_orders(so_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_payment_date (payment_date)
);

-- ============================================
-- INSERT SAMPLE DATA
-- ============================================

-- Insert Vendors
INSERT INTO vendors (vendor_name, vendor_code, contact_person, email, phone, city, country, payment_terms, credit_limit) VALUES
('Tech Solutions Inc', 'VEN001', 'John Smith', 'john@techsolutions.com', '555-0101', 'New York', 'USA', 'Net 30', 100000),
('Global Supplies Ltd', 'VEN002', 'Sarah Johnson', 'sarah@globalsupplies.com', '555-0102', 'London', 'UK', 'Net 45', 150000),
('Asian Traders Co', 'VEN003', 'Wei Zhang', 'wei@asiantraders.com', '555-0103', 'Shanghai', 'China', 'Net 60', 200000),
('Euro Parts GmbH', 'VEN004', 'Hans Mueller', 'hans@europarts.de', '555-0104', 'Berlin', 'Germany', 'Net 30', 120000),
('Pacific Imports', 'VEN005', 'Yuki Tanaka', 'yuki@pacificimports.jp', '555-0105', 'Tokyo', 'Japan', 'Net 30', 180000),
('India Vendors Pvt', 'VEN006', 'Raj Kumar', 'raj@indiavendors.in', '555-0106', 'Mumbai', 'India', 'Net 45', 90000),
('Latin America Trade', 'VEN007', 'Carlos Rodriguez', 'carlos@latinamerica.com', '555-0107', 'Mexico City', 'Mexico', 'Net 30', 110000),
('Middle East Supply', 'VEN008', 'Ahmed Hassan', 'ahmed@mesupply.ae', '555-0108', 'Dubai', 'UAE', 'Net 60', 160000),
('Australian Goods', 'VEN009', 'Emma Wilson', 'emma@ausgood.au', '555-0109', 'Sydney', 'Australia', 'Net 30', 130000),
('Canadian Resources', 'VEN010', 'Michael Brown', 'michael@canresources.ca', '555-0110', 'Toronto', 'Canada', 'Net 45', 140000);

-- Insert Customers
INSERT INTO customers (customer_name, customer_code, contact_person, email, phone, city, country, customer_type, credit_limit) VALUES
('Mega Retail Corp', 'CUST001', 'Lisa Anderson', 'lisa@megaretail.com', '555-0201', 'Chicago', 'USA', 'Corporate', 500000),
('Small Business LLC', 'CUST002', 'Tom Williams', 'tom@smallbiz.com', '555-0202', 'Austin', 'USA', 'Corporate', 100000),
('Individual Buyer', 'CUST003', 'Jane Doe', 'jane@email.com', '555-0203', 'Seattle', 'USA', 'Individual', 10000),
('Government Agency', 'CUST004', 'Robert Smith', 'robert@gov.us', '555-0204', 'Washington', 'USA', 'Government', 1000000),
('European Chain', 'CUST005', 'Pierre Dubois', 'pierre@eurochain.fr', '555-0205', 'Paris', 'France', 'Corporate', 300000);

-- Insert Products
INSERT INTO products (product_name, product_code, description, category, unit_of_measure, unit_price, cost_price, stock_quantity) VALUES
('Laptop Computer', 'PROD001', 'High-performance laptop', 'Electronics', 'Each', 1200.00, 800.00, 50),
('Office Chair', 'PROD002', 'Ergonomic office chair', 'Furniture', 'Each', 350.00, 200.00, 100),
('Printer', 'PROD003', 'Laser printer', 'Electronics', 'Each', 450.00, 280.00, 30),
('Desk', 'PROD004', 'Wooden office desk', 'Furniture', 'Each', 600.00, 350.00, 25),
('Monitor', 'PROD005', '27-inch LED monitor', 'Electronics', 'Each', 400.00, 250.00, 75),
('Keyboard', 'PROD006', 'Wireless keyboard', 'Electronics', 'Each', 80.00, 45.00, 200),
('Mouse', 'PROD007', 'Wireless mouse', 'Electronics', 'Each', 50.00, 28.00, 250),
('Notebook', 'PROD008', 'A4 notebook pack', 'Stationery', 'Pack', 15.00, 8.00, 500),
('Pen Set', 'PROD009', 'Professional pen set', 'Stationery', 'Set', 25.00, 12.00, 300),
('Filing Cabinet', 'PROD010', '4-drawer filing cabinet', 'Furniture', 'Each', 280.00, 160.00, 40);

-- Insert Purchase Orders
INSERT INTO purchase_orders (po_number, vendor_id, order_date, status, subtotal, tax_amount, total_amount) VALUES
('PO-2025-001', 1, '2025-01-15', 'Received', 60000.00, 4800.00, 64800.00),
('PO-2025-002', 2, '2025-01-20', 'Received', 75000.00, 6000.00, 81000.00),
('PO-2025-003', 3, '2025-02-01', 'Received', 120000.00, 9600.00, 129600.00),
('PO-2025-004', 4, '2025-02-10', 'Received', 45000.00, 3600.00, 48600.00),
('PO-2025-005', 5, '2025-03-05', 'Received', 95000.00, 7600.00, 102600.00),
('PO-2025-006', 1, '2025-03-15', 'Received', 85000.00, 6800.00, 91800.00),
('PO-2025-007', 2, '2025-04-01', 'Received', 110000.00, 8800.00, 118800.00),
('PO-2025-008', 3, '2025-04-20', 'Received', 135000.00, 10800.00, 145800.00),
('PO-2025-009', 6, '2025-05-10', 'Received', 55000.00, 4400.00, 59400.00),
('PO-2025-010', 7, '2025-05-25', 'Received', 72000.00, 5760.00, 77760.00),
('PO-2025-011', 1, '2025-06-05', 'Received', 92000.00, 7360.00, 99360.00),
('PO-2025-012', 8, '2025-06-18', 'Received', 108000.00, 8640.00, 116640.00),
('PO-2025-013', 3, '2025-07-02', 'Received', 145000.00, 11600.00, 156600.00),
('PO-2025-014', 9, '2025-07-20', 'Received', 68000.00, 5440.00, 73440.00),
('PO-2025-015', 10, '2025-08-10', 'Received', 88000.00, 7040.00, 95040.00);

-- Insert Vendor Payments (This is the revenue for vendors!)
INSERT INTO vendor_payments (payment_number, vendor_id, po_id, payment_date, payment_method, amount) VALUES
('PAY-V-001', 1, 1, '2025-02-15', 'Wire Transfer', 64800.00),
('PAY-V-002', 2, 2, '2025-02-25', 'Wire Transfer', 81000.00),
('PAY-V-003', 3, 3, '2025-03-10', 'Wire Transfer', 129600.00),
('PAY-V-004', 4, 4, '2025-03-20', 'Wire Transfer', 48600.00),
('PAY-V-005', 5, 5, '2025-04-10', 'Wire Transfer', 102600.00),
('PAY-V-006', 1, 6, '2025-04-20', 'Wire Transfer', 91800.00),
('PAY-V-007', 2, 7, '2025-05-05', 'Wire Transfer', 118800.00),
('PAY-V-008', 3, 8, '2025-05-25', 'Wire Transfer', 145800.00),
('PAY-V-009', 6, 9, '2025-06-15', 'Wire Transfer', 59400.00),
('PAY-V-010', 7, 10, '2025-06-30', 'Wire Transfer', 77760.00),
('PAY-V-011', 1, 11, '2025-07-10', 'Wire Transfer', 99360.00),
('PAY-V-012', 8, 12, '2025-07-25', 'Wire Transfer', 116640.00),
('PAY-V-013', 3, 13, '2025-08-08', 'Wire Transfer', 156600.00),
('PAY-V-014', 9, 14, '2025-08-25', 'Wire Transfer', 73440.00),
('PAY-V-015', 10, 15, '2025-09-10', 'Wire Transfer', 95040.00);

-- Insert Sales Orders
INSERT INTO sales_orders (so_number, customer_id, order_date, status, subtotal, tax_amount, total_amount, payment_status) VALUES
('SO-2025-001', 1, '2025-01-20', 'Delivered', 85000.00, 6800.00, 91800.00, 'Paid'),
('SO-2025-002', 2, '2025-02-05', 'Delivered', 45000.00, 3600.00, 48600.00, 'Paid'),
('SO-2025-003', 1, '2025-03-10', 'Delivered', 120000.00, 9600.00, 129600.00, 'Paid'),
('SO-2025-004', 3, '2025-04-15', 'Delivered', 12000.00, 960.00, 12960.00, 'Paid'),
('SO-2025-005', 4, '2025-05-20', 'Delivered', 250000.00, 20000.00, 270000.00, 'Paid');

-- ============================================
-- CREATE USEFUL VIEWS
-- ============================================

-- View: Vendor Revenue Summary
CREATE VIEW vendor_revenue_summary AS
SELECT 
    v.vendor_id,
    v.vendor_name,
    v.vendor_code,
    v.country,
    COUNT(DISTINCT po.po_id) as total_orders,
    SUM(vp.amount) as total_revenue,
    AVG(vp.amount) as avg_order_value,
    MAX(vp.payment_date) as last_payment_date
FROM vendors v
LEFT JOIN purchase_orders po ON v.vendor_id = po.vendor_id
LEFT JOIN vendor_payments vp ON v.vendor_id = vp.vendor_id
GROUP BY v.vendor_id, v.vendor_name, v.vendor_code, v.country;

-- View: Customer Revenue Summary
CREATE VIEW customer_revenue_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_code,
    c.country,
    c.customer_type,
    COUNT(DISTINCT so.so_id) as total_orders,
    SUM(cp.amount) as total_revenue,
    AVG(cp.amount) as avg_order_value
FROM customers c
LEFT JOIN sales_orders so ON c.customer_id = so.customer_id
LEFT JOIN customer_payments cp ON c.customer_id = cp.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_code, c.country, c.customer_type;

-- View: Monthly Vendor Performance
CREATE VIEW monthly_vendor_performance AS
SELECT 
    v.vendor_id,
    v.vendor_name,
    YEAR(vp.payment_date) as year,
    MONTH(vp.payment_date) as month,
    DATE_FORMAT(vp.payment_date, '%Y-%m') as year_month,
    COUNT(vp.payment_id) as payment_count,
    SUM(vp.amount) as monthly_revenue
FROM vendors v
JOIN vendor_payments vp ON v.vendor_id = vp.vendor_id
GROUP BY v.vendor_id, v.vendor_name, YEAR(vp.payment_date), MONTH(vp.payment_date)
ORDER BY year DESC, month DESC, monthly_revenue DESC;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check vendor revenue
SELECT 'Top 10 Vendors by Revenue' as Query;
SELECT 
    vendor_name,
    country,
    total_orders,
    CONCAT('$', FORMAT(total_revenue, 2)) as revenue,
    CONCAT('$', FORMAT(avg_order_value, 2)) as avg_order_value
FROM vendor_revenue_summary
ORDER BY total_revenue DESC
LIMIT 10;

-- Check data counts
SELECT 'Data Summary' as Info;
SELECT 
    (SELECT COUNT(*) FROM vendors) as total_vendors,
    (SELECT COUNT(*) FROM customers) as total_customers,
    (SELECT COUNT(*) FROM products) as total_products,
    (SELECT COUNT(*) FROM purchase_orders) as total_purchase_orders,
    (SELECT COUNT(*) FROM vendor_payments) as total_vendor_payments,
    (SELECT CONCAT('$', FORMAT(SUM(amount), 2)) FROM vendor_payments) as total_vendor_revenue;

SELECT '✅ Database schema created successfully with sample data!' as Status;

