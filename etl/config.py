import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_XML_PATH = os.path.join(BASE_DIR, "data", "raw", "momo.xml")
PROCESSED_JSON_PATH = os.path.join(BASE_DIR, "data", "processed", "transactions.json")
LOG_PATH = os.path.join(BASE_DIR, "data", "logs", "etl.log")
