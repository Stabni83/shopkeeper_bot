from flask import Flask, request, render_template, redirect, url_for , flash , send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user ,current_user
import database
import sqlite3
from werkzeug.security import check_password_hash , generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import uuid

load_dotenv()
database_file = os.getenv("DATABASE_PATH")
IMAGES_PATH = os.getenv("IMAGES_PATH")
os.makedirs(IMAGES_PATH, exist_ok=True)

class AdminUser(UserMixin):
    def __init__(self, admin_name, admin_id):
        self.Admin_name = admin_name
        self.id = admin_id


login_manager = LoginManager()

app = Flask(__name__)

login_manager.init_app(app)

app.secret_key = os.getenv("SECRET_KEY")

login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()

        admin_name = database.Show_admin(cursor, user_id)[1]
        admin_id = database.Show_admin(cursor, user_id)[0]

    conn.commit()
    Admin = AdminUser(admin_name, admin_id)
    return Admin

@app.context_processor
def notification_count():
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        notification_count = database.notification_count (cursor)
    conn.commit()
    return{'notification_count' : notification_count}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]
        
        with sqlite3.connect(database_file) as conn:
            cursor = conn.cursor()
            passhash = database.find_admin(cursor, name)[0]
            admin_id = database.find_admin(cursor, name)[1]
        conn.commit()
        if check_password_hash(passhash, password):
            Admin = AdminUser(name, admin_id)
            login_user(Admin)
            return redirect(url_for("dashboard"))
        else:
            return render_template(
                "login.html", error="Invalid username or password"
            )


@app.route("/", methods=["GET"])
@login_required
def dashboard():
    recent_order_list = []
    sales_chart_list = []
    stats = {}
    financial = {}
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        stats["new_orders"] = database.stats_new_orders(cursor)
        stats["processing_orders"] = database.stats_Processing_orders(cursor)
        stats["total_orders"] = database.stats_total_orders(cursor)
        stats["revenue"] = database.stats_revenue(cursor)
        stats["customers"] = database.stats_customers(cursor)
        financial["pending"] = database.financial_pending(cursor)
        financial["pending_withdrawals"] = database.financial_pending_withdrawals(
            cursor
        )
        financial["received"] = database.stats_revenue(cursor)
        pending_withdrawals = database.pending_withdrawals(cursor)
        recent_orders = database.recent_orders(cursor)
        sales_chart = database.sales_chart(cursor)

    conn.commit()
    for row in recent_orders:
        recent_order = {}
        recent_order["Order_id"] = row[0]
        recent_order["Date"] = row[1]
        recent_order["User_name"] = row[2]
        recent_order["Price"] = row[3]
        recent_order["status_label"] = row[4]
        recent_order["status"] = row[4].lower()
        recent_order["Address"] = row[5]
        recent_order["Postal_code"] = row[6]
        recent_order_list.append(recent_order)

    for row in sales_chart:
        sales_chart_dic = {}
        sales_chart_dic["value"] = row[0]
        sales_chart_dic["label"] = row[1]

        sales_chart_list.append(sales_chart_dic)

    return render_template(
        "dashboard.html",
        stats=stats,
        financial=financial,
        pending_withdrawals=pending_withdrawals,
        recent_orders=recent_order_list,
        sales_chart=sales_chart_list,
    )


@app.route("/update_order_status", methods=["POST"])
@login_required
def update_order_status():
    order_id = request.form.get("order_id")
    status = request.form.get("status").capitalize()
    if status in ["Processing", "Sent"]:
        
        with sqlite3.connect(database_file) as conn:
            cursor = conn.cursor()
            database.update_order(cursor, order_id, status)

        conn.commit()
    return redirect(url_for("orders_page"))

@app.route("/withdrawals_page", methods=["GET"])
@login_required
def withdrawals_page():
    withdrawals_list=[]
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        Withdrawal_Requests= database. Withdrawal_Requests(cursor)
        pending_withdrawals = database.pending_withdrawals(cursor)
    conn.commit()
    for row in  Withdrawal_Requests:
        Withdrawal_Requests_dic={}
        Withdrawal_Requests_dic['id'] = row[0]
        Withdrawal_Requests_dic['User_name'] = row[1]
        Withdrawal_Requests_dic['amount'] = row[2]
        Withdrawal_Requests_dic['sheba_number'] = row[3]
        Withdrawal_Requests_dic['status'] = row[4].lower()
        Withdrawal_Requests_dic['requested_at'] = row[5]
        withdrawals_list.append (Withdrawal_Requests_dic)
    return render_template(
        "withdrawals.html",
        requests = withdrawals_list,
        pending_withdrawals=pending_withdrawals
    )


