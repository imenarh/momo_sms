USE momo_sms_db;

INSERT INTO transaction_categories (name, description) VALUES
('DEPOSIT',        'Money received into the mobile money account'),
('PAYMENT',        'Payment made to a person or merchant'),
('BANK_DEPOSIT',   'Cash deposit added via bank/agent'),
('TRANSFER',       'Peer-to-peer transfer of funds'),
('AIRTIME',        'Airtime or bundle purchase'),
('WITHDRAWAL',     'Cash withdrawal from an agent');

INSERT INTO users (full_name, phone_number, user_type) VALUES
('Jean Pierre Uwimana',   '250788123456', 'CUSTOMER'),
('Marie Claire Mukamana', '250788234567', 'CUSTOMER'),
('Eric Nkurunziza',       '250791345678', 'CUSTOMER'),
('Diane Umutoni',         '250790456789', 'CUSTOMER'),
('MoMo Agent Remera',     '250795963036', 'AGENT'),
('Simba Airtime Kigali',  '250700000001', 'MERCHANT');

INSERT INTO transactions
    (reference_id, category_id, amount, balance_after, fee, status, transaction_date, raw_sms_text)
VALUES
('76662021700', 1, 2000.00, 2000.00,   0.00, 'COMPLETED', '2024-05-10 16:30:51',
 'You have received 2000 RWF from Marie Claire Mukamana (*********567) on your mobile money account at 2024-05-10 16:30:51. Your new balance:2000 RWF. Financial Transaction Id: 76662021700.'),

('73214484437', 2, 1000.00, 1000.00,   0.00, 'COMPLETED', '2024-05-10 16:31:39',
 'TxId: 73214484437. Your payment of 1,000 RWF to Marie Claire Mukamana 12845 has been completed at 2024-05-10 16:31:39. Your new balance: 1,000 RWF. Fee was 0 RWF.'),

('51732411227', 2, 600.00,  400.00,    0.00, 'COMPLETED', '2024-05-10 21:32:32',
 'TxId: 51732411227. Your payment of 600 RWF to Eric Nkurunziza 95464 has been completed at 2024-05-10 21:32:32. Your new balance: 400 RWF. Fee was 0 RWF.'),

(NULL,          3, 40000.00, 40400.00, 0.00, 'COMPLETED', '2024-05-11 18:43:49',
 '*113*R*A bank deposit of 40000 RWF has been added to your mobile money account at 2024-05-11 18:43:49. Your NEW BALANCE :40400 RWF. Cash Deposit.'),

('17818959211', 2, 2000.00, 38400.00,  0.00, 'COMPLETED', '2024-05-11 18:48:42',
 'TxId: 17818959211. Your payment of 2,000 RWF to Eric Nkurunziza 14965 has been completed at 2024-05-11 18:48:42. Your new balance: 38,400 RWF. Fee was 0 RWF.'),

(NULL,          4, 10000.00, 28300.00, 100.00, 'COMPLETED', '2024-05-11 20:34:47',
 '*165*S*10000 RWF transferred to Eric Nkurunziza (250791345678) from 36521838 at 2024-05-11 20:34:47. Fee was: 100 RWF. New balance: 28300 RWF.'),

(NULL,          4, 1000.00, 27280.00,  20.00, 'COMPLETED', '2024-05-12 03:47:33',
 '*165*S*1000 RWF transferred to Diane Umutoni (250790456789) from 36521838 at 2024-05-12 03:47:33. Fee was: 20 RWF. New balance: 27280 RWF.'),

('13913173274', 5, 2000.00, 25280.00,  0.00, 'COMPLETED', '2024-05-12 11:41:28',
 '*162*TxId:13913173274*S*Your payment of 2000 RWF to Airtime with token has been completed at 2024-05-12 11:41:28. Fee was 0 RWF. Your new balance: 25280 RWF.');

INSERT INTO transaction_participants (user_id, transaction_id, role) VALUES
(2, 1, 'SENDER'), (1, 1, 'RECEIVER'),
(1, 2, 'SENDER'), (2, 2, 'RECEIVER'),
(1, 3, 'SENDER'), (3, 3, 'RECEIVER'),
(5, 4, 'AGENT'), (1, 4, 'ACCOUNT_OWNER'),
(1, 5, 'SENDER'), (3, 5, 'RECEIVER'),
(1, 6, 'SENDER'), (3, 6, 'RECEIVER'),
(1, 7, 'SENDER'), (4, 7, 'RECEIVER'),
(1, 8, 'SENDER'), (6, 8, 'RECEIVER');

INSERT INTO system_logs (transaction_id, level, message) VALUES
(1, 'INFO',  'Transaction 76662021700 parsed and categorized as DEPOSIT'),
(4, 'INFO',  'Bank deposit SMS matched (*113*R*) for Jean Pierre Uwimana wallet'),
(NULL, 'WARNING', 'SMS at 2024-05-11 20:34:47 missing explicit TxId, matched by regex fallback'),
(8, 'INFO',  'Transaction 13913173274 parsed and categorized as AIRTIME'),
(NULL, 'WARNING', 'Duplicate SMS reference_id detected during load_db insert, record skipped'),
(NULL, 'ERROR', 'Failed to categorize SMS body: no matching keyword pattern in categorize.py, defaulted to UNKNOWN'),
(2, 'INFO', 'clean_normalize.py stripped currency formatting from raw amount string before insert');
