-- ============================================================
-- FoodBridge - Food Distribution Management System
-- Database Schema (MySQL) - Fully Normalized 3NF
-- ============================================================

DROP DATABASE IF EXISTS foodbridge;
CREATE DATABASE foodbridge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE foodbridge;

-- ============================================================
-- TABLE 1: Zone
-- ============================================================
CREATE TABLE Zone (
    zone_id     INT AUTO_INCREMENT PRIMARY KEY,
    zone_name   VARCHAR(100) NOT NULL,
    city        VARCHAR(100) NOT NULL,
    pincode     VARCHAR(10)  NOT NULL,
    CONSTRAINT uq_zone UNIQUE (zone_name, city, pincode)
) ENGINE=InnoDB;

-- ============================================================
-- TABLE 2: Donor
-- ============================================================
CREATE TABLE Donor (
    donor_id    INT AUTO_INCREMENT PRIMARY KEY,
    donor_name  VARCHAR(150) NOT NULL,
    phone       VARCHAR(15)  NOT NULL,
    email       VARCHAR(150) NOT NULL,
    address     TEXT         NOT NULL,
    zone_id     INT          NOT NULL,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_donor_zone FOREIGN KEY (zone_id)
        REFERENCES Zone(zone_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_donor_phone CHECK (LENGTH(phone) >= 10),
    INDEX idx_donor_zone (zone_id)
) ENGINE=InnoDB;

-- ============================================================
-- TABLE 3: Receiver
-- ============================================================
CREATE TABLE Receiver (
    receiver_id       INT AUTO_INCREMENT PRIMARY KEY,
    receiver_name     VARCHAR(150) NOT NULL,
    organization_name VARCHAR(200) NOT NULL,
    phone             VARCHAR(15)  NOT NULL,
    address           TEXT         NOT NULL,
    zone_id           INT          NOT NULL,
    created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_receiver_zone FOREIGN KEY (zone_id)
        REFERENCES Zone(zone_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_receiver_phone CHECK (LENGTH(phone) >= 10),
    INDEX idx_receiver_zone (zone_id)
) ENGINE=InnoDB;

-- ============================================================
-- TABLE 4: FoodItem
-- ============================================================
CREATE TABLE FoodItem (
    food_id       INT AUTO_INCREMENT PRIMARY KEY,
    donor_id      INT          NOT NULL,
    food_name     VARCHAR(150) NOT NULL,
    category      VARCHAR(80)  NOT NULL,
    quantity      DECIMAL(10,2) NOT NULL,
    unit          VARCHAR(30)  NOT NULL,
    is_perishable BOOLEAN      NOT NULL DEFAULT TRUE,
    cooked_time   DATETIME     NOT NULL,
    expiry_date   DATETIME     NOT NULL,
    status        ENUM('available','requested','assigned','fulfilled','expired')
                  NOT NULL DEFAULT 'available',
    zone_id       INT          NOT NULL,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_food_donor FOREIGN KEY (donor_id)
        REFERENCES Donor(donor_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_food_zone FOREIGN KEY (zone_id)
        REFERENCES Zone(zone_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_quantity CHECK (quantity > 0),
    CONSTRAINT chk_expiry CHECK (expiry_date > cooked_time),
    INDEX idx_food_zone (zone_id),
    INDEX idx_food_expiry (expiry_date),
    INDEX idx_food_status (status)
) ENGINE=InnoDB;

-- ============================================================
-- TABLE 5: Request
-- ============================================================
CREATE TABLE Request (
    request_id         INT AUTO_INCREMENT PRIMARY KEY,
    receiver_id        INT NOT NULL,
    food_id            INT NOT NULL,
    requested_quantity DECIMAL(10,2) NOT NULL,
    request_status     ENUM('pending','approved','fulfilled','cancelled','expired')
                       NOT NULL DEFAULT 'pending',
    request_time       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fulfilled_time     DATETIME NULL,
    CONSTRAINT fk_request_receiver FOREIGN KEY (receiver_id)
        REFERENCES Receiver(receiver_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_request_food FOREIGN KEY (food_id)
        REFERENCES FoodItem(food_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_req_quantity CHECK (requested_quantity > 0),
    INDEX idx_request_receiver (receiver_id),
    INDEX idx_request_food (food_id)
) ENGINE=InnoDB;

-- ============================================================
-- TABLE 6: AuditLog
-- ============================================================
CREATE TABLE AuditLog (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    table_name  VARCHAR(80)  NOT NULL,
    action_type VARCHAR(30)  NOT NULL,
    record_id   INT          NOT NULL,
    old_value   TEXT         NULL,
    new_value   TEXT         NULL,
    changed_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- VIEW 1: Available_Donations
-- ============================================================
CREATE OR REPLACE VIEW Available_Donations AS
SELECT
    f.food_id,
    f.food_name,
    f.category,
    f.quantity,
    f.unit,
    f.is_perishable,
    f.cooked_time,
    f.expiry_date,
    f.status,
    f.zone_id,
    z.zone_name,
    z.city,
    d.donor_id,
    d.donor_name,
    d.phone AS donor_phone
FROM FoodItem f
JOIN Zone  z ON f.zone_id  = z.zone_id
JOIN Donor d ON f.donor_id = d.donor_id
WHERE f.status = 'available'
  AND f.expiry_date > NOW();

-- ============================================================
-- VIEW 2: Pending_Requests
-- ============================================================
CREATE OR REPLACE VIEW Pending_Requests AS
SELECT
    r.request_id,
    r.requested_quantity,
    r.request_status,
    r.request_time,
    f.food_id,
    f.food_name,
    f.category,
    f.quantity  AS available_quantity,
    f.unit,
    f.expiry_date,
    rec.receiver_id,
    rec.receiver_name,
    rec.organization_name,
    rec.phone AS receiver_phone,
    z.zone_name,
    z.city
FROM Request  r
JOIN FoodItem f   ON r.food_id     = f.food_id
JOIN Receiver rec ON r.receiver_id = rec.receiver_id
JOIN Zone     z   ON f.zone_id     = z.zone_id
WHERE r.request_status = 'pending';

-- ============================================================
-- FUNCTION: GetUrgencyLevel
-- ============================================================
DELIMITER $$
CREATE FUNCTION GetUrgencyLevel(p_expiry DATETIME)
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE diff_minutes INT;
    SET diff_minutes = TIMESTAMPDIFF(MINUTE, NOW(), p_expiry);

    IF diff_minutes <= 0 THEN
        RETURN 'Expired';
    ELSEIF diff_minutes <= 60 THEN
        RETURN 'Critical';
    ELSEIF diff_minutes <= 180 THEN
        RETURN 'Soon';
    ELSE
        RETURN 'Fresh';
    END IF;
END$$
DELIMITER ;

-- ============================================================
-- STORED PROCEDURE 1: MatchDonation
-- ============================================================
DELIMITER $$
CREATE PROCEDURE MatchDonation(IN p_zone_id INT)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_food_id INT;
    DECLARE v_quantity DECIMAL(10,2);
    DECLARE v_receiver_id INT;

    DECLARE food_cursor CURSOR FOR
        SELECT food_id, quantity
        FROM FoodItem
        WHERE zone_id = p_zone_id
          AND status = 'available'
          AND expiry_date > NOW();

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN food_cursor;

    read_loop: LOOP
        FETCH food_cursor INTO v_food_id, v_quantity;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SELECT receiver_id INTO v_receiver_id
        FROM Receiver
        WHERE zone_id = p_zone_id
        LIMIT 1;

        IF v_receiver_id IS NOT NULL THEN
            INSERT INTO Request (receiver_id, food_id, requested_quantity, request_status, request_time)
            VALUES (v_receiver_id, v_food_id, v_quantity, 'pending', NOW());

            UPDATE FoodItem SET status = 'requested' WHERE food_id = v_food_id;
        END IF;
    END LOOP;

    CLOSE food_cursor;
END$$
DELIMITER ;

-- ============================================================
-- STORED PROCEDURE 2: UpdateDistributionStatus
-- ============================================================
DELIMITER $$
CREATE PROCEDURE UpdateDistributionStatus(
    IN p_request_id INT,
    IN p_status VARCHAR(20)
)
BEGIN
    DECLARE v_food_id INT;

    SELECT food_id INTO v_food_id
    FROM Request
    WHERE request_id = p_request_id;

    UPDATE Request
    SET request_status = p_status,
        fulfilled_time = IF(p_status = 'fulfilled', NOW(), fulfilled_time)
    WHERE request_id = p_request_id;

    IF p_status = 'fulfilled' THEN
        UPDATE FoodItem SET status = 'fulfilled' WHERE food_id = v_food_id;
    ELSEIF p_status = 'cancelled' THEN
        UPDATE FoodItem SET status = 'available' WHERE food_id = v_food_id;
    ELSEIF p_status = 'approved' THEN
        UPDATE FoodItem SET status = 'assigned' WHERE food_id = v_food_id;
    END IF;
END$$
DELIMITER ;

-- ============================================================
-- TRIGGER 1: Auto-expire food (BEFORE UPDATE on FoodItem)
-- ============================================================
DELIMITER $$
CREATE TRIGGER trg_auto_expire_food
BEFORE UPDATE ON FoodItem
FOR EACH ROW
BEGIN
    IF NEW.expiry_date < NOW() AND NEW.status NOT IN ('fulfilled', 'expired') THEN
        SET NEW.status = 'expired';
    END IF;
END$$
DELIMITER ;

-- ============================================================
-- TRIGGER 2: Log request status changes into AuditLog
-- ============================================================
DELIMITER $$
CREATE TRIGGER trg_request_audit
AFTER UPDATE ON Request
FOR EACH ROW
BEGIN
    IF OLD.request_status <> NEW.request_status THEN
        INSERT INTO AuditLog (table_name, action_type, record_id, old_value, new_value, changed_at)
        VALUES ('Request', 'STATUS_UPDATE', NEW.request_id,
                OLD.request_status, NEW.request_status, NOW());
    END IF;
END$$
DELIMITER ;

-- ============================================================
-- TRIGGER 3: Log food status changes into AuditLog
-- ============================================================
DELIMITER $$
CREATE TRIGGER trg_food_audit
AFTER UPDATE ON FoodItem
FOR EACH ROW
BEGIN
    IF OLD.status <> NEW.status THEN
        INSERT INTO AuditLog (table_name, action_type, record_id, old_value, new_value, changed_at)
        VALUES ('FoodItem', 'STATUS_UPDATE', NEW.food_id,
                OLD.status, NEW.status, NOW());
    END IF;
END$$
DELIMITER ;

-- ============================================================
-- EVENT: Auto-expire food items periodically
-- ============================================================
SET GLOBAL event_scheduler = ON;

DELIMITER $$
CREATE EVENT IF NOT EXISTS evt_expire_food
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
    UPDATE FoodItem
    SET status = 'expired'
    WHERE expiry_date < NOW()
      AND status IN ('available', 'requested');
END$$
DELIMITER ;
