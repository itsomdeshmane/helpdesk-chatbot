-- ============================================
-- DATABASE VIEWS FOR REPORTING
-- ============================================

USE erp_demo;

-- ============================================
-- VENDOR REVENUE VIEWS
-- ============================================

-- Vendor Revenue Summary (with location details)
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
    COALESCE(MAX(vp.amount), 0) as max_payment,
    COALESCE(MIN(vp.amount), 0) as min_payment,
    MAX(vp.payment_date) as last_payment_date,
    v.rating as vendor_rating,
    v.credit_limit
FROM vendors v
LEFT JOIN vendor_categories vc ON v.vendor_category_id = vc.vendor_category_id
LEFT JOIN countries c ON v.country_id = c.country_id
LEFT JOIN states s ON v.state_id = s.state_id
LEFT JOIN cities ct ON v.city_id = ct.city_id
LEFT JOIN purchase_orders po ON v.vendor_id = po.vendor_id
LEFT JOIN vendor_payments vp ON v.vendor_id = vp.vendor_id
WHERE v.is_active = TRUE
GROUP BY v.vendor_id, v.vendor_code, v.vendor_name, vc.category_name, 
         c.country_name, s.state_name, ct.city_name, v.rating, v.credit_limit;

-- Top Vendors by Revenue
CREATE OR REPLACE VIEW top_vendors_by_revenue AS
SELECT 
    vendor_name,
    country_name as country,
    vendor_category,
    total_orders,
    CONCAT('$', FORMAT(total_revenue, 2)) as revenue,
    CONCAT('$', FORMAT(avg_order_value, 2)) as avg_order_value,
    vendor_rating as rating
FROM vendor_revenue_summary
WHERE total_revenue > 0
ORDER BY total_revenue DESC;

-- Vendor Revenue by Country
CREATE OR REPLACE VIEW vendor_revenue_by_country AS
SELECT 
    c.country_name,
    COUNT(DISTINCT v.vendor_id) as vendor_count,
    COUNT(DISTINCT po.po_id) as total_orders,
    COALESCE(SUM(vp.amount), 0) as total_revenue,
    COALESCE(AVG(vp.amount), 0) as avg_payment
FROM countries c
LEFT JOIN vendors v ON c.country_id = v.country_id AND v.is_active = TRUE
LEFT JOIN purchase_orders po ON v.vendor_id = po.vendor_id
LEFT JOIN vendor_payments vp ON v.vendor_id = vp.vendor_id
GROUP BY c.country_name
HAVING total_revenue > 0
ORDER BY total_revenue DESC;

-- Monthly Vendor Performance
CREATE OR REPLACE VIEW monthly_vendor_performance AS
SELECT 
    v.vendor_id,
    v.vendor_name,
    c.country_name,
    YEAR(vp.payment_date) as year,
    MONTH(vp.payment_date) as month,
    MONTHNAME(vp.payment_date) as month_name,
    DATE_FORMAT(vp.payment_date, '%Y-%m') as year_month,
    COUNT(vp.payment_id) as payment_count,
    SUM(vp.amount) as monthly_revenue,
    AVG(vp.amount) as avg_payment
FROM vendors v
JOIN countries c ON v.country_id = c.country_id
JOIN vendor_payments vp ON v.vendor_id = vp.vendor_id
GROUP BY v.vendor_id, v.vendor_name, c.country_name, 
         YEAR(vp.payment_date), MONTH(vp.payment_date)
ORDER BY year DESC, month DESC, monthly_revenue DESC;

-- ============================================
-- CUSTOMER REVENUE VIEWS
-- ============================================

-- Customer Revenue Summary
CREATE OR REPLACE VIEW customer_revenue_summary AS
SELECT 
    cust.customer_id,
    cust.customer_code,
    cust.customer_name,
    ct.type_name as customer_type,
    c.country_name,
    s.state_name,
    city.city_name,
    COUNT(DISTINCT so.so_id) as total_orders,
    COALESCE(SUM(cp.amount), 0) as total_revenue,
    COALESCE(AVG(cp.amount), 0) as avg_order_value,
    MAX(cp.payment_date) as last_payment_date,
    cust.rating as customer_rating,
    cust.credit_limit
FROM customers cust
LEFT JOIN customer_types ct ON cust.customer_type_id = ct.customer_type_id
LEFT JOIN countries c ON cust.country_id = c.country_id
LEFT JOIN states s ON cust.state_id = s.state_id
LEFT JOIN cities city ON cust.city_id = city.city_id
LEFT JOIN sales_orders so ON cust.customer_id = so.customer_id
LEFT JOIN customer_payments cp ON cust.customer_id = cp.customer_id
WHERE cust.is_active = TRUE
GROUP BY cust.customer_id, cust.customer_code, cust.customer_name, ct.type_name,
         c.country_name, s.state_name, city.city_name, cust.rating, cust.credit_limit;

-- ============================================
-- PRODUCT VIEWS
-- ============================================

