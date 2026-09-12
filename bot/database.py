import sqlite3
from dotenv import load_dotenv
import os

sql_statements = [
    """CREATE TABLE IF NOT EXISTS Products (
            Product_id  INTEGER PRIMARY KEY,
            Products_image TEXT,
            Products_name TEXT NOT NULL, 
            Quantity INTEGER DEFAULT 0 CHECK(Quantity >= 0) , 
            Price Decimal NOT NULL,
            Is_active Decimal  NOT NULL DEFAULT 1 CHECK( Is_active IN (0,1))  , 
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
            User_id  INTEGER  NOT NULL,
            Adress_id  INTEGER,
            Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            Sum Decimal DEFAULT 0   CHECK (Sum >= 0),  
            Price Decimal DEFAULT 0 CHECK (Price >= 0),
            Order_Status TEXT NOT NULL CHECK(Order_Status IN ('Selecting', 'Awaiting payment', 'Paid','Processing','Sent','Cancelled')),
            FOREIGN KEY (User_id) REFERENCES Users (User_id),
            FOREIGN KEY (Adress_id) REFERENCES Adress(Adress_id)
        );""",
    """CREATE TABLE IF NOT EXISTS Order_Items (
            Order_Items_id  INTEGER PRIMARY KEY, 
            Order_id  INTEGER NOT NULL ,
            Product_id  INTEGER NOT NULL ,
            Price Decimal NOT NULL,
            Quantity INTEGER DEFAULT 0 , 
            FOREIGN KEY (Order_id) REFERENCES Orders (Order_id),
            FOREIGN KEY (Product_id) REFERENCES Products (Product_id)
        );""",
    """CREATE TABLE IF NOT EXISTS Wallet_Transactions (
            Wallet_Transactions_id  INTEGER PRIMARY KEY,
            User_id  INTEGER  NOT NULL,
            Type TEXT  NOT NULL CHECK(Type IN ('Top_up' , 'Refund' , 'Purchase' , 'Withdrawal' )),
            Amount Decimal NOT NULL CHECK ( Amount> 0),
            Direction TEXT NOT NULL CHECK(Direction IN ('In' , 'Out')),
            Order_id  INTEGER ,
            Description TEXT ,
            Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Order_id) REFERENCES Orders (Order_id),
            FOREIGN KEY (User_id) REFERENCES Users (User_id)


        );""",
    """CREATE TABLE IF NOT EXISTS Withdrawal_Requests (
            Withdrawal_Requests_id  INTEGER PRIMARY KEY,
            User_id  INTEGER  NOT NULL,
            Amount Decimal NOT NULL,
            Sheba_number TEXT NOT NULL,
            Withdrawal_Requests_Status TEXT NOT NULL CHECK(Withdrawal_Requests_Status IN ('Pending','Approved','Rejected')),
            Requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Reviewed_at TIMESTAMP,
            Admin_note TEXT ,
            FOREIGN KEY (User_id) REFERENCES Users (User_id)
        );""",
    """CREATE TABLE IF NOT EXISTS Adress (
        Adress_id  INTEGER PRIMARY KEY,
        User_id  INTEGER NOT NULL ,
        User_adress TEXT NOT NULL,
        Adress_name TEXT DEFAULT 'Untitled',
        Postal_code INTEGER NOT NULL,
        FOREIGN KEY (User_id) REFERENCES Users (User_id)
        );""",
]


def find_or_insert_users(cursor, value):
    cursor.execute("SELECT Telegram_id FROM Users  WHERE Telegram_id = ?", (value,))
    row = cursor.fetchone()
    if row == None:
        cursor.execute("INSERT INTO Users (Telegram_id) VALUES(?)", (value,))
        return True
    return False


def update_user_name(cursor, user_id, user_name):
    cursor.execute(
        "UPDATE Users SET User_name = ? WHERE User_id = ?",
        (user_name, user_id),
    )


def find_user_id(cursor, Telegram_id):
    cursor.execute("SELECT User_id FROM Users  WHERE Telegram_id = ?", (Telegram_id,))
    row = cursor.fetchone()
    return row


def get_all_products(cursor):
    cursor.execute("SELECT * FROM Products WHERE  Is_active = 1")
    rows = cursor.fetchall()
    return rows


