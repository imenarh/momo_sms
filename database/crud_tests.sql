USE momo_sms_db;

SELECT '--- Q1: All transactions with category name ---' AS '';
SELECT t.id, t.reference_id, c.name AS category, t.amount, t.status, t.transaction_date
FROM transactions t
JOIN transaction_categories c ON t.category_id = c.id
ORDER BY t.transaction_date;

SELECT '--- Q2: Total amount moved per category ---' AS '';
SELECT c.name AS category, COUNT(*) AS txn_count, SUM(t.amount) AS total_amount
FROM transactions t
JOIN transaction_categories c ON t.category_id = c.id
GROUP BY c.name
ORDER BY total_amount DESC;

SELECT '--- Q3: All parties involved in transaction 6 (transfer) ---' AS '';
SELECT u.full_name, u.user_type, p.role
FROM transaction_participants p
JOIN users u ON p.user_id = u.id
WHERE p.transaction_id = 6;

SELECT '--- Q4: Every transaction James Kanneh sent ---' AS '';
SELECT t.id, t.reference_id, t.amount, t.transaction_date
FROM transactions t
JOIN transaction_participants p ON t.id = p.transaction_id
JOIN users u ON p.user_id = u.id
WHERE u.full_name = 'James Kanneh' AND p.role = 'SENDER';

SELECT '--- Q5: INSERT a new withdrawal transaction ---' AS '';
INSERT INTO transactions
    (reference_id, category_id, amount, balance_after, fee, status, transaction_date, raw_sms_text)
VALUES
    ('99999999999', 6, 5000.00, 20280.00, 100.00, 'COMPLETED', '2024-05-13 09:15:00',
     'You have withdrawn 5000 RWF from agent 36521838. Fee was 100 RWF. New balance: 20280 RWF.');

SET @new_txn_id = LAST_INSERT_ID();
INSERT INTO transaction_participants (user_id, transaction_id, role) VALUES
    (1, @new_txn_id, 'SENDER'), (5, @new_txn_id, 'AGENT');

SELECT * FROM transactions WHERE id = @new_txn_id;

SELECT '--- Q6: UPDATE a transaction status (e.g., flagged as REVERSED) ---' AS '';
UPDATE transactions SET status = 'REVERSED' WHERE id = @new_txn_id;
SELECT id, status FROM transactions WHERE id = @new_txn_id;

SELECT '--- Q7: UPDATE a user phone number ---' AS '';
UPDATE users SET phone_number = '250788110099' WHERE full_name = 'Jane Smith';
SELECT id, full_name, phone_number FROM users WHERE full_name = 'Jane Smith';

SELECT '--- Q9: DELETE a transaction (should CASCADE into transaction_participants) ---' AS '';
SELECT COUNT(*) AS participants_before FROM transaction_participants WHERE transaction_id = @new_txn_id;
DELETE FROM transactions WHERE id = @new_txn_id;
SELECT COUNT(*) AS participants_after FROM transaction_participants WHERE transaction_id = @new_txn_id;
