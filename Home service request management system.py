"""Home Service Request Management System (SQLite + Matplotlib).

Run: python home_service.py
Install chart dependency: python -m pip install matplotlib
The SQLite database is created as home_service.db beside this script.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

DB_PATH = Path(__file__).with_name("home_service.db")
STATUSES = ("Pending", "Assigned", "In Progress", "Completed", "Cancelled")


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        service_type TEXT NOT NULL,
        description TEXT NOT NULL,
        preferred_date TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TEXT NOT NULL
    )""")
    return conn


def add_request():
    print("\nNew service request")
    fields = {
        "customer": input("Customer name: ").strip(),
        "phone": input("Phone: ").strip(),
        "address": input("Service address: ").strip(),
        "service_type": input("Service type (e.g. plumbing): ").strip(),
        "description": input("Describe the issue: ").strip(),
        "preferred_date": input("Preferred date (YYYY-MM-DD, optional): ").strip() or None,
    }
    if not all(fields[k] for k in ("customer", "phone", "address", "service_type", "description")):
        print("Please fill in all required fields.")
        return
    with connect() as db:
        cur = db.execute("""INSERT INTO requests
            (customer, phone, address, service_type, description, preferred_date, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?)""",
            (*fields.values(), datetime.now().isoformat(timespec="seconds")))
    print(f"Request #{cur.lastrowid} added.")


def list_requests():
    with connect() as db:
        rows = db.execute("SELECT * FROM requests ORDER BY id DESC").fetchall()
    if not rows:
        print("No service requests yet.")
        return
    print("\nID | Customer | Service | Preferred date | Status | Phone")
    print("-" * 75)
    for r in rows:
        print(f"{r['id']} | {r['customer']} | {r['service_type']} | {r['preferred_date'] or '-'} | {r['status']} | {r['phone']}")


def update_status():
    list_requests()
    try:
        request_id = int(input("\nRequest ID to update: "))
    except ValueError:
        print("Enter a valid numeric ID.")
        return
    print("Statuses: " + ", ".join(STATUSES))
    status = input("New status: ").strip().title()
    if status not in STATUSES:
        print("That status is not valid.")
        return
    with connect() as db:
        cur = db.execute("UPDATE requests SET status = ? WHERE id = ?", (status, request_id))
    print("Status updated." if cur.rowcount else "Request ID not found.")


def delete_request():
    list_requests()
    try:
        request_id = int(input("\nRequest ID to delete: "))
    except ValueError:
        print("Enter a valid numeric ID.")
        return
    with connect() as db:
        cur = db.execute("DELETE FROM requests WHERE id = ?", (request_id,))
    print("Request deleted." if cur.rowcount else "Request ID not found.")


def show_chart():
    if plt is None:
        print("Matplotlib isn't installed. Run: python -m pip install matplotlib")
        return
    with connect() as db:
        rows = db.execute("SELECT status, COUNT(*) AS total FROM requests GROUP BY status").fetchall()
    counts = {r["status"]: r["total"] for r in rows}
    labels = [s for s in STATUSES if counts.get(s, 0)]
    values = [counts[s] for s in labels]
    if not values:
        print("Add some requests before creating a chart.")
        return
    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=["#f4b942", "#4c78a8", "#f58518", "#54a24b", "#e45756"][:len(labels)])
    plt.title("Home Service Requests by Status")
    plt.xlabel("Status")
    plt.ylabel("Number of requests")
    plt.bar_label(bars, padding=3)
    plt.tight_layout()
    chart_path = Path(__file__).with_name("request_status_chart.png")
    plt.savefig(chart_path, dpi=150)
    print(f"Chart saved to {chart_path}")
    plt.show()


def main():
    connect().close()
    actions = {"1": add_request, "2": list_requests, "3": update_status,
               "4": delete_request, "5": show_chart}
    while True:
        print("\n=== Home Service Request Management ===")
        print("1. Add request\n2. View requests\n3. Update request status")
        print("4. Delete request\n5. Show status chart\n0. Exit")
        choice = input("Choose: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Choose one of the listed options.")


if __name__ == "__main__":
    main()
