#ShopkeeperBot

A Telegram store for a small business, complete with a Flask admin panel.

Customers can browse products, build carts, checkout, track orders, and manage a wallet entirely within Telegram.

The store owner manages products, orders, customers, and payments from a clean web dashboard.

Built as a portfolio project that designs a true two-way backend: relational database design, stateful conversation flows in a chatbot, session-based authentication in a web application, and maintaining consistent money-related data (orders, wallet balances, payments) on both sides.

## What it does

### Customer side (Telegram bot)
- Product catalog with photos, paginated browsing
- Multi-item shopping cart with quantity picker and inventory validation (cannot order more than available inventory)
- Address book and guided checkout flow
- Trial payment gateway (clearly labeled as alternative inventory) or pay from wallet balance
- In-app wallet: automatic charging, spending and refunds from canceled orders
- Withdrawal requests by IBAN (reviewed by admin before payment)
- Self-service order status tracking and order cancellation (inventory and wallet are automatically restored)

### Admin side (web panel)
- Secure login (Flask - login with hashed passwords)
- Dashboard: overview of revenue, number of orders, recent orders and pending withdrawals
- Order management: filter by status or scope History, transfer of orders through the order fulfillment pipeline
- Product management: add/edit/deactivate products and upload photos
- Customer list with details (orders, addresses, wallet history)
- Withdrawal request review: approve (with inventory check) or reject
- Global search across products, orders and customers
- Change wallet transaction ledger and admin password

## Technical stack

- **Python** — `python-telegram-bot` for the bot, Flask + Flask-Login for the admin panel
- **SQLite** — a common database (`shopkeeper.db`) used by both the bot and the admin panel
- HTML / CSS / simple forms for the admin panel (no JavaScript framework, full page refresh as designed)

## Project structure

shopkeeper_bot/
├── bot/ # Telegram bot
│ ├── main.py
│ └── database.py
├── admin_panel/ # Flask admin panel
│ ├── app.py
│ ├── database.py
│ ├── templates/
│ └── static/
├── photo/ # Product images
├── project_photo/ # Screenshots for documentation
├── seed_demo_data.py # Stores realistic demo data + product photos
├── requirements.txt
├── .env.example
└── shopkeeper.db

## Architecture notes

- Both the bot and the admin panel use a common SQLite database.

- Wallet balance is stored as a running total that stays in sync with the transaction ledger.

- Wallet balance and balance checks are done in a way that prevents overselling and overwithdrawing.

## Honest Scope and Limitations

This is a learning-focused portfolio project, so a few things are intentionally simplified:

- The payment gateway is displayed as a dummy (a simple success/failure selection screen) instead of a real payment provider.

- Withdrawals are handled manually: confirming the request updates the ledger, but no actual bank transfers are made.

- There is no automated test suite yet.

## Setup

```bash
git clone <your-repo-url>
cd shopkeeper_bot
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env # Then fill in the BOT_TOKEN and SECRET_KEY.
```

**Demo Seed Data** (recommended before first run):

```bash
python seed_demo_data.py
```

This will create a demo admin account:

**Username:** `admin`
**Password:** `admin123`
(Change it later from the admin panel settings page.)

**Run the bot:**

```bash
cd bot
python main.py
```

**Run the admin panel** (in a separate terminal):

```bash
cd admin_panel
python app.py
```

Then open `http://127.0.0.1:5000` and log in with the demo admin account.

## Screenshots

<!-- Replace the lines below with your actual screenshots from the project_photo folder -->

**Admin Dashboard**
![Admin Dashboard](project_photo/your-dashboard-screenshot.png)

**Product Management**
![Products](project_photo/your-products-screenshot.png)

**Order Management**
![Orders](project_photo/your-orders-screenshot.png)

**Telegram Bot – Product Catalog**
![Bot Catalog](project_photo/your-bot-catalog-screenshot.png)

**Telegram Bot – Shopping Cart and Payment**
![Bot Cart](project_photo/your-bot-cart-screenshot.png)

**Wallet and Withdrawals**
![Wallet](project_photo/your-wallet-screenshot.png)

## Status

Bot and admin panel include all the necessary features for all the described flows Above.

See the commit history for a step-by-step build process (from schema design to full payment, wallet, and management workflows).

## License

This project is for portfolio/educational purposes.

```
