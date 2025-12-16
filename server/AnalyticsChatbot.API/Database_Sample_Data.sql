-- ============================================
-- SAMPLE DATA FOR BASE TABLES
-- ============================================

USE erp_demo;

-- ============================================
-- 1. INSERT LOCATION DATA
-- ============================================

-- Countries
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

-- States (USA)
INSERT INTO states (state_code, state_name, country_id) VALUES
('NY', 'New York', 1),
('CA', 'California', 1),
('TX', 'Texas', 1),
('FL', 'Florida', 1),
('IL', 'Illinois', 1),
('WA', 'Washington', 1);

-- States (Canada)
INSERT INTO states (state_code, state_name, country_id) VALUES
('ON', 'Ontario', 2),
('QC', 'Quebec', 2),
('BC', 'British Columbia', 2);

-- States (India)
INSERT INTO states (state_code, state_name, country_id) VALUES
('MH', 'Maharashtra', 8),
('DL', 'Delhi', 8),
('KA', 'Karnataka', 8),
('TN', 'Tamil Nadu', 8);

-- Cities (USA)
INSERT INTO cities (city_name, state_id) VALUES
('New York', 1),
('Los Angeles', 2),
('Houston', 3),
('Miami', 4),
('Chicago', 5),
('Seattle', 6);

-- Cities (Canada)
INSERT INTO cities (city_name, state_id) VALUES
('Toronto', 7),
('Montreal', 8),
('Vancouver', 9);

-- Cities (India)
INSERT INTO cities (city_name, state_id) VALUES
('Mumbai', 10),
('Delhi', 11),
('Bangalore', 12),
('Chennai', 13);

-- Cities (Other - without state)
INSERT INTO cities (city_name, state_id) VALUES
('London', 1),
('Berlin', 1),
('Paris', 1),
('Shanghai', 1),
('Tokyo', 1),
('Dubai', 1),
('Singapore', 1),
('Sydney', 1),
('Mexico City', 1);

-- ============================================
-- 2. INSERT PRODUCT MASTER DATA
-- ============================================

-- Product Categories
INSERT INTO product_categories (category_code, category_name, parent_category_id, description) VALUES
('ELEC', 'Electronics', NULL, 'Electronic devices and equipment'),
('FURN', 'Furniture', NULL, 'Office and home furniture'),
('STAT', 'Stationery', NULL, 'Office supplies and stationery'),
('COMP', 'Computers', 1, 'Computer hardware and peripherals'),
('ACCS', 'Accessories', 1, 'Electronic accessories'),
('OFF-FURN', 'Office Furniture', 2, 'Office furniture items'),
('HOME-FURN', 'Home Furniture', 2, 'Home furniture items');

-- Units of Measure
INSERT INTO units_of_measure (uom_code, uom_name, uom_type, base_unit) VALUES
('EA', 'Each', 'Quantity', TRUE),
('PC', 'Piece', 'Quantity', FALSE),
('SET', 'Set', 'Quantity', FALSE),
('BOX', 'Box', 'Quantity', FALSE),
('PACK', 'Pack', 'Quantity', FALSE),
('DOZ', 'Dozen', 'Quantity', FALSE),
('KG', 'Kilogram', 'Weight', TRUE),
('LB', 'Pound', 'Weight', FALSE),
('L', 'Liter', 'Volume', TRUE),
('GAL', 'Gallon', 'Volume', FALSE);

-- Brands
INSERT INTO brands (brand_code, brand_name, description, website) VALUES
('DELL', 'Dell Technologies', 'Computer hardware', 'www.dell.com'),
('HP', 'HP Inc', 'Computing and printing', 'www.hp.com'),
('APPLE', 'Apple Inc', 'Consumer electronics', 'www.apple.com'),
('LENOVO', 'Lenovo', 'Computing devices', 'www.lenovo.com'),
('LOGITECH', 'Logitech', 'Computer peripherals', 'www.logitech.com'),
('IKEA', 'IKEA', 'Furniture and home goods', 'www.ikea.com'),
('HERMAN-M', 'Herman Miller', 'Premium office furniture', 'www.hermanmiller.com'),
('GENERIC', 'Generic Brand', 'Unbranded products', NULL);

-- ============================================
-- 3. INSERT FINANCIAL MASTER DATA
-- ============================================

