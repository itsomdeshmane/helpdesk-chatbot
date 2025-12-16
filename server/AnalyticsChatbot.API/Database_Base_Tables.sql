-- ============================================
-- BASE/MASTER DATA TABLES
-- Properly normalized reference tables
-- ============================================

DROP DATABASE IF EXISTS erp_demo;
CREATE DATABASE erp_demo;
USE erp_demo;

-- ============================================
-- 1. LOCATION MASTER TABLES
-- ============================================

-- Countries Table
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

-- States/Regions Table
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

-- Cities Table
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

-- ============================================
-- 2. PRODUCT MASTER TABLES
-- ============================================

-- Product Categories Table
CREATE TABLE product_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    parent_category_id INT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES product_categories(category_id),
    INDEX idx_category_name (category_name),
    INDEX idx_parent_category (parent_category_id)
);

-- Units of Measure Table
CREATE TABLE units_of_measure (
    uom_id INT PRIMARY KEY AUTO_INCREMENT,
    uom_code VARCHAR(20) UNIQUE NOT NULL,
    uom_name VARCHAR(50) UNIQUE NOT NULL,
    uom_type ENUM('Weight', 'Volume', 'Length', 'Quantity', 'Time') NOT NULL,
    base_unit BOOLEAN DEFAULT FALSE,
    conversion_factor DECIMAL(15, 6) DEFAULT 1.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_uom_code (uom_code),
    INDEX idx_uom_type (uom_type)
);

-- Brands Table
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

-- ============================================
-- 3. FINANCIAL MASTER TABLES
-- ============================================

-- Payment Terms Table
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

-- Tax Rates Table
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
    INDEX idx_tax_code (tax_code),
    INDEX idx_country_id (country_id)
);

-- Payment Methods Table
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

-- ============================================
-- 4. VENDOR MASTER TABLES
-- ============================================

-- Vendor Categories Table
CREATE TABLE vendor_categories (
    vendor_category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_code VARCHAR(50) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category_name (category_name)
);

-- Vendors Table (Enhanced with Foreign Keys)
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
    INDEX idx_vendor_category (vendor_category_id),
    INDEX idx_is_active (is_active)
);

-- ============================================
-- 5. CUSTOMER MASTER TABLES
-- ============================================

-- Customer Types Table
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

-- Customers Table (Enhanced with Foreign Keys)
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
    INDEX idx_country_id (country_id),
    INDEX idx_customer_type (customer_type_id),
    INDEX idx_is_active (is_active)
);

-- ============================================
-- 6. PRODUCT TABLES (Enhanced)
-- ============================================

-- Products Table (Enhanced with Foreign Keys)
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
    max_order_quantity INT NULL,
    weight DECIMAL(10, 3),
    length DECIMAL(10, 2),
    width DECIMAL(10, 2),
    height DECIMAL(10, 2),
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
    INDEX idx_category_id (category_id),
    INDEX idx_brand_id (brand_id),
    INDEX idx_barcode (barcode),
    INDEX idx_sku (sku)
);

-- ============================================
-- 7. ORDER STATUS TABLES
-- ============================================

-- Order Status Table
CREATE TABLE order_statuses (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    status_code VARCHAR(20) UNIQUE NOT NULL,
    status_name VARCHAR(100) NOT NULL,
    status_type ENUM('Purchase', 'Sales', 'Both') NOT NULL,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status_code (status_code),
    INDEX idx_status_type (status_type)
);

-- ============================================
-- 8. PURCHASE ORDERS (Using Foreign Keys)
-- ============================================

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
    shipping_address TEXT,
    billing_address TEXT,
    notes TEXT,
    created_by VARCHAR(100),
    approved_by VARCHAR(100),
    approved_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (status_id) REFERENCES order_statuses(status_id),
    FOREIGN KEY (payment_term_id) REFERENCES payment_terms(term_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id),
    INDEX idx_vendor_id (vendor_id),
    INDEX idx_order_date (order_date),
    INDEX idx_status_id (status_id)
);

CREATE TABLE purchase_order_items (
    po_item_id INT PRIMARY KEY AUTO_INCREMENT,
    po_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    tax_id INT,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) NOT NULL,
    received_quantity INT DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (tax_id) REFERENCES tax_rates(tax_id),
    INDEX idx_po_id (po_id),
    INDEX idx_product_id (product_id)
);

-- ============================================
-- 9. SALES ORDERS (Using Foreign Keys)
-- ============================================

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
    shipping_address TEXT,
    billing_address TEXT,
    notes TEXT,
    created_by VARCHAR(100),
    approved_by VARCHAR(100),
    approved_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (status_id) REFERENCES order_statuses(status_id),
    FOREIGN KEY (payment_term_id) REFERENCES payment_terms(term_id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(payment_method_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_order_date (order_date),
    INDEX idx_status_id (status_id)
);

CREATE TABLE sales_order_items (
    so_item_id INT PRIMARY KEY AUTO_INCREMENT,
    so_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    tax_id INT,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    discount_amount DECIMAL(15, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) NOT NULL,
    notes TEXT,
    FOREIGN KEY (so_id) REFERENCES sales_orders(so_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (tax_id) REFERENCES tax_rates(tax_id),
    INDEX idx_so_id (so_id),
    INDEX idx_product_id (product_id)
);

-- ============================================
-- 10. PAYMENT TABLES
-- ============================================

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
    INDEX idx_payment_date (payment_date),
    INDEX idx_payment_method (payment_method_id)
);

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
    INDEX idx_payment_date (payment_date),
    INDEX idx_payment_method (payment_method_id)
);

SELECT '✅ All base tables created successfully!' as Status;
SHOW TABLES;

