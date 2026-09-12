"""
Seed script for the Shopkeeper Bot + Admin Panel demo.

Wipes and recreates the SQLite database at DATABASE_PATH (from .env),
then fills it with a realistic "everyday-carry accessories" shop:
products (with generated placeholder photos), customers, addresses,
orders in every status, wallet transactions, and withdrawal requests.

Run this once before taking portfolio screenshots or handing the
project to someone to click through.

    python seed_demo_data.py

Demo admin login created by this script:
    username: admin
    password: admin123
"""

import os
import sqlite3
from datetime import datetime, timedelta

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH", "./shopkeeper.db")
IMAGES_PATH = os.getenv("IMAGES_PATH", "./photo")

SQL_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS Products (
            Product_id  INTEGER PRIMARY KEY,
            Products_image TEXT,
            Products_name TEXT NOT NULL,
            Quantity INTEGER DEFAULT 0 CHECK(Quantity >= 0),
            Price Decimal NOT NULL,
            Is_active Decimal NOT NULL DEFAULT 1 CHECK(Is_active IN (0,1)),
            Information TEXT NOT NULL
        );""",
    """CREATE TABLE IF NOT EXISTS Users (
            User_id  INTEGER PRIMARY KEY,
            Telegram_id INTEGER UNIQUE NOT NULL,
            User_name TEXT,
            User_adress TEXT,
            Walet INTEGER DEFAULT 0
        );""",
    """CREATE TABLE IF NOT EXISTS Admin (
            Admin_id  INTEGER PRIMARY KEY,
            Admin_name TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL
        );""",
    """CREATE TABLE IF NOT EXISTS Orders (
            Order_id  INTEGER PRIMARY KEY,
            User_id  INTEGER NOT NULL,
            Adress_id  INTEGER,
            Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Sum Decimal DEFAULT 0 CHECK (Sum >= 0),
            Price Decimal DEFAULT 0 CHECK (Price >= 0),
            Order_Status TEXT NOT NULL CHECK(Order_Status IN
                ('Selecting', 'Awaiting payment', 'Paid', 'Processing', 'Sent', 'Cancelled')),
            FOREIGN KEY (User_id) REFERENCES Users (User_id),
            FOREIGN KEY (Adress_id) REFERENCES Adress(Adress_id)
        );""",
    """CREATE TABLE IF NOT EXISTS Order_Items (
            Order_Items_id  INTEGER PRIMARY KEY,
            Order_id  INTEGER NOT NULL,
            Product_id  INTEGER NOT NULL,
            Price Decimal NOT NULL,
            Quantity INTEGER DEFAULT 0,
            FOREIGN KEY (Order_id) REFERENCES Orders (Order_id),
            FOREIGN KEY (Product_id) REFERENCES Products (Product_id)
        );""",
    """CREATE TABLE IF NOT EXISTS Wallet_Transactions (
            Wallet_Transactions_id  INTEGER PRIMARY KEY,
            User_id  INTEGER NOT NULL,
            Type TEXT NOT NULL CHECK(Type IN ('Top_up', 'Refund', 'Purchase', 'Withdrawal')),
            Amount Decimal NOT NULL CHECK (Amount > 0),
            Direction TEXT NOT NULL CHECK(Direction IN ('In', 'Out')),
            Order_id  INTEGER,
            Description TEXT,
            Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Order_id) REFERENCES Orders (Order_id),
            FOREIGN KEY (User_id) REFERENCES Users (User_id)
        );""",
    """CREATE TABLE IF NOT EXISTS Withdrawal_Requests (
            Withdrawal_Requests_id  INTEGER PRIMARY KEY,
            User_id  INTEGER NOT NULL,
            Amount Decimal NOT NULL,
            Sheba_number TEXT NOT NULL,
            Withdrawal_Requests_Status TEXT NOT NULL CHECK(Withdrawal_Requests_Status IN
                ('Pending', 'Approved', 'Rejected')),
            Requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Reviewed_at TIMESTAMP,
            Admin_note TEXT,
            FOREIGN KEY (User_id) REFERENCES Users (User_id)
        );""",
    """CREATE TABLE IF NOT EXISTS Adress (
            Adress_id  INTEGER PRIMARY KEY,
            User_id  INTEGER NOT NULL,
            User_adress TEXT NOT NULL,
            Adress_name TEXT DEFAULT 'Untitled',
            Postal_code INTEGER NOT NULL,
            FOREIGN KEY (User_id) REFERENCES Users (User_id)
        );""",
]

PRODUCTS = [
    {"name": "Aviator Sunglasses", "price": 825000, "qty": 12, "color": "#D9A441",
     "info": "Polarized UV400 lenses with a metal frame."},
    {"name": "Classic Wristwatch", "price": 1250000, "qty": 3, "color": "#3C4A5C",
     "info": "Stainless steel case, leather strap, quartz movement."},
    {"name": "Leather Wallet", "price": 450000, "qty": 20, "color": "#6B4226",
     "info": "Full-grain leather bifold wallet with 6 card slots."},
    {"name": "Canvas Tote Bag", "price": 320000, "qty": 0, "color": "#7C9070",
     "info": "Heavy canvas tote, reinforced handles, inner pocket."},
    {"name": "Wireless Earbuds", "price": 1890000, "qty": 8, "color": "#2E2E38",
     "info": "Bluetooth 5.3, active noise cancellation, 24h battery."},
    {"name": "Wool Beanie", "price": 210000, "qty": 15, "color": "#9B2C2C",
     "info": "Ribbed knit beanie, one size, machine washable."},
    {"name": "Minimalist Backpack", "price": 1450000, "qty": 5, "color": "#38546B",
     "info": "Water-resistant 18L backpack with padded laptop sleeve."},
    {"name": "Leather Belt", "price": 380000, "qty": 10, "color": "#4A3728",
     "info": "Full-grain leather belt with a brushed steel buckle."},
]

CUSTOMERS = [
    {"telegram_id": 100001, "name": "Sara Ahmadi", "address": "Tehran, Valiasr St, No. 12", "postal": 1234567890},
    {"telegram_id": 100002, "name": "Reza Karimi", "address": "Isfahan, Chaharbagh Ave, No. 8", "postal": 8134567891},
    {"telegram_id": 100003, "name": "Niloofar Hosseini", "address": "Shiraz, Zand St, No. 45", "postal": 7134567892},
    {"telegram_id": 100004, "name": "Amir Rostami", "address": "Mashhad, Vakilabad Blvd, No. 3", "postal": 9134567893},
    {"telegram_id": 100005, "name": "Elham Moradi", "address": "Tabriz, Abresan St, No. 21", "postal": 5134567894},
    {"telegram_id": 100006, "name": "Kian Sadeghi", "address": "Karaj, Golshahr Blvd, No. 60", "postal": 3134567895},
]


def make_placeholder_image(path, text, color_hex):
    """Simple solid-color placeholder photo with the product name on it.
    Falls back to a built-in font if no truetype font is found, so this
    works the same on any machine."""
    img = Image.new("RGB", (640, 640), color_hex)
    draw = ImageDraw.Draw(img)

    font = None
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ):
        if os.path.exists(candidate):
            font = ImageFont.truetype(candidate, 42)
            break
    if font is None:
        font = ImageFont.load_default()

    lines = text.split(" ")
    wrapped = "\n".join(
        " ".join(lines[i:i + 2]) for i in range(0, len(lines), 2)
    )
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, align="center")
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.multiline_text(
        ((640 - w) / 2, (640 - h) / 2), wrapped, font=font,
        fill="white", align="center",
    )
    img.save(path, "JPEG", quality=85)


def seed():
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    os.makedirs(IMAGES_PATH, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    for statement in SQL_STATEMENTS:
        cursor.execute(statement)

    # --- Admin ---
    cursor.execute(
        "INSERT INTO Admin (Admin_name, Password) VALUES (?, ?)",
        ("admin", generate_password_hash("admin123")),
    )

    # --- Products (with generated photos) ---
    product_ids = []
    for p in PRODUCTS:
        filename = p["name"].lower().replace(" ", "_") + ".jpg"
        make_placeholder_image(os.path.join(IMAGES_PATH, filename), p["name"], p["color"])
        cursor.execute(
            "INSERT INTO Products (Products_image, Products_name, Quantity, Price, Information) "
            "VALUES (?, ?, ?, ?, ?)",
            (filename, p["name"], p["qty"], p["price"], p["info"]),
        )
        product_ids.append(cursor.lastrowid)

    # --- Customers + one address each ---
    user_ids = []
    address_ids = []
    for c in CUSTOMERS:
        cursor.execute(
            "INSERT INTO Users (Telegram_id, User_name) VALUES (?, ?)",
            (c["telegram_id"], c["name"]),
        )
        user_id = cursor.lastrowid
        user_ids.append(user_id)
        cursor.execute(
            "INSERT INTO Adress (User_id, User_adress, Adress_name, Postal_code) VALUES (?, ?, ?, ?)",
            (user_id, c["address"], "Home", c["postal"]),
        )
        address_ids.append(cursor.lastrowid)

    wallet_balance = {uid: 0 for uid in user_ids}

    def add_wallet_tx(user_id, tx_type, amount, direction, description, order_id=None):
        cursor.execute(
            "INSERT INTO Wallet_Transactions (User_id, Type, Amount, Direction, Order_id, Description) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, tx_type, amount, direction, order_id, description),
        )
        if direction == "In":
            wallet_balance[user_id] += amount
        else:
            wallet_balance[user_id] -= amount

    def make_order(user_id, address_id, status, days_ago, items, paid_from_wallet=False):
        date_str = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        total_qty = sum(q for _, q in items)
        total_price = sum(PRODUCTS[pid_index]["price"] * q for pid_index, q in items)
        cursor.execute(
            "INSERT INTO Orders (User_id, Adress_id, Date, Sum, Price, Order_Status) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, address_id, date_str, total_qty, total_price, status),
        )
        order_id = cursor.lastrowid
        for pid_index, qty in items:
            product_id = product_ids[pid_index]
            cursor.execute(
                "INSERT INTO Order_Items (Order_id, Product_id, Price, Quantity) VALUES (?, ?, ?, ?)",
                (order_id, product_id, PRODUCTS[pid_index]["price"] * qty, qty),
            )
        if paid_from_wallet and status in ("Paid", "Processing", "Sent"):
            add_wallet_tx(user_id, "Purchase", total_price, "Out", "Order payment", order_id)
        return order_id

    # top up a couple of wallets before any wallet-paid orders
    add_wallet_tx(user_ids[0], "Top_up", 2000000, "In", "Wallet top-up")
    add_wallet_tx(user_ids[2], "Top_up", 1000000, "In", "Wallet top-up")

    # a spread of orders across every status and both recent (<=10 days)
    # and older (>10 days) dates, so the date-range search has something to find
    make_order(user_ids[0], address_ids[0], "Paid", 2, [(0, 1), (2, 1)], paid_from_wallet=True)
    make_order(user_ids[1], address_ids[1], "Processing", 4, [(1, 1)])
    make_order(user_ids[2], address_ids[2], "Sent", 6, [(4, 1), (5, 2)])
    make_order(user_ids[3], address_ids[3], "Sent", 8, [(6, 1)])
    make_order(user_ids[4], address_ids[4], "Awaiting payment", 1, [(7, 1)])
    make_order(user_ids[5], address_ids[5], "Processing", 3, [(0, 2)])
    old_order_id = make_order(user_ids[1], address_ids[1], "Paid", 15, [(1, 1), (7, 1)])
    cancelled_id = make_order(user_ids[3], address_ids[3], "Cancelled", 5, [(3, 1)])
    add_wallet_tx(user_ids[3], "Refund", PRODUCTS[3]["price"], "In", "Refund for cancelled order", cancelled_id)

    # --- Withdrawal requests ---
    add_wallet_tx(user_ids[0], "Top_up", 500000, "In", "Wallet top-up")
    cursor.execute(
        "INSERT INTO Withdrawal_Requests (User_id, Amount, Sheba_number, Withdrawal_Requests_Status) "
        "VALUES (?, ?, ?, ?)",
        (user_ids[0], 300000, "IR820540102680020817909002", "Pending"),
    )
    cursor.execute(
        "INSERT INTO Withdrawal_Requests (User_id, Amount, Sheba_number, Withdrawal_Requests_Status) "
        "VALUES (?, ?, ?, ?)",
        (user_ids[2], 400000, "IR120170000000123456789012", "Pending"),
    )
    cursor.execute(
        "INSERT INTO Withdrawal_Requests (User_id, Amount, Sheba_number, Withdrawal_Requests_Status, Reviewed_at) "
        "VALUES (?, ?, ?, ?, datetime('now', '-2 days'))",
        (user_ids[2], 200000, "IR330560611828001234567891", "Approved"),
    )
    add_wallet_tx(user_ids[2], "Withdrawal", 200000, "Out", "Withdrawal approved")
    cursor.execute(
        "INSERT INTO Withdrawal_Requests (User_id, Amount, Sheba_number, Withdrawal_Requests_Status, Reviewed_at) "
        "VALUES (?, ?, ?, ?, datetime('now', '-1 days'))",
        (user_ids[4], 5000000, "IR650170000000987654321098", "Rejected"),
    )

    # write the running wallet balances computed above
    for uid, balance in wallet_balance.items():
        cursor.execute("UPDATE Users SET Walet = ? WHERE User_id = ?", (balance, uid))

    conn.commit()
    conn.close()

    print(f"Seeded database at {DATABASE_PATH}")
    print(f"Product photos written to {IMAGES_PATH}")
    print("Demo admin login -> username: admin | password: admin123")


if __name__ == "__main__":
    seed()
