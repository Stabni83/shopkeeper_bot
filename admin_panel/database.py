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
            Is_active Decimal  NOT NULL DEFAULT 1 CHECK( Is_active IN (0,1)) , 
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


def Show_admin(cursor, admin_id):
    cursor.execute(
        "SELECT Admin_id , Admin_name FROM Admin  WHERE Admin_id= ?  ",
        (admin_id,),
    )
    row = cursor.fetchone()
    return row


def find_admin(cursor, admin_name):

    cursor.execute(
        "SELECT Password , Admin_id FROM Admin  WHERE Admin_name= ?  ",
        (admin_name,),
    )
    row = cursor.fetchone()

    return row


def stats_new_orders(cursor):
    cursor.execute(
        "SELECT Order_id  FROM Orders  WHERE   Order_Status = ?  ",
        ("Paid",),
    )
    rows = cursor.fetchall()
    count = 0
    for row in rows:
        count += 1
    return count


def stats_Processing_orders(cursor):
    cursor.execute(
        "SELECT Order_id  FROM Orders  WHERE   Order_Status = ?  ",
        ("Processing",),
    )
    rows = cursor.fetchall()
    count = 0
    for row in rows:
        count += 1
    return count


def stats_total_orders(cursor):
    cursor.execute(
        "SELECT Order_id  FROM Orders  WHERE   Order_Status IN (?,?,?)  ",
        ("Paid", "Processing", "Sent"),
    )
    rows = cursor.fetchall()
    count = 0
    for row in rows:
        count += 1
    return count


def stats_revenue(cursor):
    cursor.execute(
        "SELECT Price  FROM Orders  WHERE   Order_Status IN (?,?,?)  ",
        ("Paid", "Processing", "Sent"),
    )
    rows = cursor.fetchall()
    price = 0
    for row in rows:
        price += row[0]
    return price


def stats_customers(cursor):
    cursor.execute(
        "SELECT DISTINCT User_id  FROM Orders  WHERE   Order_Status IN (?,?,?)  ",
        ("Paid", "Processing", "Sent"),
    )
    rows = cursor.fetchall()
    count = 0
    user = []
    for row in rows:
        user.append(row[0])
        count += 1
    return count


def financial_pending(cursor):
    cursor.execute(
        "SELECT Price  FROM Orders  WHERE   Order_Status = ?  ",
        ("Awaiting payment",),
    )
    rows = cursor.fetchall()
    price = 0
    for row in rows:
        price += row[0]
    return price


def financial_pending_withdrawals(cursor):
    cursor.execute(
        "SELECT Amount  FROM Withdrawal_Requests  WHERE  Withdrawal_Requests_Status = ?  ",
        ("Pending",),
    )
    rows = cursor.fetchall()
    amount = 0
    for row in rows:
        amount += row[0]
    return amount


def pending_withdrawals(cursor):
    cursor.execute(
        "SELECT Amount  FROM Withdrawal_Requests  WHERE  Withdrawal_Requests_Status = ?  ",
        ("Pending",),
    )
    rows = cursor.fetchall()
    count = 0
    for row in rows:
        count += 1
    return count


def recent_orders(cursor):
    cursor.execute(
        "SELECT  Orders.Order_id , Orders.Date  , Users.User_name  , Orders.Price , Orders.Order_Status , Adress.User_adress ,Adress.Postal_code FROM Orders , Users ,Adress  WHERE Orders.User_id = Users.User_id AND  Adress.Adress_id = Orders.Adress_id AND Orders.Date >= datetime('now', '-10 days') AND Orders.Order_Status IN (?,?,?) ORDER BY Orders.Date DESC ",
        (
            "Paid",
            "Processing",
            "Sent",
        ),
    )
    rows = cursor.fetchall()
    order_list = []
    for row in rows:
        order_list.append(row)
    return order_list


def filter_orders(cursor,status= None, start = None,end = None):
    conditions=[]
    params = []
    condition = ""
    if status != None:
        conditions.append ('Orders.Order_Status = ?')
        params.append(status)
    if start != None:
        conditions.append('Orders.Date >= ?')
        params.append(start)
    if end != None:
        conditions.append('Orders.Date <= ?')
        params.append(end)
    if conditions   :
        for row in conditions:
            condition += f" AND  {row}  "
    else:
        condition = "AND Orders.Order_Status IN (?,?,?) AND Orders.Date >= datetime('now', '-10 days')"
        params.extend(["Paid","Processing","Sent"])
    cursor.execute(
        f"SELECT Orders.Order_id , Orders.Date  , Users.User_name  , Orders.Price , Orders.Order_Status  , Adress.User_adress ,Adress.Postal_code FROM Orders , Users ,Adress WHERE Orders.User_id = Users.User_id AND Adress.Adress_id = Orders.Adress_id {condition}  ORDER BY Orders.Date DESC ",
        (params),
    )
    rows = cursor.fetchall()
    order_list = []
    for row in rows:
        order_list.append(row)
    return order_list


