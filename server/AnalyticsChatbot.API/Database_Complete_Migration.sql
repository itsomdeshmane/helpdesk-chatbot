-- ============================================
-- COMPLETE DATABASE MIGRATION SCRIPT
-- Includes: Base tables, Relationships, Sample Data, Views
-- ============================================

-- ============================================
-- PART 1: CREATE IDENTITY DATABASE
-- ============================================
CREATE DATABASE IF NOT EXISTS chatbot_identity;
USE chatbot_identity;

-- Identity Tables
CREATE TABLE IF NOT EXISTS AspNetRoles (
    Id VARCHAR(255) NOT NULL PRIMARY KEY,
    Name VARCHAR(256) NULL,
    NormalizedName VARCHAR(256) NULL UNIQUE,
    ConcurrencyStamp TEXT NULL
);

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

CREATE TABLE IF NOT EXISTS AspNetUserClaims (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    UserId VARCHAR(255) NOT NULL,
    ClaimType TEXT NULL,
    ClaimValue TEXT NULL,
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_AspNetUserClaims_UserId ON AspNetUserClaims (UserId);

CREATE TABLE IF NOT EXISTS AspNetUserLogins (
    LoginProvider VARCHAR(128) NOT NULL,
    ProviderKey VARCHAR(128) NOT NULL,
    ProviderDisplayName TEXT NULL,
    UserId VARCHAR(255) NOT NULL,
    PRIMARY KEY (LoginProvider, ProviderKey),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_AspNetUserLogins_UserId ON AspNetUserLogins (UserId);

CREATE TABLE IF NOT EXISTS AspNetUserRoles (
    UserId VARCHAR(255) NOT NULL,
    RoleId VARCHAR(255) NOT NULL,
    PRIMARY KEY (UserId, RoleId),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE,
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_AspNetUserRoles_RoleId ON AspNetUserRoles (RoleId);

CREATE TABLE IF NOT EXISTS AspNetUserTokens (
    UserId VARCHAR(255) NOT NULL,
    LoginProvider VARCHAR(128) NOT NULL,
    Name VARCHAR(128) NOT NULL,
    Value TEXT NULL,
    PRIMARY KEY (UserId, LoginProvider, Name),
    FOREIGN KEY (UserId) REFERENCES AspNetUsers(Id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS AspNetRoleClaims (
    Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    RoleId VARCHAR(255) NOT NULL,
    ClaimType TEXT NULL,
    ClaimValue TEXT NULL,
    FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_AspNetRoleClaims_RoleId ON AspNetRoleClaims (RoleId);

-- Chat Session Tables
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

-- RAG Tables
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

SELECT '✅ Part 1: Identity and Chat tables created' as Status;

-- ============================================
-- PART 2: CREATE ERP DATABASE WITH BASE TABLES
-- ============================================

DROP DATABASE IF EXISTS erp_demo;
CREATE DATABASE erp_demo;
USE erp_demo;

-- 1. Countries
CREATE TABLE countries (
    country_id INT PRIMARY KEY AUTO_INCREMENT,
    country_code VARCHAR(3) UNIQUE NOT NULL,
    country_name VARCHAR(100) UNIQUE NOT NULL,
    currency_code VARCHAR(3),
    phone_code VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_country_code (country_code),
    INDEX idx_country_name (country_name)
);

-- 2. States
CREATE TABLE states (
    state_id INT PRIMARY KEY AUTO_INCREMENT,
    state_code VARCHAR(10) NOT NULL,
    state_name VARCHAR(100) NOT NULL,
    country_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    UNIQUE KEY unique_state (state_code, country_id),
    INDEX idx_state_name (state_name),
    INDEX idx_country_id (country_id)
);

-- 3. Cities
CREATE TABLE cities (
    city_id INT PRIMARY KEY AUTO_INCREMENT,
    city_name VARCHAR(100) NOT NULL,
    state_id INT NOT NULL,
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    INDEX idx_city_name (city_name),
    INDEX idx_state_id (state_id)
);

-- 4. Product Categories
CREATE TABLE product_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    parent_category_id INT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES product_categories(category_id),
    INDEX idx_category_name (category_name)
);

-- 5. Units of Measure
CREATE TABLE units_of_measure (
    uom_id INT PRIMARY KEY AUTO_INCREMENT,
    uom_code VARCHAR(20) UNIQUE NOT NULL,
    uom_name VARCHAR(50) UNIQUE NOT NULL,
    uom_type ENUM('Weight', 'Volume', 'Length', 'Quantity', 'Time') NOT NULL,
    base_unit BOOLEAN DEFAULT FALSE,
    conversion_factor DECIMAL(15, 6) DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_uom_code (uom_code)
);

-- 6. Brands
CREATE TABLE brands (
    brand_id INT PRIMARY KEY AUTO_INCREMENT,
    brand_code VARCHAR(50) UNIQUE NOT NULL,
    brand_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    website VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_brand_name (brand_name)
);

-- 7. Payment Terms
CREATE TABLE payment_terms (
    term_id INT PRIMARY KEY AUTO_INCREMENT,
    term_code VARCHAR(20) UNIQUE NOT NULL,
    term_name VARCHAR(100) NOT NULL,
    days INT NOT NULL,
    description TEXT,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    discount_days INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_term_code (term_code)
);

-- 8. Tax Rates
CREATE TABLE tax_rates (
    tax_id INT PRIMARY KEY AUTO_INCREMENT,
    tax_code VARCHAR(20) UNIQUE NOT NULL,
    tax_name VARCHAR(100) NOT NULL,
    tax_rate DECIMAL(5, 2) NOT NULL,
    country_id INT,
    state_id INT NULL,
    effective_date DATE,
    expiry_date DATE NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    INDEX idx_tax_code (tax_code)
);

-- 9. Payment Methods
CREATE TABLE payment_methods (
    payment_method_id INT PRIMARY KEY AUTO_INCREMENT,
    method_code VARCHAR(20) UNIQUE NOT NULL,
    method_name VARCHAR(100) NOT NULL,
    description TEXT,
    processing_fee_percent DECIMAL(5, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_method_code (method_code)
);

-- 10. Vendor Categories
CREATE TABLE vendor_categories (
    vendor_category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category_name (category_name)
);

-- 11. Vendors (with all foreign keys)
CREATE TABLE vendors (
    vendor_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_code VARCHAR(50) UNIQUE NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    vendor_category_id INT,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    city_id INT,
    state_id INT,
    country_id INT NOT NULL,
    postal_code VARCHAR(20),
    tax_id VARCHAR(50),
    payment_term_id INT,
    credit_limit DECIMAL(15, 2) DEFAULT 0,
    rating DECIMAL(3, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_category_id) REFERENCES vendor_categories(vendor_category_id),
    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (payment_term_id) REFERENCES payment_terms(term_id),
    INDEX idx_vendor_name (vendor_name),
    INDEX idx_country_id (country_id),
    INDEX idx_vendor_category (vendor_category_id)
);

-- 12. Customer Types
CREATE TABLE customer_types (
    customer_type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_code VARCHAR(20) UNIQUE NOT NULL,
    type_name VARCHAR(100) NOT NULL,
    description TEXT,
    default_discount_percent DECIMAL(5, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type_code (type_code)
);

-- 13. Customers (with all foreign keys)
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_code VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_type_id INT,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    city_id INT,
    state_id INT,
    country_id INT NOT NULL,
    postal_code VARCHAR(20),
    tax_id VARCHAR(50),
    payment_term_id INT,
    credit_limit DECIMAL(15, 2) DEFAULT 0,
    rating DECIMAL(3, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_type_id) REFERENCES customer_types(customer_type_id),
    FOREIGN KEY (city_id) REFERENCES cities(city_id),
    FOREIGN KEY (state_id) REFERENCES states(state_id),
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (payment_term_id) REFERENCES payment_terms(term_id),
    INDEX idx_customer_name (customer_name),
    INDEX idx_country_id (country_id)
);

-- 14. Products (with all foreign keys)
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category_id INT,
    brand_id INT,
    uom_id INT NOT NULL,
    description TEXT,
    specifications TEXT,
    unit_price DECIMAL(15, 2) NOT NULL,
    cost_price DECIMAL(15, 2),
    stock_quantity INT DEFAULT 0,
    reorder_level INT DEFAULT 0,
    reorder_quantity INT DEFAULT 0,
    min_order_quantity INT DEFAULT 1,
    barcode VARCHAR(100),
    sku VARCHAR(100),
    tax_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id),
    FOREIGN KEY (brand_id) REFERENCES brands(brand_id),
    FOREIGN KEY (uom_id) REFERENCES units_of_measure(uom_id),
    FOREIGN KEY (tax_id) REFERENCES tax_rates(tax_id),
    INDEX idx_product_name (product_name),
    INDEX idx_category_id (category_id)
);

-- 15. Order Statuses
CREATE TABLE order_statuses (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    status_code VARCHAR(20) UNIQUE NOT NULL,
    status_name VARCHAR(100) NOT NULL,
    status_type ENUM('Purchase', 'Sales', 'Both') NOT NULL,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status_code (status_code)
);

-- 16. Purchase Orders
CREATE TABLE purchase_orders (
    po_id INT PRIMARY KEY AUTO_INCREMENT,
    po_number VARCHAR(50) UNIQUE NOT NULL,
    vendor_id INT NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    status_id INT NOT NULL,
    payment_term_id INT,
    payment_method_id INT,
    subtotal DECIMAL(15, 2) DEFAULT 0,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    shipping_cost DECIMAL(15, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    total_amount DECIMAL(15, 2) DEFAULT 0,
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (status_id) REFERENCES order_statuses(status_id),
    FOREIGN KEY (payment_term_id) REFERENCES payment_terms(term_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id),
    INDEX idx_vendor_id (vendor_id),
    INDEX idx_order_date (order_date)
);

-- 17. Purchase Order Items
CREATE TABLE purchase_order_items (
    po_item_id INT PRIMARY KEY AUTO_INCREMENT,
    po_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    tax_id INT,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) NOT NULL,
    received_quantity INT DEFAULT 0,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (tax_id) REFERENCES tax_rates(tax_id),
    INDEX idx_po_id (po_id),
    INDEX idx_product_id (product_id)
);

-- 18. Sales Orders
CREATE TABLE sales_orders (
    so_id INT PRIMARY KEY AUTO_INCREMENT,
    so_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE,
    status_id INT NOT NULL,
    payment_term_id INT,
    payment_method_id INT,
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
    FOREIGN KEY (status_id) REFERENCES order_statuses(status_id),
    FOREIGN KEY (payment_term_id) REFERENCES payment_terms(term_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_order_date (order_date)
);

-- 19. Sales Order Items
CREATE TABLE sales_order_items (
    so_item_id INT PRIMARY KEY AUTO_INCREMENT,
    so_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    tax_id INT,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) NOT NULL,
    FOREIGN KEY (so_id) REFERENCES sales_orders(so_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (tax_id) REFERENCES tax_rates(tax_id),
    INDEX idx_so_id (so_id),
    INDEX idx_product_id (product_id)
);

-- 20. Vendor Payments
CREATE TABLE vendor_payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    vendor_id INT NOT NULL,
    po_id INT,
    payment_date DATE NOT NULL,
    payment_method_id INT NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    reference_number VARCHAR(100),
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id),
    INDEX idx_vendor_id (vendor_id),
    INDEX idx_payment_date (payment_date)
);

-- 21. Customer Payments
CREATE TABLE customer_payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    so_id INT,
    payment_date DATE NOT NULL,
    payment_method_id INT NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    reference_number VARCHAR(100),
    notes TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (so_id) REFERENCES sales_orders(so_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_payment_date (payment_date)
);

SELECT '✅ Part 2: ERP base tables created' as Status;

-- ============================================
-- PART 3: INSERT MASTER DATA
-- ============================================

-- Insert Countries
INSERT INTO countries (country_code, country_name, currency_code, phone_code) VALUES
('USA', 'United States', 'USD', '+1'),
('CAN', 'Canada', 'CAD', '+1'),
('GBR', 'United Kingdom', 'GBP', '+44'),
('DEU', 'Germany', 'EUR', '+49'),
('FRA', 'France', 'EUR', '+33'),
('CHN', 'China', 'CNY', '+86'),
('JPN', 'Japan', 'JPY', '+81'),
('IND', 'India', 'INR', '+91'),
('AUS', 'Australia', 'AUD', '+61'),
('MEX', 'Mexico', 'MXN', '+52'),
('BRA', 'Brazil', 'BRL', '+55'),
('ARE', 'United Arab Emirates', 'AED', '+971'),
('SGP', 'Singapore', 'SGD', '+65'),
('KOR', 'South Korea', 'KRW', '+82');

-- Insert States
INSERT INTO states (state_code, state_name, country_id) VALUES
-- USA
('NY', 'New York', 1),
('CA', 'California', 1),
('TX', 'Texas', 1),
('FL', 'Florida', 1),
('IL', 'Illinois', 1),
('WA', 'Washington', 1),
-- Canada
('ON', 'Ontario', 2),
('QC', 'Quebec', 2),
('BC', 'British Columbia', 2),
-- India
('MH', 'Maharashtra', 8),
('DL', 'Delhi', 8),
('KA', 'Karnataka', 8),
('TN', 'Tamil Nadu', 8);

-- Insert Cities
INSERT INTO cities (city_name, state_id) VALUES
-- USA Cities
('New York', 1),
('Los Angeles', 2),
('Houston', 3),
('Miami', 4),
('Chicago', 5),
('Seattle', 6),
-- Canada Cities
('Toronto', 7),
('Montreal', 8),
('Vancouver', 9),
-- India Cities
('Mumbai', 10),
('Delhi', 11),
('Bangalore', 12),
('Chennai', 13);

-- Insert Product Categories
INSERT INTO product_categories (category_code, category_name, parent_category_id, description) VALUES
('ELEC', 'Electronics', NULL, 'Electronic devices and equipment'),
('FURN', 'Furniture', NULL, 'Office and home furniture'),
('STAT', 'Stationery', NULL, 'Office supplies and stationery'),
('COMP', 'Computers', 1, 'Computer hardware and peripherals'),
('ACCS', 'Accessories', 1, 'Electronic accessories'),
('OFF-FURN', 'Office Furniture', 2, 'Office furniture items');

-- Insert Units of Measure
INSERT INTO units_of_measure (uom_code, uom_name, uom_type, base_unit) VALUES
('EA', 'Each', 'Quantity', TRUE),
('PC', 'Piece', 'Quantity', FALSE),
('SET', 'Set', 'Quantity', FALSE),
('BOX', 'Box', 'Quantity', FALSE),
('PACK', 'Pack', 'Quantity', FALSE),
('DOZ', 'Dozen', 'Quantity', FALSE);

-- Insert Brands
INSERT INTO brands (brand_code, brand_name, description, website) VALUES
('DELL', 'Dell Technologies', 'Computer hardware', 'www.dell.com'),
('HP', 'HP Inc', 'Computing and printing', 'www.hp.com'),
('APPLE', 'Apple Inc', 'Consumer electronics', 'www.apple.com'),
('LENOVO', 'Lenovo', 'Computing devices', 'www.lenovo.com'),
('LOGITECH', 'Logitech', 'Computer peripherals', 'www.logitech.com'),
('HERMAN-M', 'Herman Miller', 'Premium office furniture', 'www.hermanmiller.com'),
('GENERIC', 'Generic Brand', 'Unbranded products', NULL);

-- Insert Payment Terms
INSERT INTO payment_terms (term_code, term_name, days, discount_percent, discount_days) VALUES
('NET30', 'Net 30 Days', 30, 0, 0),
('NET45', 'Net 45 Days', 45, 0, 0),
('NET60', 'Net 60 Days', 60, 0, 0),
('NET15', 'Net 15 Days', 15, 0, 0),
('COD', 'Cash on Delivery', 0, 0, 0);

-- Insert Tax Rates
INSERT INTO tax_rates (tax_code, tax_name, tax_rate, country_id, effective_date) VALUES
('VAT-20', 'VAT 20%', 20.00, 3, '2020-01-01'),
('GST-18', 'GST 18%', 18.00, 8, '2020-01-01'),
('GST-12', 'GST 12%', 12.00, 8, '2020-01-01'),
('SALES-TAX-8', 'Sales Tax 8%', 8.00, 1, '2020-01-01'),
('VAT-19', 'VAT 19%', 19.00, 4, '2020-01-01'),
('NO-TAX', 'No Tax', 0.00, NULL, '2020-01-01');

-- Insert Payment Methods
INSERT INTO payment_methods (method_code, method_name, processing_fee_percent) VALUES
('CASH', 'Cash', 0.00),
('CHECK', 'Check', 0.00),
('WIRE', 'Wire Transfer', 0.50),
('CREDIT', 'Credit Card', 2.50),
('ONLINE', 'Online Payment', 2.00);

-- Insert Vendor Categories
INSERT INTO vendor_categories (category_code, category_name, description) VALUES
('IT-HARD', 'IT Hardware', 'Computer and IT equipment vendors'),
('IT-SOFT', 'IT Software', 'Software and license vendors'),
('FURNITURE', 'Furniture Suppliers', 'Office and home furniture vendors'),
('STATIONERY', 'Stationery Suppliers', 'Office supplies vendors'),
('ELECTRONICS', 'Electronics', 'Electronic equipment vendors');

-- Insert Customer Types
INSERT INTO customer_types (type_code, type_name, description, default_discount_percent) VALUES
('IND', 'Individual', 'Individual customers', 0.00),
('CORP', 'Corporate', 'Corporate clients', 5.00),
('GOV', 'Government', 'Government agencies', 3.00),
('RETAIL', 'Retail', 'Retail chains', 7.00);

-- Insert Order Statuses
INSERT INTO order_statuses (status_code, status_name, status_type, sort_order) VALUES
('DRAFT', 'Draft', 'Both', 1),
('PENDING', 'Pending', 'Both', 2),
('APPROVED', 'Approved', 'Both', 3),
('PROCESSING', 'Processing', 'Both', 4),
('SHIPPED', 'Shipped', 'Sales', 5),
('RECEIVED', 'Received', 'Purchase', 5),
('DELIVERED', 'Delivered', 'Sales', 6),
('COMPLETED', 'Completed', 'Both', 7),
('CANCELLED', 'Cancelled', 'Both', 9);

SELECT '✅ Part 3: Master data inserted' as Status;

-- ============================================
-- PART 4: INSERT TRANSACTION DATA
-- ============================================

-- Insert Vendors
INSERT INTO vendors (vendor_code, vendor_name, vendor_category_id, contact_person, email, phone, 
                     city_id, state_id, country_id, payment_term_id, credit_limit, rating) VALUES
('VEN001', 'Tech Solutions Inc', 1, 'John Smith', 'john@techsolutions.com', '555-0101', 
 1, 1, 1, 1, 100000, 4.5),
('VEN002', 'Global Supplies Ltd', 4, 'Sarah Johnson', 'sarah@globalsupplies.com', '555-0102', 
 NULL, NULL, 3, 2, 150000, 4.8),
('VEN003', 'Asian Traders Co', 5, 'Wei Zhang', 'wei@asiantraders.com', '555-0103', 
 NULL, NULL, 6, 3, 200000, 4.2),
('VEN004', 'Euro Parts GmbH', 1, 'Hans Mueller', 'hans@europarts.de', '555-0104', 
 NULL, NULL, 4, 1, 120000, 4.6),
('VEN005', 'Pacific Imports', 5, 'Yuki Tanaka', 'yuki@pacificimports.jp', '555-0105', 
 NULL, NULL, 7, 1, 180000, 4.7),
('VEN006', 'India Vendors Pvt', 4, 'Raj Kumar', 'raj@indiavendors.in', '555-0106', 
 10, 10, 8, 2, 90000, 4.3),
('VEN007', 'Latin America Trade', 3, 'Carlos Rodriguez', 'carlos@latinamerica.com', '555-0107', 
 NULL, NULL, 10, 1, 110000, 4.4),
('VEN008', 'Middle East Supply', 5, 'Ahmed Hassan', 'ahmed@mesupply.ae', '555-0108', 
 NULL, NULL, 12, 3, 160000, 4.5),
('VEN009', 'Australian Goods', 2, 'Emma Wilson', 'emma@ausgood.au', '555-0109', 
 NULL, NULL, 9, 1, 130000, 4.6),
('VEN010', 'Canadian Resources', 2, 'Michael Brown', 'michael@canresources.ca', '555-0110', 
 7, 7, 2, 2, 140000, 4.7);

-- Insert Customers
INSERT INTO customers (customer_code, customer_name, customer_type_id, contact_person, email, phone,
                       city_id, state_id, country_id, payment_term_id, credit_limit, rating) VALUES
('CUST001', 'Mega Retail Corp', 4, 'Lisa Anderson', 'lisa@megaretail.com', '555-0201',
 5, 5, 1, 1, 500000, 4.8),
('CUST002', 'Small Business LLC', 2, 'Tom Williams', 'tom@smallbiz.com', '555-0202',
 3, 3, 1, 1, 100000, 4.5),
('CUST003', 'Individual Buyer', 1, 'Jane Doe', 'jane@email.com', '555-0203',
 6, 6, 1, 5, 10000, 4.0),
('CUST004', 'Government Agency', 3, 'Robert Smith', 'robert@gov.us', '555-0204',
 1, 1, 1, 2, 1000000, 4.9),
('CUST005', 'European Chain', 2, 'Pierre Dubois', 'pierre@eurochain.fr', '555-0205',
 NULL, NULL, 5, 2, 300000, 4.7);

-- Insert Products
INSERT INTO products (product_code, product_name, category_id, brand_id, uom_id, 
                      unit_price, cost_price, stock_quantity, reorder_level, tax_id) VALUES
('PROD001', 'Dell Laptop i7', 4, 1, 1, 1200.00, 800.00, 50, 10, 4),
('PROD002', 'HP Desktop Computer', 4, 2, 1, 950.00, 650.00, 30, 5, 4),
('PROD003', 'Apple MacBook Pro', 4, 3, 1, 2500.00, 1800.00, 20, 5, 4),
('PROD004', 'Lenovo ThinkPad', 4, 4, 1, 1100.00, 750.00, 40, 8, 4),
('PROD005', 'Logitech Wireless Mouse', 5, 5, 1, 50.00, 28.00, 250, 50, 4),
('PROD006', 'Logitech Keyboard', 5, 5, 1, 80.00, 45.00, 200, 40, 4),
('PROD007', 'Dell 27" Monitor', 4, 1, 1, 400.00, 250.00, 75, 15, 4),
('PROD008', 'Herman Miller Office Chair', 6, 6, 1, 850.00, 500.00, 25, 5, 4),
('PROD009', 'Office Desk', 6, 7, 1, 350.00, 200.00, 40, 10, 4),
('PROD010', 'A4 Notebook Pack', 3, 7, 5, 25.00, 12.00, 500, 100, 3);

-- Insert Purchase Orders
INSERT INTO purchase_orders (po_number, vendor_id, order_date, status_id, payment_term_id, payment_method_id,
                             subtotal, tax_amount, total_amount) VALUES
('PO-2025-001', 1, '2025-01-15', 6, 1, 3, 60000.00, 4800.00, 64800.00),
('PO-2025-002', 2, '2025-01-20', 6, 2, 3, 75000.00, 6000.00, 81000.00),
('PO-2025-003', 3, '2025-02-01', 6, 3, 3, 120000.00, 9600.00, 129600.00),
('PO-2025-004', 4, '2025-02-10', 6, 1, 3, 45000.00, 3600.00, 48600.00),
('PO-2025-005', 5, '2025-03-05', 6, 1, 3, 95000.00, 7600.00, 102600.00),
('PO-2025-006', 1, '2025-03-15', 6, 1, 3, 85000.00, 6800.00, 91800.00),
('PO-2025-007', 2, '2025-04-01', 6, 2, 3, 110000.00, 8800.00, 118800.00),
('PO-2025-008', 3, '2025-04-20', 6, 3, 3, 135000.00, 10800.00, 145800.00),
('PO-2025-009', 6, '2025-05-10', 6, 2, 3, 55000.00, 4400.00, 59400.00),
('PO-2025-010', 7, '2025-05-25', 6, 1, 3, 72000.00, 5760.00, 77760.00),
('PO-2025-011', 1, '2025-06-05', 6, 1, 3, 92000.00, 7360.00, 99360.00),
('PO-2025-012', 8, '2025-06-18', 6, 3, 3, 108000.00, 8640.00, 116640.00),
('PO-2025-013', 3, '2025-07-02', 6, 3, 3, 145000.00, 11600.00, 156600.00),
('PO-2025-014', 9, '2025-07-20', 6, 1, 3, 68000.00, 5440.00, 73440.00),
('PO-2025-015', 10, '2025-08-10', 6, 2, 3, 88000.00, 7040.00, 95040.00);

-- Insert Vendor Payments (VENDOR REVENUE!)
INSERT INTO vendor_payments (payment_number, vendor_id, po_id, payment_date, payment_method_id, amount, created_by) VALUES
('PAY-V-001', 1, 1, '2025-02-15', 3, 64800.00, 'system'),
('PAY-V-002', 2, 2, '2025-02-25', 3, 81000.00, 'system'),
('PAY-V-003', 3, 3, '2025-03-10', 3, 129600.00, 'system'),
('PAY-V-004', 4, 4, '2025-03-20', 3, 48600.00, 'system'),
('PAY-V-005', 5, 5, '2025-04-10', 3, 102600.00, 'system'),
('PAY-V-006', 1, 6, '2025-04-20', 3, 91800.00, 'system'),
('PAY-V-007', 2, 7, '2025-05-05', 3, 118800.00, 'system'),
('PAY-V-008', 3, 8, '2025-05-25', 3, 145800.00, 'system'),
('PAY-V-009', 6, 9, '2025-06-15', 3, 59400.00, 'system'),
('PAY-V-010', 7, 10, '2025-06-30', 3, 77760.00, 'system'),
('PAY-V-011', 1, 11, '2025-07-10', 3, 99360.00, 'system'),
('PAY-V-012', 8, 12, '2025-07-25', 3, 116640.00, 'system'),
('PAY-V-013', 3, 13, '2025-08-08', 3, 156600.00, 'system'),
('PAY-V-014', 9, 14, '2025-08-25', 3, 73440.00, 'system'),
('PAY-V-015', 10, 15, '2025-09-10', 3, 95040.00, 'system');

SELECT '✅ Part 4: Transaction data inserted' as Status;

-- ============================================
-- PART 5: CREATE VIEWS
-- ============================================

-- Vendor Revenue Summary View
CREATE OR REPLACE VIEW vendor_revenue_summary AS
SELECT 
    v.vendor_id,
    v.vendor_code,
    v.vendor_name,
    vc.category_name as vendor_category,
    c.country_name,
    s.state_name,
    ct.city_name,
    COUNT(DISTINCT po.po_id) as total_orders,
    COALESCE(SUM(vp.amount), 0) as total_revenue,
    COALESCE(AVG(vp.amount), 0) as avg_order_value,
    MAX(vp.payment_date) as last_payment_date,
    v.rating as vendor_rating
FROM vendors v
LEFT JOIN vendor_categories vc ON v.vendor_category_id = vc.vendor_category_id
LEFT JOIN countries c ON v.country_id = c.country_id
LEFT JOIN states s ON v.state_id = s.state_id
LEFT JOIN cities ct ON v.city_id = ct.city_id
LEFT JOIN purchase_orders po ON v.vendor_id = po.vendor_id
LEFT JOIN vendor_payments vp ON v.vendor_id = vp.vendor_id
WHERE v.is_active = TRUE
GROUP BY v.vendor_id, v.vendor_code, v.vendor_name, vc.category_name, 
         c.country_name, s.state_name, ct.city_name, v.rating;

-- Top Vendors by Revenue
CREATE OR REPLACE VIEW top_vendors_by_revenue AS
SELECT 
    vendor_name,
    country_name as country,
    vendor_category,
    total_orders,
    total_revenue,
    avg_order_value,
    vendor_rating
FROM vendor_revenue_summary
WHERE total_revenue > 0
ORDER BY total_revenue DESC;

-- Vendor Revenue by Country
CREATE OR REPLACE VIEW vendor_revenue_by_country AS
SELECT 
    c.country_name,
    COUNT(DISTINCT v.vendor_id) as vendor_count,
    COALESCE(SUM(vp.amount), 0) as total_revenue
FROM countries c
LEFT JOIN vendors v ON c.country_id = v.country_id AND v.is_active = TRUE
LEFT JOIN vendor_payments vp ON v.vendor_id = vp.vendor_id
GROUP BY c.country_name
HAVING total_revenue > 0
ORDER BY total_revenue DESC;

-- Product Catalog View
CREATE OR REPLACE VIEW product_catalog AS
SELECT 
    p.product_id,
    p.product_code,
    p.product_name,
    pc.category_name,
    b.brand_name,
    uom.uom_name as unit,
    p.unit_price,
    p.cost_price,
    p.stock_quantity,
    p.reorder_level,
    p.is_active
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN brands b ON p.brand_id = b.brand_id
LEFT JOIN units_of_measure uom ON p.uom_id = uom.uom_id;

SELECT '✅ Part 5: Views created' as Status;

-- ============================================
-- FINAL VERIFICATION
-- ============================================

SELECT '========================================' as '';
SELECT '   MIGRATION COMPLETED SUCCESSFULLY' as '';
SELECT '========================================' as '';

-- Identity Database Summary
USE chatbot_identity;
SELECT 'Identity Database (chatbot_identity):' as Info;
SELECT COUNT(*) as Total_Tables FROM information_schema.tables WHERE table_schema='chatbot_identity';

-- ERP Database Summary
USE erp_demo;
SELECT 'ERP Database (erp_demo):' as Info;
SELECT 
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='erp_demo' AND table_type='BASE TABLE') as Total_Tables,
    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='erp_demo' AND table_type='VIEW') as Total_Views;

SELECT 'Master Data Summary:' as Info;
SELECT 
    (SELECT COUNT(*) FROM countries) as Countries,
    (SELECT COUNT(*) FROM states) as States,
    (SELECT COUNT(*) FROM cities) as Cities,
    (SELECT COUNT(*) FROM product_categories) as Product_Categories,
    (SELECT COUNT(*) FROM brands) as Brands,
    (SELECT COUNT(*) FROM payment_terms) as Payment_Terms,
    (SELECT COUNT(*) FROM payment_methods) as Payment_Methods;

SELECT 'Transaction Data Summary:' as Info;
SELECT 
    (SELECT COUNT(*) FROM vendors) as Vendors,
    (SELECT COUNT(*) FROM customers) as Customers,
    (SELECT COUNT(*) FROM products) as Products,
    (SELECT COUNT(*) FROM purchase_orders) as Purchase_Orders,
    (SELECT COUNT(*) FROM vendor_payments) as Vendor_Payments,
    (SELECT CONCAT('$', FORMAT(SUM(amount), 2)) FROM vendor_payments) as Total_Vendor_Revenue;

-- Test the revenue query
SELECT 'Top 10 Vendors by Revenue:' as Test_Query;
SELECT 
    vendor_name,
    country,
    CONCAT('$', FORMAT(total_revenue, 2)) as revenue,
    vendor_rating as rating
FROM top_vendors_by_revenue
LIMIT 10;

SELECT '✅ ALL MIGRATIONS COMPLETED!' as Final_Status;
SELECT '🎉 Database is ready for use!' as Message;