@app.route("/approve_withdrawal", methods=["POST"])
@login_required
def approve_withdrawal():
    request_id = request.form.get("request_id")
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        database.update_Withdrawal_Requests(cursor, request_id)  

    conn.commit()
    return redirect(url_for("withdrawals_page"))

@app.route("/reject_withdrawal", methods=["POST"])
@login_required
def reject_withdrawal():
    request_id = request.form.get("request_id")
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        database.rejected_Withdrawal_Requests(cursor, request_id)  

    conn.commit()
    return redirect(url_for("withdrawals_page"))


@app.route("/products_page", methods=["GET"])
@login_required
def products_page():
    products_list=[]
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        products= database. get_all_products(cursor)
    conn.commit()
    for row in  products:
        products_dic={}
        products_dic['Product_id'] = row[0]
        products_dic['Products_image'] = row[1]
        products_dic['Products_name'] = row[2]
        products_dic['Quantity'] = row[3]
        products_dic['Price'] = row[4]
        products_dic['Is_active'] = row[5]
        products_dic['Information'] = row[6]
        products_list.append (products_dic)
    return render_template(
        "products.html",
        products = products_list,
        )


@app.route("/add_product", methods=["POST"])
@login_required
def add_product():
    name =  request.form.get("name")
    price =  request.form.get("price")
    quantity = request.form.get("quantity")
    information = request.form.get("information")

    image_file = request.files.get("image")
    image_filename = None
    if image_file and image_file.filename:
        safe_name = secure_filename(image_file.filename)
        image_filename = f"{uuid.uuid4().hex}_{safe_name}"
        image_file.save(os.path.join(IMAGES_PATH, image_filename))
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        database.add_product(cursor, image_filename , name , quantity , price , information)  

    conn.commit()
    return redirect(url_for("products_page"))


@app.route("/edit_product", methods=["POST"])
@login_required
def edit_product():
    product_id =  request.form.get("product_id")
    name =  request.form.get("name")
    price =  request.form.get("price")
    quantity = request.form.get("quantity")
    information = request.form.get("information")
    current_image = request.form.get("current_image")

    image_file = request.files.get("image")
    if image_file and image_file.filename:
        safe_name = secure_filename(image_file.filename)
        image_filename = f"{uuid.uuid4().hex}_{safe_name}"
        image_file.save(os.path.join(IMAGES_PATH, image_filename))
    else:
        image_filename = current_image
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        database.edit_product(cursor, product_id , image_filename , name , quantity , price , information)  

    conn.commit()
    return redirect(url_for("products_page"))


@app.route("/product_image/<filename>")
@login_required
def product_image(filename):
    return send_from_directory(IMAGES_PATH, filename)


@app.route("/deactivate_product", methods=["POST"])
@login_required
def deactivate_product():
    product_id =  request.form.get("product_id")
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        database.deactivate_product(cursor, product_id)  

    conn.commit()
    return redirect(url_for("products_page"))


@app.route("/customers_page", methods=["GET"])
@login_required
def customers_page ():
    customers_list=[]
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        customers= database.customers(cursor)
    conn.commit()
    for row in  customers:
        customers_dic={}
        customers_dic['User_id'] = row[0]
        customers_dic['User_name'] = row[1]
        customers_dic['Walet'] = row[2]
        customers_list.append (customers_dic)
    return render_template(
        "customers.html",
        customers = customers_list,
        )


@app.route("/customer_detail/<user_id>", methods=["GET"])
@login_required
def customer_detail (user_id):
    customers_order_list=[]
    customers_address_list=[]
    customers_transactions_list=[]
    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        customers= database.customers_user(cursor,user_id)
        customers_order= database. customers_order(cursor,user_id)
        customers_address= database. customers_Address(cursor,user_id)
        customers_transactions= database. customers_transactions(cursor,user_id)

    conn.commit()

    for row in  customers:
            customers_dic={}
            customers_dic['User_id'] = row[0]
            customers_dic['User_name'] = row[1]
            customers_dic['Walet'] = row[2]


    for row in  customers_order:
        customers_order_dic={}
        customers_order_dic['Order_id'] = row[0]
        customers_order_dic['Date'] = row[1]
        customers_order_dic['Price'] = row[2]
        customers_order_dic['status'] = row[3].lower()
        customers_order_dic['status_label'] = row[3]
        customers_order_list.append (customers_order_dic)

    for row in  customers_address:
        customers_address_dic={}
        customers_address_dic['Address'] = row[0]
        customers_address_dic['Postal_code'] = row[1]
        customers_address_list.append (customers_address_dic)

    for row in  customers_transactions:
        customers_transactions_dic={}
        customers_transactions_dic['amount'] = row[0]
        customers_transactions_dic['type'] = row[1]
        customers_transactions_dic['direction'] = row[2]
        customers_transactions_dic['description'] = row[3]
        customers_transactions_dic['created_at'] = row[4]
        customers_transactions_dic['order_id'] = row[5]
        customers_transactions_list.append (customers_transactions_dic)   


    return render_template(
        "customer_detail.html",
        customer = customers_dic ,
        orders = customers_order_list,
        addresses= customers_address_list,
        transactions = customers_transactions_list
        )