def update_order(cursor, order_id, status):
    cursor.execute(
        "UPDATE Orders SET  Order_Status = ?  WHERE Order_id  = ?",
        (
            status,
            order_id,
        ),
    )


def Withdrawal_Requests(cursor):
    cursor.execute(
        "SELECT Withdrawal_Requests.Withdrawal_Requests_id , Users.User_name , Withdrawal_Requests.Amount , Withdrawal_Requests.Sheba_number , Withdrawal_Requests.Withdrawal_Requests_Status , Withdrawal_Requests.Requested_at FROM  Users , Withdrawal_Requests  WHERE Users.User_id = Withdrawal_Requests.User_id AND Withdrawal_Requests.Withdrawal_Requests_Status = ? ",
    ('Pending',)
    )
    rows = cursor.fetchall()
    Withdrawal_Requests = []
    for row in rows:
        Withdrawal_Requests.append(row)
    return Withdrawal_Requests
    

def rejected_Withdrawal_Requests(cursor, Withdrawal_Requests_id):
    cursor.execute(
        "UPDATE Withdrawal_Requests SET  Withdrawal_Requests_Status = ?  WHERE Withdrawal_Requests_id  = ?",
        (
            "Rejected",
            Withdrawal_Requests_id,
        ),
    )


def update_Withdrawal_Requests(cursor, Withdrawal_Requests_id):

    cursor.execute(
        "SELECT Users.Walet , Withdrawal_Requests.Amount , Users.User_id FROM Users , Withdrawal_Requests WHERE Users.User_id = Withdrawal_Requests.User_id And Withdrawal_Requests.Withdrawal_Requests_id = ? ",
        (Withdrawal_Requests_id,),
    )
    row = cursor.fetchone()
    if row[0] >= row[1]:
        cursor.execute(
            "UPDATE Withdrawal_Requests SET  Withdrawal_Requests_Status = ?  WHERE Withdrawal_Requests_id  = ?",
            (
                'Approved',
                Withdrawal_Requests_id,
            ),
        )
        cursor.execute(
            "INSERT INTO Wallet_Transactions ( User_id , Type , Amount , Direction  , Description ) VALUES(?,?,?,?,?)",
            (row[2], "Withdrawal", row[1], "Out", "Withdrawal"),
        )
        cursor.execute(
            "UPDATE Users SET Walet = Walet - ?  WHERE  User_id = ?",
            (
                row[1],
                row[2],
            ),
        )
    else:
        rejected_Withdrawal_Requests(cursor, Withdrawal_Requests_id)


def get_all_products(cursor):
    cursor.execute("SELECT * FROM Products WHERE  Is_active = 1")
    rows = cursor.fetchall()
    products_list = []
    for row in rows:
        products_list.append(row)
    return products_list


def add_product (cursor, products_image, products_name, quantity, price, information):
    cursor.execute(
    "INSERT INTO Products (Products_image, Products_name, Quantity, Price, Information) VALUES (?, ?, ?, ?, ?)",
   ( products_image, products_name, quantity, price, information),
    )


def deactivate_product (cursor, product_id):
    cursor.execute(
    "UPDATE Products SET  Is_active = 0  WHERE  Product_id = ?",
    (
        product_id,
    ),
    )


def edit_product (cursor, product_id, products_image, products_name, quantity, price, information):
    cursor.execute(
    "UPDATE Products SET  Products_image = ?, Products_name = ? , Quantity  = ?, Price = ?, Information = ? WHERE  Product_id = ?",
    (
         products_image, products_name, quantity, price, information,product_id
    ),
    )


def customers (cursor):
    cursor.execute("SELECT User_id , User_name , Walet FROM Users")
    rows = cursor.fetchall()
    customers_list = []
    for row in rows:
        customers_list.append(row)
    return customers_list    


def customers_user (cursor, user_id):
    cursor.execute("SELECT User_id , User_name , Walet FROM Users WHERE User_id =? " ,
                    (user_id,)
                    )
    rows = cursor.fetchall()
    customers_user_list = []
    for row in rows:
        customers_user_list.append(row)
    return customers_user_list    


