# DSA & Data Parsing — Member 2

## 1. XML Parsing

`dsa/parse_transactions.py` parses `data/raw/modified_sms_v2.xml` (1,691 SMS records) into a list of JSON objects, written to `data/processed/transactions.json`.

SMS bodies come in several distinct formats, so each is matched with its own regex:

| Category | Count |
|---|---|
| PAYMENT | 658 |
| TRANSFER | 585 |
| BANK_DEPOSIT | 248 |
| DEPOSIT | 63 |
| AIRTIME_UTILITY | 53 |
| AIRTIME_BUNDLE | 36 |
| BUNDLE_PURCHASE | 21 |
| OTHER (unmatched) | 15 |
| OTP_NOTIFICATION | 8 |
| WITHDRAWAL | 3 |
| REVERSAL | 1 |

15 of 1,691 records (<1%) don't match a known pattern and are kept as raw text under `OTHER` — a normal outcome for real-world SMS data.

## 2. DSA Comparison — Linear Search vs Dictionary Lookup

`dsa/search_comparison.py` compares two ways to find a transaction by `id`:

- **Linear search** — scans the list from the start until the id matches. O(n).
- **Dictionary lookup** — builds a `{id: transaction}` dict once, then looks up by key. O(1) average case.

**Results (100 random lookups across 1,691 records):**

| Method | Avg time/lookup | Total time |
|---|---|---|
| Linear search | 77.061 µs | 7.706 ms |
| Dictionary lookup | 0.950 µs | 0.095 ms |

Dictionary lookup was **~81x faster** on average.

**Worst case** (looking up the last record, id=1691):
- Linear search: 170.215 µs
- Dictionary lookup: 1.015 µs (**~168x faster**)

## 3. Reflection

**Why dictionary lookup wins:** Linear search checks records one at a time, so its cost grows with dataset size — worst case it scans every record. A dictionary is a hash table: inserting `{id: transaction}` stores each record at a position determined by hashing its key, so lookup jumps straight there without scanning. That's why it's O(1) regardless of size.

**Tradeoff:** building the dictionary costs O(n) up front (every record inserted once), but that cost is paid once while every lookup after is O(1). Linear search has no setup cost but pays O(n) on *every* lookup. For an API doing many repeated lookups, dictionary lookup wins decisively.

**Other structures worth considering:**
- A second dictionary indexed by sender/receiver phone number, for lookups by something other than id
- A sorted list + binary search (O(log n)) for range queries (e.g. transactions between two dates), which a plain dictionary can't do
- A real database index (e.g. `idx_transactions_category` already in our schema) once data lives in MySQL instead of a flat JSON file
