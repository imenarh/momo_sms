import re

AMOUNT_RE = re.compile(r"([\d,]+(?:\.\d+)?)\s*RWF")
FEE_RE = re.compile(r"Fee (?:was|of)[:]?\s*([\d,]+(?:\.\d+)?)\s*RWF", re.IGNORECASE)
TXID_RE = re.compile(r"(?:TxId:|Financial Transaction Id:)\s*(\d+)", re.IGNORECASE)

RECEIVED_SENDER_RE = re.compile(r"from\s+([A-Za-z ]+?)\s*\(")
TRANSFER_RECEIVER_RE = re.compile(r"transferred to\s+([A-Za-z ]+?)\s*\(")
PAYMENT_RECEIVER_RE = re.compile(r"to\s+([A-Za-z ]+?)\s+\d")


def _clean_number(value):
    return value.replace(",", "") if value else value


def extract_amount(body):
    match = AMOUNT_RE.search(body)
    return _clean_number(match.group(1)) if match else None


def extract_fee(body):
    match = FEE_RE.search(body)
    return _clean_number(match.group(1)) if match else "0"


def extract_txid(body):
    match = TXID_RE.search(body)
    return match.group(1) if match else None


def _extract_name(body, pattern):
    match = pattern.search(body)
    return match.group(1).strip() if match else None


def categorize_transaction(body):

    body_lower = body.lower()

    if "received" in body_lower and " from " in body_lower:
        sender = _extract_name(body, RECEIVED_SENDER_RE)
        return "RECEIVED", sender, None

    if "bank deposit" in body_lower:
        return "DEPOSIT", None, None

    if "transferred to" in body_lower:
        receiver = _extract_name(body, TRANSFER_RECEIVER_RE)
        return "TRANSFER", None, receiver

    if "payment of" in body_lower and "airtime" in body_lower:
        return "AIRTIME", None, "Airtime"

    if "payment of" in body_lower:
        receiver = _extract_name(body, PAYMENT_RECEIVER_RE)
        return "PAYMENT", None, receiver

    return "OTHER", None, None


def categorize_records(records):
    categorized = []
    for r in records:
        body = r.get("body", "")
        tx_type, sender, receiver = categorize_transaction(body)
        categorized.append({
            **r,
            "type": tx_type,
            "sender": sender,
            "receiver": receiver,
            "amount": extract_amount(body),
            "fee": extract_fee(body),
            "transaction_id": extract_txid(body),
        })
    return categorized


if __name__ == "__main__":
    from config import RAW_XML_PATH
    from parse_xml import parse_sms_xml
    from clean_normalize import clean_records

    raw = parse_sms_xml(RAW_XML_PATH)
    cleaned = clean_records(raw)
    categorized = categorize_records(cleaned)

    print(f"Categorized {len(categorized)} records")
    if categorized:
        print("Sample record:", categorized[0])

    # Quick breakdown of how many of each type were found
    from collections import Counter
    counts = Counter(r["type"] for r in categorized)
    print("Type breakdown:", dict(counts))
