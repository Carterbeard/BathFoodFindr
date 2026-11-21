import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

db_path = Path(__file__).parent / "instance" / "bathfoodfinder.sqlite"
db_path.parent.mkdir(exist_ok=True)

with sqlite3.connect(db_path) as db:
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            outlet TEXT NOT NULL,
            allergens TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY,
            food_item_id INTEGER NOT NULL REFERENCES food_items(id),
            price_pence INTEGER NOT NULL,
            portions INTEGER NOT NULL,
            collection_deadline TEXT NOT NULL
        );
    """)

    db.executemany("""
        INSERT OR IGNORE INTO food_items (id, name, outlet, allergens)
        VALUES (?, ?, ?, ?)
    """, [
        (1, "Regular chicken katsu curry with rice", "Fountain Canteen", "Wheat, milk"),
        (2, "Cheese sandwich", "Fountain Canteen", "Wheat, milk"),
        (3, "Cheese sandwich", "Pitstop", "Wheat, milk"),
        (4, "Vegetable pasta", "Lime Tree", "Wheat"),
        (5, "Chocolate pastry", "Pitstop", ""),
    ])

    deadline = datetime.now(timezone.utc) + timedelta(hours=1)
    db.execute("""
        INSERT OR IGNORE INTO listings
            (id, food_item_id, price_pence, portions, collection_deadline)
        VALUES (1, 1, 200, 3, ?)
    """, (deadline.isoformat(timespec="seconds"),))

print(f"Database ready at {db_path}")