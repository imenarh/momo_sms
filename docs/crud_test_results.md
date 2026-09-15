# CRUD Testing — Member 3 Deliverable
## MoMo SMS Data (momo_sms) — Database: momo_sms_db

Tested against MariaDB 10.11, schema loaded from database/database_setup.sql. Two bugs
were found during testing (missing comma before the CHECK constraints, and category_id
being NOT NULL while its FK said ON DELETE SET NULL) and have since been fixed in the file.

## Test data
6 users, 6 categories, 8 transactions (built from real SMS bodies in data/raw/momo.xml),
16 participant rows, 4 system logs.

## SELECT / INSERT / UPDATE / DELETE results
See docs/crud_results_part1.png, docs/crud_results_part2.png, and docs/crud_output.txt for terminal output of:
- Q1: all transactions joined with category name
- Q2: total amount moved per category (aggregate)
- Q3: all parties in a transaction (junction table join)
- Q4: every transaction sent by a given user
- Q5: INSERT a new transaction + its participants
- Q6/Q7: UPDATE transaction status and user phone number
- Q9: DELETE a transaction, confirmed CASCADE removed its participant rows (2 -> 0)

## Referential integrity tests
All four deliberately triggered and confirmed to fail correctly:

| Action attempted | Result |
|---|---|
| Delete a category still referenced by transactions | ERROR 1451 - blocked by ON DELETE RESTRICT |
| Insert a transaction with a non-existent category_id | ERROR 1452 - blocked by foreign key |
| Insert a transaction with a negative amount | ERROR 3819 - blocked by CHECK constraint |
| Insert a duplicate (user_id, transaction_id, role) | ERROR 1062 - blocked by UNIQUE constraint |

**Conclusion:** all foreign keys, the UNIQUE constraint, and the CHECK constraints
are enforced correctly. CASCADE and RESTRICT delete rules both behave as designed.