def customers_order (cursor, user_id):
    cursor.execute(
    "SELECT  Orders.Order_id , Orders.Date   , Orders.Price , Orders.Order_Status FROM Orders , Users   WHERE Users.User_id = ? AND Orders.User_id = Users.User_id  ORDER BY Orders.Date DESC ",
    (
        user_id,
    ),
)
    rows = cursor.fetchall()
    order_list = []
    for row in rows:
        order_list.append(row)
    return order_list


def customers_Address (cursor, user_id):
    cursor.execute("SELECT User_adress  , Postal_code  FROM Adress WHERE User_id =? " ,
        (user_id,)
        )
    rows = cursor.fetchall()
    customers_address_list = []    
    for row in rows:
        customers_address_list.append(row)
    return  customers_address_list    


def customers_transactions (cursor, user_id):
    cursor.execute("SELECT Amount , Type , Direction ,  Description , Created_at , Order_id FROM  Wallet_Transactions WHERE User_id =? " ,
        (user_id,)
        )
    rows = cursor.fetchall()
    customers_transactions_list = []    
    for row in rows:
        customers_transactions_list.append(row)
    return customers_transactions_list 


def Wallet_transactions (cursor, q) :
    if not q :
        cursor.execute("SELECT  Wallet_Transactions.Wallet_Transactions_id , Users.User_name , Type , Amount , Direction , Order_id ,  Description , Created_at  FROM  Wallet_Transactions , Users WHERE Users.User_id = Wallet_Transactions.User_id  ORDER BY Created_at DESC" ,
        )
    else :
        cursor.execute("SELECT  Wallet_Transactions.Wallet_Transactions_id , Users.User_name , Type , Amount , Direction , Order_id ,  Description , Created_at  FROM  Wallet_Transactions , Users WHERE Users.User_id = Wallet_Transactions.User_id AND Users.User_name LIKE ? ORDER BY Created_at DESC" ,
                       ('%' + q + '%',),
        ) 
    rows = cursor.fetchall()
    wallet_list = []    
    for row in rows:
        wallet_list.append(row)
    return wallet_list       


def update_admin_pass (cursor , admin_id, password):
        cursor.execute(
        "UPDATE Admin SET  Password = ?  WHERE Admin_id  = ?",
        (
            password,
            admin_id,
            
        ),
    )


def get_admin_password(cursor, admin_id):
    cursor.execute(
        "SELECT Password FROM Admin  WHERE Admin_id= ?  ",
        (admin_id,),
    )
    row = cursor.fetchone()

    return row


def sales_chart (cursor):
    cursor.execute(
            "SELECT SUM(Price) ,  strftime('%Y-%m-%d', Date) FROM Orders  WHERE Order_Status IN (?,?,?) AND Date >= datetime('now', '-7 days') GROUP BY strftime('%Y-%m-%d', Date) ORDER BY strftime('%Y-%m-%d', Date) ",
            ('Paid','Processing','Sent',),
        )
    rows = cursor.fetchall()
    sales_list = []    
    for row in rows:
        sales_list.append(row)
    return sales_list  
    

def notification_count (cursor) :
    cursor.execute(
    "SELECT Order_id  FROM Orders  WHERE  Order_Status = ?  ",
    ("Paid",),
    )
    rows = cursor.fetchall()
    count = 0
    for row in rows:
        count += 1
    cursor.execute(
        "SELECT Withdrawal_Requests_id FROM Withdrawal_Requests  WHERE Withdrawal_Requests_Status = ? ",
    ('Pending',)
    )
    rows = cursor.fetchall()
    for row in rows:
            count += 1
    return count


def global_search(cursor, q):
    products_list = []
    customers_list = []
    order_list = []

    cursor.execute("SELECT Product_id, Products_name, Quantity , Price , Is_active , Information FROM Products WHERE Products_name LIKE ? ", 
                   ('%' + q + '%',),
                   )
    products = cursor.fetchall()
    cursor.execute("SELECT DISTINCT User_id , User_name , Walet FROM Users  WHERE User_name LIKE ? ",
                    ('%' + q + '%',),
                   )
    customers = cursor.fetchall()
    cursor.execute(
    "SELECT  Orders.Order_id , Orders.Date  , Users.User_name  , Orders.Price , Orders.Order_Status , Adress.User_adress ,Adress.Postal_code FROM Orders , Users ,Adress  WHERE Orders.User_id = Users.User_id AND  Adress.Adress_id = Orders.Adress_id AND ( Orders.Order_id LIKE ? OR Users.User_name LIKE ? ) ORDER BY Orders.Date DESC ",
        ('%' + q + '%','%' + q + '%',)
    )
    order = cursor.fetchall()


    for row in products:
        products_list.append(row)
    for row in customers:
        customers_list.append(row)
    for row in order:
        order_list.append(row)

    return products_list , customers_list , order_list

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