def Product_Equilibrium_Analysis(cursor, Product_id, quantity=0):
    cursor.execute(
        "SELECT Quantity , Price FROM Products  WHERE Product_id = ?", (Product_id,)
    )
    row = cursor.fetchone()
    if row[0] >= quantity:
        cursor.execute(
            "UPDATE Products SET Quantity = Quantity - ? WHERE Product_id = ?",
            (
                quantity,
                Product_id,
            ),
        )
    return row


def add_to_cart(cursor, product_id, quantity, user_id, price):
    cursor.execute(
        "SELECT  Order_id  FROM Orders  WHERE User_id = ? AND Order_Status = ?",
        (user_id, "Selecting"),
    )
    order_row = cursor.fetchone()
    if order_row == None:
        cursor.execute(
            "INSERT INTO Orders (User_id ,  Order_Status ) VALUES(?,?)",
            (user_id, "Selecting"),
        )
        order_id = cursor.lastrowid
    else:
        order_id = order_row[0]
    cursor.execute(
        "UPDATE Orders SET Sum = Sum + ? WHERE Order_id  = ?",
        (
            quantity,
            order_id,
        ),
    )
    cursor.execute(
        "UPDATE Orders SET Price = Price +(? * ?) WHERE Order_id  = ?",
        (
            quantity,
            price,
            order_id,
        ),
    )
    order_item_price = quantity * price
    cursor.execute(
        "INSERT INTO Order_Items (Order_id,Product_id,Quantity,Price) VALUES (?,?,?,?)",
        (order_id, product_id, quantity, order_item_price),
    )


def View_Shopping_Cart(cursor, user_id):
    cursor.execute(
        "SELECT User_id   FROM Orders  WHERE User_id = ? And Order_Status IN (?,?) ",
        (user_id, "Selecting", "Awaiting payment"),
    )
    order_row = cursor.fetchone()
    if order_row == None:
        return 0
    else:
        cursor.execute(
            "SELECT Products.Products_name ,Order_Items.Quantity , Order_Items.price , Orders.Order_Status , Orders.price , Orders.Sum , Orders.Order_id FROM Products , Orders, Order_Items  WHERE Orders.Order_id =Order_Items.Order_id And Order_Items.product_id = Products.Product_id And Orders.User_id = ? And Order_Status IN (?,?)",
            (
                user_id,
                "Selecting",
                "Awaiting payment",
            ),
        )
        rows = cursor.fetchall()
        return rows


def show_order_id(cursor, user_id):
    cursor.execute(
        "SELECT Order_id   FROM Orders  WHERE User_id = ? And Order_Status = ? ",
        (
            user_id,
            "Selecting",
        ),
    )
    row = cursor.fetchone()
    return row


def show_order_id_awaiting(cursor, user_id):
    cursor.execute(
        "SELECT Order_id   FROM Orders  WHERE User_id = ? And Order_Status = ? ",
        (
            user_id,
            "Awaiting payment",
        ),
    )
    row = cursor.fetchone()
    return row


def show_adress(cursor, user_id):
    cursor.execute(
        "SELECT  Adress.Adress_name , Adress.User_adress  ,Orders.Order_Status  FROM Adress , Orders WHERE Adress.User_id = ? And Orders.Order_Status = ? ",
        (
            user_id,
            "Awaiting payment",
        ),
    )
    row = cursor.fetchone()
    return row


def get_user_addresses(cursor, user_id):
    cursor.execute(
        "SELECT Adress_name , User_adress , Postal_code FROM Adress  WHERE User_id = ?",
        (user_id,),
    )
    rows = cursor.fetchall()
    return rows


def add_address(cursor, user_id, address_name, user_adress, postal_code):
    cursor.execute(
        "INSERT INTO Adress ( User_id , User_adress , Adress_name , Postal_code ) VALUES (?,?,?,?)",
        (user_id, user_adress, address_name, postal_code),
    )
    return cursor.lastrowid


def finalize_order(cursor, order_id, adress_id):
    cursor.execute(
        "UPDATE Orders SET Adress_id = ? , Order_Status = ?  WHERE Order_id  = ?",
        (
            adress_id,
            "Awaiting payment",
            order_id,
        ),
    )