-- Payment Terms
INSERT INTO payment_terms (term_code, term_name, days, discount_percent, discount_days) VALUES
('NET30', 'Net 30 Days', 30, 0, 0),
('NET45', 'Net 45 Days', 45, 0, 0),
('NET60', 'Net 60 Days', 60, 0, 0),
('NET15', 'Net 15 Days', 15, 0, 0),
('2-10-NET30', '2/10 Net 30', 30, 2.0, 10),
('COD', 'Cash on Delivery', 0, 0, 0),
('DUE-RECEIPT', 'Due on Receipt', 0, 0, 0);

-- Tax Rates
INSERT INTO tax_rates (tax_code, tax_name, tax_rate, country_id, effective_date) VALUES
('VAT-20', 'VAT 20%', 20.00, 3, '2020-01-01'),
('GST-18', 'GST 18%', 18.00, 8, '2020-01-01'),
('GST-12', 'GST 12%', 12.00, 8, '2020-01-01'),
('GST-5', 'GST 5%', 5.00, 8, '2020-01-01'),
('SALES-TAX-8', 'Sales Tax 8%', 8.00, 1, '2020-01-01'),
('SALES-TAX-10', 'Sales Tax 10%', 10.00, 1, '2020-01-01'),
('VAT-19', 'VAT 19%', 19.00, 4, '2020-01-01'),
('NO-TAX', 'No Tax', 0.00, NULL, '2020-01-01');

-- Payment Methods
INSERT INTO payment_methods (method_code, method_name, processing_fee_percent) VALUES
('CASH', 'Cash', 0.00),
('CHECK', 'Check', 0.00),
('WIRE', 'Wire Transfer', 0.50),
('CREDIT', 'Credit Card', 2.50),
('DEBIT', 'Debit Card', 1.50),
('ONLINE', 'Online Payment', 2.00),
('ACH', 'ACH Transfer', 0.25),
('PAYPAL', 'PayPal', 2.90);

-- ============================================
-- 4. INSERT VENDOR DATA
-- ============================================

-- Vendor Categories
INSERT INTO vendor_categories (category_code, category_name, description) VALUES
('IT-HARD', 'IT Hardware', 'Computer and IT equipment vendors'),
('IT-SOFT', 'IT Software', 'Software and license vendors'),
('FURNITURE', 'Furniture Suppliers', 'Office and home furniture vendors'),
('STATIONERY', 'Stationery Suppliers', 'Office supplies vendors'),
('ELECTRONICS', 'Electronics', 'Electronic equipment vendors'),
('SERVICES', 'Services', 'Service providers');

-- Vendors
INSERT INTO vendors (vendor_code, vendor_name, vendor_category_id, contact_person, email, phone, 
                     city_id, state_id, country_id, payment_term_id, credit_limit, rating) VALUES
('VEN001', 'Tech Solutions Inc', 1, 'John Smith', 'john@techsolutions.com', '555-0101', 
 1, 1, 1, 1, 100000, 4.5),
('VEN002', 'Global Supplies Ltd', 4, 'Sarah Johnson', 'sarah@globalsupplies.com', '555-0102', 
 14, NULL, 3, 2, 150000, 4.8),
('VEN003', 'Asian Traders Co', 5, 'Wei Zhang', 'wei@asiantraders.com', '555-0103', 
 17, NULL, 6, 3, 200000, 4.2),
('VEN004', 'Euro Parts GmbH', 1, 'Hans Mueller', 'hans@europarts.de', '555-0104', 
 15, NULL, 4, 1, 120000, 4.6),
('VEN005', 'Pacific Imports', 5, 'Yuki Tanaka', 'yuki@pacificimports.jp', '555-0105', 
 18, NULL, 7, 1, 180000, 4.7),
('VEN006', 'India Vendors Pvt', 4, 'Raj Kumar', 'raj@indiavendors.in', '555-0106', 
 10, 10, 8, 2, 90000, 4.3),
('VEN007', 'Latin America Trade', 3, 'Carlos Rodriguez', 'carlos@latinamerica.com', '555-0107', 
 22, NULL, 10, 1, 110000, 4.4),
('VEN008', 'Middle East Supply', 5, 'Ahmed Hassan', 'ahmed@mesupply.ae', '555-0108', 
 19, NULL, 12, 3, 160000, 4.5),
