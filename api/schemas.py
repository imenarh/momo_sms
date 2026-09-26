"""
api/schemas.py
Member 3 Deliverable — Data Validation

Provides basic schema validation for incoming API requests to ensure 
payloads match the required relational structure before hitting the DB.
"""

def validate_transaction_payload(payload):
    """Validates the incoming JSON against required fields."""
    required_fields = ["amount", "type", "timestamp", "raw_body"]
    
    if not isinstance(payload, dict):
        return False, "Payload must be a JSON object."
        
    for field in required_fields:
        if field not in payload:
            return False, f"Missing required field: {field}"
            
    if not isinstance(payload.get("amount"), (int, float)):
        return False, "Field 'amount' must be a number."
        
    return True, "Valid payload"