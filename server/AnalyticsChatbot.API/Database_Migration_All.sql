-- ============================================
-- COMPLETE DATABASE MIGRATION SCRIPT
-- Applies all migrations in correct order
-- ============================================

-- ============================================
-- STEP 1: Create Identity Database for Authentication
-- ============================================
CREATE DATABASE IF NOT EXISTS chatbot_identity;
USE chatbot_identity;

-- AspNetRoles table
CREATE TABLE IF NOT EXISTS AspNetRoles (
    Id VARCHAR(255) NOT NULL PRIMARY KEY,
    Name VARCHAR(256) NULL,
    NormalizedName VARCHAR(256) NULL UNIQUE,
    ConcurrencyStamp TEXT NULL
);

-- AspNetUsers table
CREATE TABLE IF NOT EXISTS AspNetUsers (
    Id VARCHAR(255) NOT NULL PRIMARY KEY,
    UserName VARCHAR(256) NULL,
    NormalizedUserName VARCHAR(256) NULL UNIQUE,
    Email VARCHAR(256) NULL,
    NormalizedEmail VARCHAR(256) NULL,
    EmailConfirmed BOOLEAN NOT NULL DEFAULT FALSE,
    PasswordHash TEXT NULL,
    SecurityStamp TEXT NULL,
    ConcurrencyStamp TEXT NULL,
    PhoneNumber TEXT NULL,
    PhoneNumberConfirmed BOOLEAN NOT NULL DEFAULT FALSE,
    TwoFactorEnabled BOOLEAN NOT NULL DEFAULT FALSE,
    LockoutEnd DATETIME(6) NULL,
    LockoutEnabled BOOLEAN NOT NULL DEFAULT FALSE,
    AccessFailedCount INT NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS EmailIndex ON AspNetUsers (NormalizedEmail);

-- AspNetUserClaims table
CREATE TABLE IF NOT EXISTS AspNetUserClaims (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    UserId VARCHAR(255) NOT NULL,
    ClaimType TEXT NULL,
    ClaimValue TEXT NULL,
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_AspNetUserClaims_UserId ON AspNetUserClaims (UserId);

-- AspNetUserLogins table
CREATE TABLE IF NOT EXISTS AspNetUserLogins (
    LoginProvider VARCHAR(128) NOT NULL,
    ProviderKey VARCHAR(128) NOT NULL,
    ProviderDisplayName TEXT NULL,
    UserId VARCHAR(255) NOT NULL,
    PRIMARY KEY (LoginProvider, ProviderKey),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_AspNetUserLogins_UserId ON AspNetUserLogins (UserId);

-- AspNetUserRoles table
CREATE TABLE IF NOT EXISTS AspNetUserRoles (
    UserId VARCHAR(255) NOT NULL,
    RoleId VARCHAR(255) NOT NULL,
    PRIMARY KEY (UserId, RoleId),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE,
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_AspNetUserRoles_RoleId ON AspNetUserRoles (RoleId);

-- AspNetUserTokens table
CREATE TABLE IF NOT EXISTS AspNetUserTokens (
    UserId VARCHAR(255) NOT NULL,
    LoginProvider VARCHAR(128) NOT NULL,
    Name VARCHAR(128) NOT NULL,
    Value TEXT NULL,
    PRIMARY KEY (UserId, LoginProvider, Name),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
);

-- AspNetRoleClaims table
CREATE TABLE IF NOT EXISTS AspNetRoleClaims (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    RoleId VARCHAR(255) NOT NULL,
    ClaimType TEXT NULL,
    ClaimValue TEXT NULL,
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_AspNetRoleClaims_RoleId ON AspNetRoleClaims (RoleId);

SELECT '✅ Step 1: Identity tables created' as Status;

-- ============================================
-- STEP 2: Create Chat Session Tables
-- ============================================

-- ChatSessions table
CREATE TABLE IF NOT EXISTS ChatSessions (
    SessionId VARCHAR(255) NOT NULL PRIMARY KEY,
    UserId VARCHAR(255) NOT NULL,
    UserEmail VARCHAR(256) NULL,
    UserName VARCHAR(256) NULL,
    CreatedAt DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    IsActive BOOLEAN NOT NULL DEFAULT TRUE,
    MessageCount INT NOT NULL DEFAULT 0,
    INDEX IX_ChatSessions_UserId (UserId),
    INDEX IX_ChatSessions_CreatedAt (CreatedAt)
);

-- ChatMessages table
CREATE TABLE IF NOT EXISTS ChatMessages (
    MessageId VARCHAR(255) NOT NULL PRIMARY KEY,
    SessionId VARCHAR(255) NOT NULL,
    Message TEXT NOT NULL,
    Role VARCHAR(50) NOT NULL,
    SqlQuery TEXT NULL,
    ResponseData TEXT NULL,
    ResponseFormat VARCHAR(50) NULL,
    HasError BOOLEAN NOT NULL DEFAULT FALSE,
    ErrorMessage TEXT NULL,
    Timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    ResponseTimeMs INT NULL,
    INDEX IX_ChatMessages_SessionId (SessionId),
    INDEX IX_ChatMessages_Timestamp (Timestamp),
    FOREIGN KEY (SessionId) REFERENCES ChatSessions(SessionId) ON DELETE CASCADE
);

SELECT '✅ Step 2: Chat session tables created' as Status;

-- ============================================
-- STEP 3: Create Smart Chat RAG Tables
-- ============================================

-- ConversationHistories table
CREATE TABLE IF NOT EXISTS ConversationHistories (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    SessionId VARCHAR(255) NOT NULL,
    UserId VARCHAR(255) NOT NULL,
    Message TEXT NOT NULL,
    Role VARCHAR(50) NOT NULL,
    Keywords TEXT NULL,
    ConfidenceScore DECIMAL(5, 2) NULL,
    Timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX IX_ConversationHistories_SessionId (SessionId),
    INDEX IX_ConversationHistories_UserId (UserId)
);

-- KnowledgeBases table
CREATE TABLE IF NOT EXISTS KnowledgeBases (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    Question TEXT NOT NULL,
    Answer TEXT NOT NULL,
    Keywords TEXT NULL,
    Category VARCHAR(100) NULL,
    Embedding TEXT NULL,
    UsageCount INT NOT NULL DEFAULT 0,
    CreatedAt DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX IX_KnowledgeBases_Category (Category)
);

-- ConversationContexts table
CREATE TABLE IF NOT EXISTS ConversationContexts (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    SessionId VARCHAR(255) NOT NULL UNIQUE,
    UserId VARCHAR(255) NOT NULL,
    LastQuery TEXT NULL,
    LastResponse TEXT NULL,
    PendingClarification BOOLEAN NOT NULL DEFAULT FALSE,
    ContextData TEXT NULL,
    CreatedAt DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UpdatedAt DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX IX_ConversationContexts_SessionId (SessionId),
    INDEX IX_ConversationContexts_UserId (UserId)
);

SELECT '✅ Step 3: RAG tables created' as Status;

-- ============================================
-- STEP 4: Create ERP Database with Normalized Schema
-- ============================================

DROP DATABASE IF EXISTS erp_demo;
CREATE DATABASE erp_demo;
USE erp_demo;

-- Vendors table
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

-- Customers table
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

-- Products table
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

-- Purchase Orders table
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

-- Purchase Order Items table
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

-- Sales Orders table
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

-- Sales Order Items table
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

-- Vendor Payments table
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

-- Customer Payments table
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

SELECT '✅ Step 4: ERP tables created' as Status;

-- ============================================
-- STEP 5: Insert Sample Data
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

-- Insert Vendor Payments
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

SELECT '✅ Step 5: Sample data inserted' as Status;

-- ============================================
-- STEP 6: Create Views
-- ============================================

-- Vendor Revenue Summary View
CREATE VIEW vendor_revenue_summary AS
SELECT 
    v.vendor_id,
    v.vendor_name,
    v.vendor_code,
    v.country,
    COUNT(DISTINCT po.po_id) as total_orders,
    COALESCE(SUM(vp.amount), 0) as total_revenue,
    COALESCE(AVG(vp.amount), 0) as avg_order_value,
    MAX(vp.payment_date) as last_payment_date
FROM vendors v
LEFT JOIN purchase_orders po ON v.vendor_id = po.vendor_id
LEFT JOIN vendor_payments vp ON v.vendor_id = vp.vendor_id
GROUP BY v.vendor_id, v.vendor_name, v.vendor_code, v.country;

-- Customer Revenue Summary View
CREATE VIEW customer_revenue_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_code,
    c.country,
    c.customer_type,
    COUNT(DISTINCT so.so_id) as total_orders,
    COALESCE(SUM(cp.amount), 0) as total_revenue,
    COALESCE(AVG(cp.amount), 0) as avg_order_value
FROM customers c
LEFT JOIN sales_orders so ON c.customer_id = so.customer_id
LEFT JOIN customer_payments cp ON c.customer_id = cp.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_code, c.country, c.customer_type;

-- Monthly Vendor Performance View
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

SELECT '✅ Step 6: Views created' as Status;

-- ============================================
-- FINAL VERIFICATION
-- ============================================

-- Switch back to identity database
USE chatbot_identity;
SELECT 'Identity Database Tables:' as Info;
SHOW TABLES;

-- Switch to ERP database
USE erp_demo;
SELECT 'ERP Database Tables:' as Info;
SHOW TABLES;

-- Show summary statistics
SELECT '=== DATABASE MIGRATION COMPLETE ===' as Status;
SELECT 
    'chatbot_identity' as Database_Name,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='chatbot_identity') as Table_Count;

SELECT 
    'erp_demo' as Database_Name,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='erp_demo') as Table_Count,
    (SELECT COUNT(*) FROM vendors) as Vendors,
    (SELECT COUNT(*) FROM customers) as Customers,
    (SELECT COUNT(*) FROM products) as Products,
    (SELECT COUNT(*) FROM purchase_orders) as Purchase_Orders,
    (SELECT COUNT(*) FROM vendor_payments) as Vendor_Payments,
    (SELECT CONCAT('$', FORMAT(SUM(amount), 2)) FROM vendor_payments) as Total_Vendor_Revenue;

SELECT '✅ ALL MIGRATIONS APPLIED SUCCESSFULLY!' as Final_Status;

