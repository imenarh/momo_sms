import re
from datetime import datetime


def normalize_date(readable_date):

    if not readable_date:
        return None
    try:
        dt = datetime.strptime(readable_date, "%d %b %Y %I:%M:%S %p")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return readable_date


def clean_records(records):
    cleaned = []
    for r in records:
        body = re.sub(r"\s+", " ", r.get("body", "")).strip()
        cleaned.append({
            **r,
            "body": body,
            "timestamp": normalize_date(r.get("readable_date")),
        })
    return cleaned


if __name__ == "__main__":
    from config import RAW_XML_PATH
    from parse_xml import parse_sms_xml

    raw = parse_sms_xml(RAW_XML_PATH)
    cleaned = clean_records(raw)
    print(f"Cleaned {len(cleaned)} records")
    if cleaned:
        print("Sample record:", cleaned[0])