('VEN009', 'Australian Goods', 2, 'Emma Wilson', 'emma@ausgood.au', '555-0109', 
 21, NULL, 9, 1, 130000, 4.6),
('VEN010', 'Canadian Resources', 6, 'Michael Brown', 'michael@canresources.ca', '555-0110', 
 7, 7, 2, 2, 140000, 4.7);

-- ============================================
-- 5. INSERT CUSTOMER DATA
-- ============================================

-- Customer Types
INSERT INTO customer_types (type_code, type_name, description, default_discount_percent) VALUES
('IND', 'Individual', 'Individual customers', 0.00),
('CORP', 'Corporate', 'Corporate clients', 5.00),
('GOV', 'Government', 'Government agencies', 3.00),
('WHSL', 'Wholesale', 'Wholesale buyers', 10.00),
('RETAIL', 'Retail', 'Retail chains', 7.00);

-- Customers
INSERT INTO customers (customer_code, customer_name, customer_type_id, contact_person, email, phone,
                       city_id, state_id, country_id, payment_term_id, credit_limit, rating) VALUES
('CUST001', 'Mega Retail Corp', 5, 'Lisa Anderson', 'lisa@megaretail.com', '555-0201',
 5, 5, 1, 1, 500000, 4.8),
('CUST002', 'Small Business LLC', 2, 'Tom Williams', 'tom@smallbiz.com', '555-0202',
 3, 3, 1, 1, 100000, 4.5),
('CUST003', 'Individual Buyer', 1, 'Jane Doe', 'jane@email.com', '555-0203',
 6, 6, 1, 7, 10000, 4.0),
('CUST004', 'Government Agency', 3, 'Robert Smith', 'robert@gov.us', '555-0204',
 1, 1, 1, 2, 1000000, 4.9),
('CUST005', 'European Chain', 4, 'Pierre Dubois', 'pierre@eurochain.fr', '555-0205',
 16, NULL, 5, 2, 300000, 4.7);

-- ============================================
-- 6. INSERT PRODUCT DATA
-- ============================================

-- Products
INSERT INTO products (product_code, product_name, category_id, brand_id, uom_id, 
                      unit_price, cost_price, stock_quantity, reorder_level, tax_id) VALUES
('PROD001', 'Dell Laptop i7', 4, 1, 1, 1200.00, 800.00, 50, 10, 5),
('PROD002', 'HP Desktop Computer', 4, 2, 1, 950.00, 650.00, 30, 5, 5),
('PROD003', 'Apple MacBook Pro', 4, 3, 1, 2500.00, 1800.00, 20, 5, 5),
('PROD004', 'Lenovo ThinkPad', 4, 4, 1, 1100.00, 750.00, 40, 8, 5),
('PROD005', 'Logitech Wireless Mouse', 5, 5, 1, 50.00, 28.00, 250, 50, 5),
('PROD006', 'Logitech Keyboard', 5, 5, 1, 80.00, 45.00, 200, 40, 5),
('PROD007', 'Dell 27" Monitor', 4, 1, 1, 400.00, 250.00, 75, 15, 5),
('PROD008', 'Herman Miller Office Chair', 6, 7, 1, 850.00, 500.00, 25, 5, 5),
('PROD009', 'IKEA Office Desk', 6, 6, 1, 350.00, 200.00, 40, 10, 5),
('PROD010', 'A4 Notebook Pack (10pcs)', 3, 8, 5, 25.00, 12.00, 500, 100, 4),
('PROD011', 'Professional Pen Set', 3, 8, 3, 35.00, 18.00, 300, 50, 4),
('PROD012', 'Laser Printer HP', 4, 2, 1, 450.00, 280.00, 30, 8, 5),
('PROD013', 'Filing Cabinet 4-Drawer', 6, 8, 1, 280.00, 160.00, 40, 10, 5),
('PROD014', 'Wireless Headset', 5, 5, 1, 120.00, 70.00, 150, 30, 5),
('PROD015', 'USB Flash Drive 64GB', 5, 8, 1, 20.00, 10.00, 500, 100, 4);

-- ============================================
-- 7. INSERT ORDER STATUS DATA
-- ============================================