-- Product Catalog View
CREATE OR REPLACE VIEW product_catalog AS
SELECT 
    p.product_id,
    p.product_code,
    p.product_name,
    pc.category_name,
    b.brand_name,
    uom.uom_name as unit,
    CONCAT('$', FORMAT(p.unit_price, 2)) as price,
    CONCAT('$', FORMAT(p.cost_price, 2)) as cost,
    p.stock_quantity,
    p.reorder_level,
    t.tax_name,
    t.tax_rate,
    p.is_active
FROM products p
LEFT JOIN product_categories pc ON p.category_id = pc.category_id
LEFT JOIN brands b ON p.brand_id = b.brand_id
LEFT JOIN units_of_measure uom ON p.uom_id = uom.uom_id
LEFT JOIN tax_rates t ON p.tax_id = t.tax_id;

-- Low Stock Products
CREATE OR REPLACE VIEW low_stock_products AS
SELECT 
    product_code,
    product_name,
    category_name,
    stock_quantity,
    reorder_level,
    (reorder_level - stock_quantity) as shortage_quantity
FROM product_catalog
WHERE stock_quantity <= reorder_level
AND is_active = TRUE
ORDER BY shortage_quantity DESC;

-- ============================================
-- FINANCIAL VIEWS
-- ============================================

-- Payment Summary by Method
CREATE OR REPLACE VIEW payment_summary_by_method AS
SELECT 
    pm.method_name as payment_method,
    COUNT(DISTINCT vp.payment_id) as vendor_payment_count,
    COALESCE(SUM(vp.amount), 0) as vendor_payments_total,
    COUNT(DISTINCT cp.payment_id) as customer_payment_count,
    COALESCE(SUM(cp.amount), 0) as customer_payments_total,
    (COALESCE(SUM(cp.amount), 0) - COALESCE(SUM(vp.amount), 0)) as net_cash_flow
FROM payment_methods pm
LEFT JOIN vendor_payments vp ON pm.payment_method_id = vp.payment_method_id
LEFT JOIN customer_payments cp ON pm.payment_method_id = cp.payment_method_id
WHERE pm.is_active = TRUE
GROUP BY pm.payment_method_id, pm.method_name
ORDER BY net_cash_flow DESC;

-- Revenue vs Expenses
CREATE OR REPLACE VIEW revenue_vs_expenses AS
SELECT 
    DATE_FORMAT(COALESCE(vp.payment_date, cp.payment_date), '%Y-%m') as year_month,
    COALESCE(SUM(vp.amount), 0) as total_expenses,
    COALESCE(SUM(cp.amount), 0) as total_revenue,
    (COALESCE(SUM(cp.amount), 0) - COALESCE(SUM(vp.amount), 0)) as net_profit,
    CASE 
        WHEN COALESCE(SUM(vp.amount), 0) > 0 THEN 
            ROUND((COALESCE(SUM(cp.amount), 0) - COALESCE(SUM(vp.amount), 0)) / COALESCE(SUM(vp.amount), 0) * 100, 2)
        ELSE 0 
    END as profit_margin_percent
FROM vendor_payments vp
FULL OUTER JOIN customer_payments cp ON DATE_FORMAT(vp.payment_date, '%Y-%m') = DATE_FORMAT(cp.payment_date, '%Y-%m')
GROUP BY year_month
ORDER BY year_month DESC;

-- ============================================
-- ORDER VIEWS
-- ============================================

-- Purchase Order Summary
CREATE OR REPLACE VIEW purchase_order_summary AS
SELECT 
    po.po_number,
    v.vendor_name,
    c.country_name as vendor_country,
    po.order_date,
    os.status_name as status,
    pt.term_name as payment_terms,
    pm.method_name as payment_method,
    CONCAT('$', FORMAT(po.total_amount, 2)) as total_amount,
    po.created_at
FROM purchase_orders po
JOIN vendors v ON po.vendor_id = v.vendor_id
JOIN countries c ON v.country_id = c.country_id
JOIN order_statuses os ON po.status_id = os.status_id
LEFT JOIN payment_terms pt ON po.payment_term_id = pt.term_id
LEFT JOIN payment_methods pm ON po.payment_method_id = pm.payment_method_id
ORDER BY po.order_date DESC;

-- Sales Order Summary
CREATE OR REPLACE VIEW sales_order_summary AS
SELECT 
    so.so_number,
    cust.customer_name,
    c.country_name as customer_country,
    ct.type_name as customer_type,
    so.order_date,
    os.status_name as status,
    so.payment_status,
    CONCAT('$', FORMAT(so.total_amount, 2)) as total_amount,
    so.created_at
FROM sales_orders so
JOIN customers cust ON so.customer_id = cust.customer_id
JOIN countries c ON cust.country_id = c.country_id
LEFT JOIN customer_types ct ON cust.customer_type_id = ct.customer_type_id
JOIN order_statuses os ON so.status_id = os.status_id
ORDER BY so.order_date DESC;

SELECT '✅ All views created successfully!' as Status;
SHOW FULL TABLES WHERE Table_type = 'VIEW';

