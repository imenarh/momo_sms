CREATE DATABASE IF NOT EXISTS momo_sms_db;
USE momo_sms_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    phone_number VARCHAR(20) NULL,
    user_type ENUM('CUSTOMER', 'MERCHANT', 'AGENT', 'UNKNOWN') DEFAULT 'UNKNOWN',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transaction_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reference_id VARCHAR(100) NULL,
    category_id INT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NULL,
    fee DECIMAL(15,2) DEFAULT 0.00,
    status ENUM('COMPLETED', 'FAILED', 'PENDING', 'REVERSED', 'UNKNOWN')
        DEFAULT 'UNKNOWN',
    transaction_date DATETIME NOT NULL,
    raw_sms_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id)
        REFERENCES transaction_categories(id)
        ON DELETE SET NULL  

        CONSTRAINT chk_transactions_amount CHECK (amount > 0),
    CONSTRAINT chk_transactions_fee CHECK (fee >= 0) 
);
    CREATE INDEX idx_transactions_category ON transactions(category_id);

CREATE TABLE transaction_participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    transaction_id INT NOT NULL,
    role ENUM('SENDER', 'RECEIVER', 'ACCOUNT_OWNER', 'MERCHANT', 'AGENT', 'OTHER')
        NOT NULL,

     CONSTRAINT fk_participants_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_participants_transaction FOREIGN KEY (transaction_id)
        REFERENCES transactions(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_participant UNIQUE (user_id, transaction_id, role)
);

CREATE INDEX idx_participants_user ON transaction_participants(user_id);
CREATE INDEX idx_participants_transaction ON transaction_participants(transaction_id);

CREATE TABLE system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NULL,
    level ENUM('INFO', 'WARNING', 'ERROR') NOT NULL,
    message VARCHAR(800) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

CONSTRAINT fk_logs_transaction FOREIGN KEY (transaction_id)
        REFERENCES transactions(id)
        ON DELETE SET NULL
);
CREATE INDEX idx_logs_transaction ON system_logs(transaction_id);
