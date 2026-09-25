"""
dsa/search_comparison.py

Member 2 deliverable — DSA Integration.

Compares two ways of finding a transaction by id in the parsed dataset:

1. Linear search  -- scan the list from the start until the id matches.
   Worst case O(n): every lookup may have to check every record.

2. Dictionary lookup -- build a {id: transaction} dict once, then look up
   by key. Average case O(1): Python dicts are hash tables, so finding a
   key doesn't depend on how many records there are.

Run directly (after parse_transactions.py has produced
data/processed/transactions.json):

    python3 dsa/search_comparison.py
"""

import json
import random
import timeit

TRANSACTIONS_PATH = "data/processed/transactions.json"
NUM_LOOKUPS = 100  # number of ids to look up per method, for a stable average
NUM_TIMEIT_REPEATS = 5


def load_transactions():
    with open(TRANSACTIONS_PATH, encoding="utf-8") as f:
        return json.load(f)


def linear_search(transactions, target_id):
    """O(n) — scan every record until the id matches."""
    for transaction in transactions:
        if transaction["id"] == target_id:
            return transaction
    return None


def build_id_index(transactions):
    """Build the {id: transaction} dict used by dict_lookup. Done once."""
    return {t["id"]: t for t in transactions}


def dict_lookup(index, target_id):
    """O(1) average case — direct hash-table lookup."""
    return index.get(target_id)


def time_method(func, *args, number=NUM_TIMEIT_REPEATS):
    """Time a single call to func(*args), averaged over `number` repeats."""
    elapsed = timeit.timeit(lambda: func(*args), number=number)
    return elapsed / number


def run_comparison(transactions, sample_ids):
    index = build_id_index(transactions)

    linear_times = []
    dict_times = []

    for target_id in sample_ids:
        linear_times.append(time_method(linear_search, transactions, target_id))
        dict_times.append(time_method(dict_lookup, index, target_id))

    return linear_times, dict_times


def main():
    transactions = load_transactions()
    n = len(transactions)
    print(f"Loaded {n} transactions from {TRANSACTIONS_PATH}\n")

    # Sample NUM_LOOKUPS random ids spread across the whole dataset -- this
    # matters for linear search, since its cost depends on *where* in the
    # list the id happens to sit (early ids are fast, late ids are slow).
    all_ids = [t["id"] for t in transactions]
    sample_size = min(NUM_LOOKUPS, n)
    sample_ids = random.sample(all_ids, sample_size)

    linear_times, dict_times = run_comparison(transactions, sample_ids)

    avg_linear = sum(linear_times) / len(linear_times)
    avg_dict = sum(dict_times) / len(dict_times)

    print(f"Compared {sample_size} random lookups against {n} records:\n")
    print(f"{'Method':<20}{'Avg time per lookup':<25}{'Total time':<15}")
    print(f"{'Linear search':<20}{avg_linear*1e6:>10.3f} microseconds"
          f"{'':<5}{sum(linear_times)*1e3:>8.3f} ms")
    print(f"{'Dictionary lookup':<20}{avg_dict*1e6:>10.3f} microseconds"
          f"{'':<5}{sum(dict_times)*1e3:>8.3f} ms")
    print()

    if avg_dict > 0:
        speedup = avg_linear / avg_dict
        print(f"Dictionary lookup was ~{speedup:.1f}x faster on average.\n")

    # Also show the specific worst case: looking up the very last id,
    # which forces linear search to scan the entire list.
    last_id = transactions[-1]["id"]
    index = build_id_index(transactions)
    linear_last = time_method(linear_search, transactions, last_id, number=NUM_TIMEIT_REPEATS)
    dict_last = time_method(dict_lookup, index, last_id, number=NUM_TIMEIT_REPEATS)
    print(f"Worst case -- looking up the LAST record (id={last_id}):")
    print(f"  Linear search:     {linear_last*1e6:.3f} microseconds")
    print(f"  Dictionary lookup: {dict_last*1e6:.3f} microseconds")


if __name__ == "__main__":
    main()
