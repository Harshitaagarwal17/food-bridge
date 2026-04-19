-- ============================================================
-- FoodBridge - Sample Seed Data
-- Run this AFTER schema.sql
-- ============================================================

USE foodbridge;
select * from FoodItem;
delete from FoodItem where food_id=15;-- ============================================================
-- ZONES (5 zones across different cities)
-- ============================================================
INSERT INTO Zone (zone_name, city, pincode) VALUES
('Anna Nagar',    'Chennai',   '600040'),
('Koramangala',   'Bangalore', '560034'),
('Bandra West',   'Mumbai',    '400050'),
('Connaught Place','Delhi',    '110001'),
('Jubilee Hills', 'Hyderabad', '500033');

-- ============================================================
-- DONORS (5 donors)
-- ============================================================
INSERT INTO Donor (donor_name, phone, email, address, zone_id) VALUES
('Rajesh Kumar',     '9876543210', 'rajesh.kumar@email.com',     '12, 3rd Street, Anna Nagar',           1),
('Priya Sharma',     '9845123456', 'priya.sharma@email.com',     '45, 1st Cross, Koramangala',           2),
('Amit Patel',       '9823456789', 'amit.patel@email.com',       '78, Hill Road, Bandra West',           3),
('Sneha Reddy',      '9912345678', 'sneha.reddy@email.com',      '23, Janpath, Connaught Place',         4),
('Vikram Singh',     '9934567890', 'vikram.singh@email.com',     '56, Road No. 10, Jubilee Hills',       5);

-- ============================================================
-- RECEIVERS (5 receivers)
-- ============================================================
INSERT INTO Receiver (receiver_name, organization_name, phone, address, zone_id) VALUES
('Meera Iyer',       'Hope Foundation',      '9871234567', '34, 6th Avenue, Anna Nagar',           1),
('Arjun Rao',        'Food For All NGO',     '9841567890', '67, 5th Block, Koramangala',           2),
('Fatima Khan',      'Mumbai Meals Trust',   '9821234567', '89, Linking Road, Bandra West',        3),
('Rahul Gupta',      'Delhi Food Bank',      '9911234567', '12, Barakhamba Road, CP',              4),
('Ananya Krishnan',  'Hyderabad Hunger Aid', '9931234567', '34, Film Nagar, Jubilee Hills',        5);

-- ============================================================
-- FOOD ITEMS (10 items with mixed statuses and expiry times)
-- ============================================================
INSERT INTO FoodItem (donor_id, food_name, category, quantity, unit, is_perishable, cooked_time, expiry_date, status, zone_id) VALUES
-- Fresh items (expiry > 3 hours from now)
(1, 'Vegetable Biryani',     'Main Course',  25, 'plates',  TRUE,  DATE_SUB(NOW(), INTERVAL 1 HOUR),  DATE_ADD(NOW(), INTERVAL 5 HOUR),   'available',  1),
(2, 'Paneer Butter Masala',  'Main Course',  15, 'kg',      TRUE,  DATE_SUB(NOW(), INTERVAL 2 HOUR),  DATE_ADD(NOW(), INTERVAL 4 HOUR),   'available',  2),
(3, 'Pav Bhaji',             'Street Food',  40, 'plates',  TRUE,  DATE_SUB(NOW(), INTERVAL 1 HOUR),  DATE_ADD(NOW(), INTERVAL 6 HOUR),   'available',  3),

-- Soon items (expiry 1-3 hours)
(4, 'Dal Makhani',           'Main Course',  10, 'kg',      TRUE,  DATE_SUB(NOW(), INTERVAL 3 HOUR),  DATE_ADD(NOW(), INTERVAL 2 HOUR),   'available',  4),
(5, 'Curd Rice',             'Rice',         20, 'plates',  TRUE,  DATE_SUB(NOW(), INTERVAL 2 HOUR),  DATE_ADD(NOW(), INTERVAL 1.5 HOUR), 'available',  5),

-- Requested items
(1, 'Chapati with Sabzi',    'Main Course',  30, 'plates',  TRUE,  DATE_SUB(NOW(), INTERVAL 2 HOUR),  DATE_ADD(NOW(), INTERVAL 4 HOUR),   'requested',  1),
(3, 'Sandwich Platter',      'Snacks',       50, 'pieces',  TRUE,  DATE_SUB(NOW(), INTERVAL 1 HOUR),  DATE_ADD(NOW(), INTERVAL 3 HOUR),   'requested',  3),

-- Fulfilled items
(2, 'Idli Sambar',           'Breakfast',    35, 'plates',  TRUE,  DATE_SUB(NOW(), INTERVAL 5 HOUR),  DATE_ADD(NOW(), INTERVAL 1 HOUR),   'fulfilled',  2),

-- Non-perishable items
(4, 'Packaged Biscuits',     'Packaged',    100, 'packets', FALSE, DATE_SUB(NOW(), INTERVAL 1 DAY),   DATE_ADD(NOW(), INTERVAL 30 DAY),   'available',  4),
(5, 'Rice Bags (25kg)',      'Grains',        5, 'bags',    FALSE, DATE_SUB(NOW(), INTERVAL 2 DAY),   DATE_ADD(NOW(), INTERVAL 90 DAY),   'available',  5);

-- ============================================================
-- REQUESTS (some pending, some fulfilled)
-- ============================================================
INSERT INTO Request (receiver_id, food_id, requested_quantity, request_status, request_time, fulfilled_time) VALUES
-- Pending requests
(1, 6, 30, 'pending',   DATE_SUB(NOW(), INTERVAL 30 MINUTE), NULL),
(3, 7, 50, 'pending',   DATE_SUB(NOW(), INTERVAL 20 MINUTE), NULL),
(4, 4, 10, 'pending',   DATE_SUB(NOW(), INTERVAL 10 MINUTE), NULL),

-- Fulfilled request
(2, 8, 35, 'fulfilled', DATE_SUB(NOW(), INTERVAL 3 HOUR),    DATE_SUB(NOW(), INTERVAL 2 HOUR)),

-- Approved request
(5, 5, 15, 'approved',  DATE_SUB(NOW(), INTERVAL 15 MINUTE), NULL);
