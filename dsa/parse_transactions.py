"""
dsa/parse_transactions.py

Member 2 deliverable — Data Parsing.

Parses the raw MoMo SMS XML export (modified_sms_v2.xml) and converts each
SMS record into a structured JSON object (a Python dict), then writes the
full list out to data/processed/transactions.json.

The MoMo SMS bodies are not one consistent format -- different transaction
types (deposit, payment, bank deposit, transfer, airtime, utility payment,
withdrawal) each have their own wording. This module recognises each of
those patterns with a dedicated regex and falls back to an "OTHER" category
(with the raw body kept) for anything that doesn't match a known pattern
(e.g. promotional / notification SMS that aren't real transactions).

Run directly to parse data/raw/modified_sms_v2.xml and write the output file:

    python3 dsa/parse_transactions.py
"""

import json
import os
import re
import xml.etree.ElementTree as ET

RAW_XML_PATH = "data/raw/modified_sms_v2.xml"
OUTPUT_JSON_PATH = "data/processed/transactions.json"


def _to_float(amount_str):
    """Convert a comma-formatted amount string like '1,000' to a float."""
    return float(amount_str.replace(",", ""))


# Each entry: (category_name, compiled regex, extractor function)
# Extractor functions pull (amount, fee, sender, receiver, transaction_id, timestamp)
# out of a regex match. Any field that doesn't apply to that message type is None.

PATTERNS = []


def _register(category, pattern):
    def decorator(extractor):
        PATTERNS.append((category, re.compile(pattern), extractor))
        return extractor
    return decorator


@_register(
    "DEPOSIT",
    r"You have received (?P<amount>[\d,]+) RWF from (?P<sender>[A-Za-z .]+?) "
    r"\(.*?\).*?at (?P<timestamp>[\d-]+ [\d:]+)\..*?"
    r"Financial Transaction Id: (?P<txid>\d+)\.",
)
def _extract_deposit(m):
    return {
        "amount": _to_float(m.group("amount")),
        "fee": 0.0,
        "sender": m.group("sender").strip(),
        "receiver": None,
        "transaction_id": m.group("txid"),
        "timestamp": m.group("timestamp"),
    }


@_register(
    "PAYMENT",
    r"TxId: (?P<txid>\d+)\. Your payment of (?P<amount>[\d,]+) RWF to "
    r"(?P<receiver>[A-Za-z0-9 .]+?) has been completed at (?P<timestamp>[\d-]+ [\d:]+)\. "
    r"Your new balance: [\d,]+ RWF\. Fee was (?P<fee>[\d,]+) RWF\.",
)
def _extract_payment(m):
    return {
        "amount": _to_float(m.group("amount")),
        "fee": _to_float(m.group("fee")),
        "sender": None,
        "receiver": m.group("receiver").strip(),
        "transaction_id": m.group("txid"),
        "timestamp": m.group("timestamp"),
    }


@_register(
    "BANK_DEPOSIT",
    r"\*113\*R\*A bank deposit of (?P<amount>[\d,]+) RWF has been added to your "
    r"mobile money account at (?P<timestamp>[\d-]+ [\d:]+)\.",
)
def _extract_bank_deposit(m):
    return {
        "amount": _to_float(m.group("amount")),
        "fee": 0.0,
        "sender": None,
        "receiver": None,
        "transaction_id": None,
        "timestamp": m.group("timestamp"),
    }


@_register(
    "TRANSFER",
    r"\*165\*S\*(?P<amount>[\d,]+) RWF transferred to (?P<receiver>[A-Za-z .]+?) "
    r"\((?P<receiver_phone>\d+)\) from \d+ at (?P<timestamp>[\d-]+ [\d:]+)\s*\.? "
    r"Fee was:? (?P<fee>[\d,]+) RWF\.",
)
def _extract_transfer(m):
    return {
        "amount": _to_float(m.group("amount")),
        "fee": _to_float(m.group("fee")),
        "sender": None,
        "receiver": m.group("receiver").strip(),
        "transaction_id": None,
        "timestamp": m.group("timestamp"),
    }