def Payment_Gateway(cursor, order_id):
    cursor.execute(
        "UPDATE Orders SET  Order_Status = ?  WHERE Order_id  = ?",
        (
            "Paid",
            order_id,
        ),
    )


def Purchase_Status(cursor, user_id):

    cursor.execute(
        "SELECT User_id   FROM Orders  WHERE User_id = ? And Order_Status IN (?,?,?) ",
        (user_id, "Paid", "Processing", "Sent"),
    )
    order_row = cursor.fetchone()
    if order_row == None:
        return 0
    else:
        cursor.execute(
            "SELECT Products.Products_name ,Order_Items.Quantity , Order_Items.price , Orders.Order_Status , Orders.price , Orders.Sum , Orders.Order_id FROM Products , Orders, Order_Items  WHERE Orders.Order_id =Order_Items.Order_id And Order_Items.product_id = Products.Product_id And Orders.User_id = ? And Order_Status IN (?,?,?)",
            (user_id, "Paid", "Processing", "Sent"),
        )
        rows = cursor.fetchall()
        return rows


def cancel_order(cursor, user_id, order_id):
    cursor.execute(
        "UPDATE Orders SET  Order_Status = ?  WHERE Order_id  = ?",
        (
            "Cancelled",
            order_id,
        ),
    )
    cursor.execute(
        "SELECT Price , Quantity , Product_id  FROM Order_Items  WHERE Order_id = ?",
        (order_id,),
    )
    rows = cursor.fetchall()
    for row in rows:
        sum_price = 0
        sum_price = row[0] * row[1]
        product_id = row[2]
        quantity = row[1]
        record_wallet_transaction(
            cursor, user_id, "Refund", sum_price, "In", "Cancel Order", order_id
        )
        cursor.execute(
            "UPDATE Products SET  Quantity = Quantity +?  WHERE Product_id  = ?",
            (
                quantity,
                product_id,
            ),
        )


def record_wallet_transaction(
    cursor, user_id, type, amount, direction, description, order_id=None
):
    if direction == "Out":
        cursor.execute(
            "SELECT  Walet FROM Users  WHERE User_id = ? ",
            (user_id,),
        )
        row = cursor.fetchone()
        if row[0] >= amount:
            if type == "Purchase":
                cursor.execute(
                    "INSERT INTO Wallet_Transactions ( User_id , Type , Amount , Direction , Order_id , Description ) VALUES(?,?,?,?,?,?)",
                    (user_id, type, amount, direction, order_id, description),
                )
                cursor.execute(
                    "UPDATE Users SET Walet = Walet - ?  WHERE  User_id = ?",
                    (
                        amount,
                        user_id,
                    ),
                )
        else:
            return 0

    else:
        cursor.execute(
            "INSERT INTO Wallet_Transactions ( User_id , Type , Amount , Direction , Order_id , Description ) VALUES(?,?,?,?,?,?)",
            (user_id, type, amount, direction, order_id, description),
        )
        cursor.execute(
            "UPDATE Users SET Walet = Walet + ?  WHERE  User_id = ?",
            (
                amount,
                user_id,
            ),
        )


def Checking_wallet_balance(cursor, user_id):
    cursor.execute(
        "SELECT Walet  FROM Users  WHERE User_id = ?  ",
        (user_id,),
    )
    row = cursor.fetchone()
    return row


def Checking_price_order(cursor, order_id):
    cursor.execute(
        "SELECT Price  FROM Orders  WHERE Order_id = ?  ",
        (order_id,),
    )
    row = cursor.fetchone()
    return row


def Withdrawal_of_funds(cursor, user_id, sheba_number, amount):
    cursor.execute(
        "INSERT INTO Withdrawal_Requests ( User_id , Amount , Sheba_number , Withdrawal_Requests_Status ) VALUES(?,?,?,?)",
        (user_id, amount, sheba_number, "Pending"),
    )

load_dotenv()
database_file = os.getenv("DATABASE_PATH")

try:

    with sqlite3.connect(database_file) as conn:

        print(
            f"Opened SQLite database with version {sqlite3.sqlite_version} successfully."
        )

        cursor = conn.cursor()

        for statement in sql_statements:
            cursor.execute(statement)

        conn.commit()

except sqlite3.OperationalError as e:
    print("Failed to open database:", e)