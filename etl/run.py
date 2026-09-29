import json
import logging
import os

from config import RAW_XML_PATH, PROCESSED_JSON_PATH, LOG_PATH
from parse_xml import parse_sms_xml
from clean_normalize import clean_records
from categorize import categorize_records


def setup_logging():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def main():
    setup_logging()
    logging.info("ETL pipeline started")

    logging.info(f"Parsing XML from {RAW_XML_PATH}")
    raw_records = parse_sms_xml(RAW_XML_PATH)
    logging.info(f"Parsed {len(raw_records)} raw records")

    cleaned = clean_records(raw_records)
    logging.info("Cleaned and normalized records")

    categorized = categorize_records(cleaned)
    logging.info("Categorized records")

    os.makedirs(os.path.dirname(PROCESSED_JSON_PATH), exist_ok=True)
    with open(PROCESSED_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(categorized, f, indent=2, ensure_ascii=False)

    logging.info(f"Wrote {len(categorized)} records to {PROCESSED_JSON_PATH}")
    print(f"ETL complete: {len(categorized)} transactions written to {PROCESSED_JSON_PATH}")


    try:
        from load_db import load_data_to_db
        load_data_to_db()
        logging.info("Loaded records into MySQL database")
    except Exception as e:
        logging.warning(f"Skipped DB load: {e}")
        print(f"Note: DB load skipped ({e}). The JSON file was still generated successfully.")


if __name__ == "__main__":
    main()