@_register(
    "AIRTIME_UTILITY",
    r"\*162\*TxId:(?P<txid>\d+)\*S\*Your payment of (?P<amount>[\d,]+) RWF to "
    r"(?P<receiver>[A-Za-z ]+?) with token\s*(?P<token>[\d-]*)\s*has been completed at "
    r"(?P<timestamp>[\d-]+ [\d:]+)\. Fee was (?P<fee>[\d,]+) RWF\.",
)
def _extract_airtime_utility(m):
    return {
        "amount": _to_float(m.group("amount")),
        "fee": _to_float(m.group("fee")),
        "sender": None,
        "receiver": m.group("receiver").strip(),
        "transaction_id": m.group("txid"),
        "timestamp": m.group("timestamp"),
    }


@_register(
    "AIRTIME_BUNDLE",
    r"\*164\*S\*Y'ello,A transaction of (?P<amount>[\d,]+) RWF by "
    r"(?P<receiver>[A-Za-z .]+?)\s+on your MOMO account was successfully completed at "
    r"(?P<timestamp>[\d-]+ [\d:]+)",
)
def _extract_airtime_bundle(m):
    return {
        "amount": _to_float(m.group("amount")),
        "fee": None,
        "sender": None,
        "receiver": m.group("receiver").strip(),
        "transaction_id": None,
        "timestamp": m.group("timestamp"),
    }


@_register(
    "WITHDRAWAL",
    r"You (?P<sender>[A-Za-z .]+?) \(.*?\) have via agent: (?P<receiver>[A-Za-z .]+?) "
    r"\(\d+\), withdrawn (?P<amount>[\d,]+) RWF from your mobile money account: \d+ at "
    r"(?P<timestamp>[\d-]+ [\d:]+)",
)
def _extract_withdrawal(m):
    return {
        "amount": _to_float(m.group("amount")),
        "fee": None,
        "sender": m.group("sender").strip(),
        "receiver": m.group("receiver").strip(),
        "transaction_id": None,
        "timestamp": m.group("timestamp"),
    }


@_register(
    "BUNDLE_PURCHASE",
    r"Yello!Umaze kugura .*?igura (?P<amount>[\d,]+) RWF",
)
def _extract_bundle_purchase(m):
    return {
        "amount": _to_float(m.group("amount")),
        "fee": None,
        "sender": None,
        "receiver": None,
        "transaction_id": None,
        "timestamp": None,
    }


@_register(
    "REVERSAL",
    r"A reversal has been initiated for your transaction to (?P<receiver>[A-Za-z .]+?) "
    r"\(\d+\) with (?P<amount>[\d,]+) RWF",
)
def _extract_reversal(m):
    return {
        "amount": _to_float(m.group("amount")),
        "fee": None,
        "sender": None,
        "receiver": m.group("receiver").strip(),
        "transaction_id": None,
        "timestamp": None,
    }


@_register(
    "OTP_NOTIFICATION",
    r"Dear Customer, your MTN MoMo application one-time password is :(?P<otp>\d+)",
)
def _extract_otp(m):
    # Not a financial transaction -- no amount/sender/receiver involved.
    return {
        "amount": None,
        "fee": None,
        "sender": None,
        "receiver": None,
        "transaction_id": None,
        "timestamp": None,
    }


def parse_sms_body(body):
    """Try each known pattern in turn; return (category, fields) or ('OTHER', {})."""
    for category, pattern, extractor in PATTERNS:
        match = pattern.search(body)
        if match:
            return category, extractor(match)
    return "OTHER", {}


def parse_xml_to_transactions(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    transactions = []
    next_id = 1
    for sms in root.findall("sms"):
        body = sms.get("body", "")
        category, fields = parse_sms_body(body)

        transaction = {
            "id": next_id,
            "type": category,
            "amount": fields.get("amount"),
            "fee": fields.get("fee"),
            "sender": fields.get("sender"),
            "receiver": fields.get("receiver"),
            "transaction_id": fields.get("transaction_id"),
            "timestamp": fields.get("timestamp") or sms.get("readable_date"),
            "raw_body": body,
        }
        transactions.append(transaction)
        next_id += 1

    return transactions


def main():
    if not os.path.exists(RAW_XML_PATH):
        raise FileNotFoundError(
            f"Could not find {RAW_XML_PATH}. Place modified_sms_v2.xml there first."
        )

    transactions = parse_xml_to_transactions(RAW_XML_PATH)

    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=2)

    # Quick category breakdown for sanity-checking the parse
    counts = {}
    for t in transactions:
        counts[t["type"]] = counts.get(t["type"], 0) + 1

    print(f"Parsed {len(transactions)} SMS records -> {OUTPUT_JSON_PATH}")
    print("Category breakdown:")
    for category, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {category:<20} {count}")


if __name__ == "__main__":
    main()
