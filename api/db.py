
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "", 
    "database": "momo_sms_db"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_all_transactions():
    """Returns a list of all transactions with nested categories and participants."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Base transaction fetch with joined category
    cursor.execute("""
        SELECT t.id, t.reference_id, t.amount, t.fee, t.status, 
               t.transaction_date, t.raw_sms_text, t.created_at,
               c.id as category_id, c.name as category_name, c.description as category_desc
        FROM transactions t
        LEFT JOIN transaction_categories c ON t.category_id = c.id
    """)
    
    results = cursor.fetchall()
    
    # Hydrate the participants and format structure
    formatted_transactions = []
    for row in results:
        tx_id = row['id']
        
        # Fetch Participants
        cursor.execute("""
            SELECT p.role, u.id, u.full_name, u.phone_number, u.user_type
            FROM transaction_participants p
            JOIN users u ON p.user_id = u.id
            WHERE p.transaction_id = %s
        """, (tx_id,))
        participants = cursor.fetchall()
        
        # Format matching the JSON schema documentation
        formatted_tx = {
            "id": tx_id,
            "reference_id": row["reference_id"],
            "amount": float(row["amount"]) if row["amount"] else 0.0,
            "fee": float(row["fee"]) if row["fee"] else 0.0,
            "status": row.get("status", "COMPLETED"),
            "transaction_date": str(row["transaction_date"]),
            "raw_sms_text": row["raw_sms_text"],
            "category": {
                "id": row["category_id"],
                "name": row["category_name"],
                "description": row["category_desc"]
            },
            "participants": [
                {
                    "role": p["role"],
                    "user": {
                        "id": p["id"],
                        "full_name": p["full_name"],
                        "phone_number": p["phone_number"],
                        "user_type": p["user_type"]
                    }
                } for p in participants
            ]
        }
        formatted_transactions.append(formatted_tx)

    cursor.close()
    conn.close()
    return formatted_transactions