-- Order Statuses
INSERT INTO order_statuses (status_code, status_name, status_type, sort_order) VALUES
('DRAFT', 'Draft', 'Both', 1),
('PENDING', 'Pending', 'Both', 2),
('APPROVED', 'Approved', 'Both', 3),
('PROCESSING', 'Processing', 'Both', 4),
('SHIPPED', 'Shipped', 'Sales', 5),
('RECEIVED', 'Received', 'Purchase', 5),
('DELIVERED', 'Delivered', 'Sales', 6),
('COMPLETED', 'Completed', 'Both', 7),
('CANCELLED', 'Cancelled', 'Both', 10),
('ON-HOLD', 'On Hold', 'Both', 8);

-- ============================================
-- 8. INSERT TRANSACTION DATA
-- ============================================

-- Purchase Orders
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

-- Vendor Payments
INSERT INTO vendor_payments (payment_number, vendor_id, po_id, payment_date, payment_method_id, amount) VALUES
('PAY-V-001', 1, 1, '2025-02-15', 3, 64800.00),
('PAY-V-002', 2, 2, '2025-02-25', 3, 81000.00),
('PAY-V-003', 3, 3, '2025-03-10', 3, 129600.00),
('PAY-V-004', 4, 4, '2025-03-20', 3, 48600.00),
('PAY-V-005', 5, 5, '2025-04-10', 3, 102600.00),
('PAY-V-006', 1, 6, '2025-04-20', 3, 91800.00),
('PAY-V-007', 2, 7, '2025-05-05', 3, 118800.00),
('PAY-V-008', 3, 8, '2025-05-25', 3, 145800.00),
('PAY-V-009', 6, 9, '2025-06-15', 3, 59400.00),
('PAY-V-010', 7, 10, '2025-06-30', 3, 77760.00),
('PAY-V-011', 1, 11, '2025-07-10', 3, 99360.00),
('PAY-V-012', 8, 12, '2025-07-25', 3, 116640.00),
('PAY-V-013', 3, 13, '2025-08-08', 3, 156600.00),
('PAY-V-014', 9, 14, '2025-08-25', 3, 73440.00),
('PAY-V-015', 10, 15, '2025-09-10', 3, 95040.00);

-- Sales Orders
INSERT INTO sales_orders (so_number, customer_id, order_date, status_id, payment_term_id, payment_method_id,
                          subtotal, tax_amount, total_amount, payment_status) VALUES
('SO-2025-001', 1, '2025-01-20', 7, 1, 6, 85000.00, 6800.00, 91800.00, 'Paid'),
('SO-2025-002', 2, '2025-02-05', 7, 1, 4, 45000.00, 3600.00, 48600.00, 'Paid'),
('SO-2025-003', 1, '2025-03-10', 7, 1, 6, 120000.00, 9600.00, 129600.00, 'Paid'),
('SO-2025-004', 3, '2025-04-15', 7, 7, 1, 12000.00, 960.00, 12960.00, 'Paid'),
('SO-2025-005', 4, '2025-05-20', 7, 2, 7, 250000.00, 20000.00, 270000.00, 'Paid');

-- Customer Payments
INSERT INTO customer_payments (payment_number, customer_id, so_id, payment_date, payment_method_id, amount) VALUES
('PAY-C-001', 1, 1, '2025-02-19', 6, 91800.00),
('PAY-C-002', 2, 2, '2025-03-07', 4, 48600.00),
('PAY-C-003', 1, 3, '2025-04-09', 6, 129600.00),
('PAY-C-004', 3, 4, '2025-04-15', 1, 12960.00),
('PAY-C-005', 4, 5, '2025-06-19', 7, 270000.00);

SELECT '✅ Sample data inserted successfully!' as Status;

-- Summary statistics
SELECT 
    (SELECT COUNT(*) FROM countries) as Countries,
    (SELECT COUNT(*) FROM states) as States,
    (SELECT COUNT(*) FROM cities) as Cities,
    (SELECT COUNT(*) FROM vendors) as Vendors,
    (SELECT COUNT(*) FROM customers) as Customers,
    (SELECT COUNT(*) FROM products) as Products,
    (SELECT COUNT(*) FROM purchase_orders) as PurchaseOrders,
    (SELECT COUNT(*) FROM vendor_payments) as VendorPayments,
    (SELECT CONCAT('$', FORMAT(SUM(amount), 2)) FROM vendor_payments) as TotalVendorRevenue;