@app.route("/settings_page", methods=["GET"])
@login_required
def settings_page ():

    return render_template(
        "settings.html",
        )


@app.route("/change_password", methods=["POST"])
@login_required
def change_password ():
    admin_id = current_user.id
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')


    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        passhash = database.get_admin_password(cursor, admin_id)[0]
        if check_password_hash (passhash , current_password):
            if new_password == confirm_password :
                new_passhash = generate_password_hash(new_password)
                database.update_admin_pass (cursor , admin_id, new_passhash)
                flash("Password updated successfully.", "success")
                return redirect(url_for("settings_page"))
            else:
                flash("New password and confirmation do not match.", "error")
                return redirect(url_for("settings_page"))
        else:

            flash("Current password is incorrect.", "error")
            return redirect(url_for("settings_page"))
        
    conn.commit()


@app.route("/orders_page", methods=["GET"])
@login_required
def orders_page ():
    status = request.args.get('status')
    start = request.args.get('start')
    end = request.args.get('end')
    cap_status = ''
    if status :
        cap_status = status.capitalize()
    filter_orders_list = []

    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        filter_orders = database.filter_orders(cursor ,cap_status , start , end )
    conn.commit()
    for row in filter_orders:
        filter_orders_dic = {}
        filter_orders_dic['Order_id'] = row[0]
        filter_orders_dic['Date'] = row[1]
        filter_orders_dic['User_name'] = row[2]
        filter_orders_dic['Price'] = row[3]
        filter_orders_dic['status'] = row[4].lower()
        filter_orders_dic['status_label'] = row[4]
        filter_orders_dic['Address'] = row[5]
        filter_orders_dic['Postal_code'] = row[6]
        filter_orders_list.append(filter_orders_dic)

    return render_template(
        "orders.html",
        orders = filter_orders_list,
        status_filter = status
        )


@app.route("/global_search", methods=["GET"])
@login_required
def global_search ():
    q = request.args.get('q')

    products_list = []
    orders_list = []
    customers_list = []

    
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        if q :
            products, customers, orders = database.global_search(cursor, q)
        else :
            products = []
            customers = []
            orders = []
    conn.commit()    
    for row in  products:
        products_dic={}
        products_dic['Product_id'] = row[0]
        products_dic['Products_name'] = row[1]
        products_dic['Quantity'] = row[2]
        products_dic['Price'] = row[3]
        products_dic['Is_active'] = row[4]
        products_dic['Information'] = row[5]
        products_list.append (products_dic)

    for row in  customers:
        customers_dic={}
        customers_dic['User_id'] = row[0]
        customers_dic['User_name'] = row[1]
        customers_dic['Walet'] = row[2]
        customers_list.append (customers_dic)

    for row in orders:
        orders_dic = {}
        orders_dic['Order_id'] = row[0]
        orders_dic['Date'] = row[1]
        orders_dic['User_name'] = row[2]
        orders_dic['Price'] = row[3]
        orders_dic['status'] = row[4].lower()
        orders_dic['status_label'] = row[4]
        orders_dic['Address'] = row[5]
        orders_dic['Postal_code'] = row[6]
        orders_list.append(orders_dic)

    return render_template(
        "search.html",
        q = q,
        orders = orders_list,
        products = products_list,
        customers = customers_list,
    )


@app.route("/wallet_page", methods=["GET"])
@login_required
def wallet_page ():
    q = request.args.get('q')

    transactions_list = []
    with sqlite3.connect(database_file) as conn:
        cursor = conn.cursor()
        transactions = database.Wallet_transactions(cursor, q)
    conn.commit() 
    for row in  transactions:
        transactions_dic={}
        transactions_dic['id'] = row[0]
        transactions_dic['User_name'] = row[1]
        transactions_dic['type'] = row[2]
        transactions_dic['amount'] = row[3]
        transactions_dic['direction'] = row[4].lower()
        transactions_dic['order_id'] = row[5]
        transactions_dic['description'] = row[6]
        transactions_dic['created_at'] = row[7]
        transactions_list.append (transactions_dic)
    return render_template(
    "wallet.html",
    transactions = transactions_list  
    )

@app.route("/logout")


@login_required
def logout():
    logout_user()
    return render_template("login.html")


if __name__ == "__main__":

    app.run(debug=True)