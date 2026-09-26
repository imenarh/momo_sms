"""
etl/load_db.py
Member 3 Deliverable — Database Loading

Extracts parsed JSON transactions and loads them into the MySQL normalized schema:
transaction_categories, users, transactions, transaction_participants, and system_logs.
"""
import json
import os
import mysql.connector
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "user": "gavinganza",
    "password": "momo123", # Update with actual local dev password
    "database": "momo_sms_db"
}

JSON_PATH = "data/processed/transactions.json"

def get_or_create_category(cursor, category_name):
    cursor.execute("SELECT id FROM transaction_categories WHERE name = %s", (category_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    cursor.execute("INSERT INTO transaction_categories (name) VALUES (%s)", (category_name,))
    return cursor.lastrowid

def get_or_create_user(cursor, identifier, role):
    if not identifier:
        return None
    
    cursor.execute("SELECT id FROM users WHERE full_name = %s", (identifier,))
    result = cursor.fetchone()
    if result:
        return result[0]
        
    cursor.execute("INSERT INTO users (full_name, user_type) VALUES (%s, %s)", (identifier, role))
    return cursor.lastrowid

def load_data_to_db():
    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f"Missing input data: {JSON_PATH}")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        transactions = json.load(f)

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    for tx in transactions:
        # 1. Handle Categories
        category_id = get_or_create_category(cursor, tx.get("type", "OTHER"))

        # 2. Insert Transaction Base
        # Note: 'amount' and 'fee' need to handle None values gracefully
        amount = tx.get("amount") or 0.0
        fee = tx.get("fee") or 0.0
        
# Convert timestamp safely handling multiple possible formats
        raw_time = tx.get("timestamp")
        formatted_time = None
        if raw_time:
            parsed_date = None
            for fmt in ("%d %b %Y %I:%M:%S %p", "%Y-%m-%d %H:%M:%S"):
                try:
                    parsed_date = datetime.strptime(raw_time, fmt)
                    break
                except ValueError:
                    continue
            
            if parsed_date:
                formatted_time = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                formatted_time = raw_time # Fallback if format is unknown
        tx_query = """
            INSERT INTO transactions (reference_id, category_id, amount, fee, transaction_date, raw_sms_text)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(tx_query, (
            tx.get("transaction_id", f"UNKNOWN-{tx['id']}"), 
            category_id, amount, fee, 
            formatted_time, tx.get("raw_body")
        ))
        transaction_id = cursor.lastrowid

        # 3. Handle Participants (M:N relationship)
        sender = tx.get("sender")
        if sender:
            sender_id = get_or_create_user(cursor, sender, "CUSTOMER")
            cursor.execute("INSERT INTO transaction_participants (transaction_id, user_id, role) VALUES (%s, %s, %s)", 
                           (transaction_id, sender_id, "SENDER"))

        receiver = tx.get("receiver")
        if receiver:
            # Check if it's a merchant payment based on type
            role = "MERCHANT" if tx.get("type") == "PAYMENT" else "RECEIVER"
            receiver_id = get_or_create_user(cursor, receiver, role)
            cursor.execute("INSERT INTO transaction_participants (transaction_id, user_id, role) VALUES (%s, %s, %s)", 
                           (transaction_id, receiver_id, role))

        # 4. System Logs
        log_query = "INSERT INTO system_logs (transaction_id, level, message) VALUES (%s, %s, %s)"
        cursor.execute(log_query, (transaction_id, "INFO", "Successfully loaded into DB"))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Successfully loaded {len(transactions)} transactions into MySQL.")

if __name__ == "__main__":
    load_data_to_db()