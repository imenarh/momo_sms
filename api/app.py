from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import json
import os
from urllib.parse import urlparse

HOST = "localhost"
PORT = 8000
USERNAME = os.getenv("API_USERNAME", "admin")
PASSWORD = os.getenv("API_PASSWORD", "password123")
DATA_FILE = "data/processed/transactions.json"


def load_transactions():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump([], file)
    with open(DATA_FILE, encoding="utf-8") as file:
        return json.load(file)


def save_transactions():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(transactions, file, indent=2)


transactions = load_transactions()

class APIHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200, headers=None):
        headers = headers or {}
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def is_authenticated(self):
        header = self.headers.get("Authorization", "")
        try:
            scheme, encoded = header.split(" ", 1)
            credentials = base64.b64decode(encoded).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return False
        return scheme.lower() == "basic" and credentials == f"{USERNAME}:{PASSWORD}"

    def require_authentication(self):
        if self.is_authenticated():
            return True
        self.send_json(
            {"error": "Authentication required"},
            401,
            {"WWW-Authenticate": 'Basic realm="Transactions API"'},
        )
        return False

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            raise ValueError("Request body is required")
        value = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def transaction_id(self):
        path = urlparse(self.path).path.rstrip("/")
        parts = path.split("/")
        if len(parts) != 3 or parts[1] != "transactions":
            return None
        try:
            return int(parts[2])
        except ValueError:
            return None

    def do_GET(self):
        if not self.require_authentication():
            return
        path = urlparse(self.path).path.rstrip("/")
        if path == "/transactions":
            self.send_json(transactions)
            return
        transaction_id = self.transaction_id()
        transaction = next((item for item in transactions if item["id"] == transaction_id), None)
        if transaction is None:
            self.send_json({"error": "Transaction not found"}, 404)
        else:
            self.send_json(transaction)

    def do_POST(self):
        if not self.require_authentication():
            return
        if urlparse(self.path).path.rstrip("/") != "/transactions":
            self.send_json({"error": "Route not found"}, 404)
            return
        try:
            transaction = self.read_json()
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "Invalid JSON body"}, 400)
            return
        new_id = max((item["id"] for item in transactions), default=0) + 1
        transaction["id"] = new_id
        transactions.append(transaction)
        save_transactions()
        self.send_json(transaction, 201)

    def do_PUT(self):
        if not self.require_authentication():
            return
        transaction_id = self.transaction_id()
        transaction = next((item for item in transactions if item["id"] == transaction_id), None)
        if transaction is None:
            self.send_json({"error": "Transaction not found"}, 404)
            return
        try:
            updated = self.read_json()
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "Invalid JSON body"}, 400)
            return
        updated["id"] = transaction_id
        transactions[transactions.index(transaction)] = updated
        save_transactions()
        self.send_json(updated)

    def do_DELETE(self):
        if not self.require_authentication():
            return
        transaction_id = self.transaction_id()
        transaction = next((item for item in transactions if item["id"] == transaction_id), None)
        if transaction is None:
            self.send_json({"error": "Transaction not found"}, 404)
            return
        transactions.remove(transaction)
        save_transactions()
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()


if __name__ == "__main__":
    print(f"API running at http://{HOST}:{PORT}")
    print(f"Transactions file: {DATA_FILE}")
    ThreadingHTTPServer((HOST, PORT), APIHandler).serve_forever()
