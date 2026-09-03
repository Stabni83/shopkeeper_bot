from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    ApplicationHandlerStop,
)
from dotenv import load_dotenv
import database
import sqlite3


import os


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

markup1 = ReplyKeyboardMarkup(
    [["Shopping Cart", "Products", "Wallet", "Purchase_Status"]]
)

async def start_Command(update: Update, context: ContextTypes.DEFAULT_TYPE):


    await update.message.reply_text(
        "hello body",
        reply_markup=markup1,
    )

    database_file = "shopkeeper.db"
    with sqlite3.connect(database_file) as conn:
        Telegram_id = update.effective_user.id
        cursor = conn.cursor()
        database.find_or_insert_users(cursor, Telegram_id)

        conn.commit()


async def Menu_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if message == "Shopping Cart":
        Telegram_id = update.effective_user.id
        database_file = "shopkeeper.db"
        with sqlite3.connect(database_file) as conn:
            cursor = conn.cursor()
            user_id = database.find_user_id(cursor, Telegram_id)[0]
            Shopping_Cart = database.View_Shopping_Cart(cursor, user_id)
            if Shopping_Cart == 0:
                await update.message.reply_text(
                    "Your shopping cart history is empty.",
                )
            else:
                Description = ""
                for Shopping in Shopping_Cart:
                    Description += f"Product Name: {Shopping[0]} \n Quantity: {Shopping[1]} \n Price {Shopping[2]} \n Status{Shopping[3]}\n"
                if Shopping[3] == "Awaiting payment":
                    address=database.show_adress(cursor, user_id)
                    await update.message.reply_text(
                        Description
                        + f"Total products{Shopping[4]} , Total price of products{Shopping[5]}"
                        + f"adress name : {address[0]} \n adress : {address[1]}",
                        reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Proceed to payment gateway",
                                    callback_data="Payment_Gateway",
                                )
                            ]
                        ]))
                else:
                    await update.message.reply_text(
                            Description
                            + f"Total products{Shopping[4]} , Total price of products{Shopping[5]}",
                            reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton("adress", callback_data="adress_form")]]
                            ),
                        )

            conn.commit()
    elif message == "Purchase_Status":
        Telegram_id = update.effective_user.id
        database_file = "shopkeeper.db"
        with sqlite3.connect(database_file) as conn:
            cursor = conn.cursor()
            user_id = database.find_user_id(cursor, Telegram_id)[0]
            Purchase_Status = database.Purchase_Status(cursor, user_id)
            if Purchase_Status == 0:
                await update.message.reply_text(
                    "You haven't placed any orders yet.",
                )
            else:
                Description = ""
                total_products = 0
                total_price = 0
                for Purchase in Purchase_Status:
                    Description += f"Product Name: {Purchase[0]} \n Quantity: {Purchase[1]} \n Price {Purchase[2]} \n Status{Purchase[3]}\n"
                    total_products += Purchase[4]
                    total_price += Purchase[5]
                await update.message.reply_text(
                    Description
                    + f"Total products : {total_products} , Total price of products : {total_price}"
                )
                for Purchase in Purchase_Status:
                    if Purchase[3] in ("Paid", "Processing"):
                        await update.message.reply_text(
                            f"Product Name: {Purchase[0]} \n Quantity: {Purchase[1]} \n Price {Purchase[2]} \n Status{Purchase[3]}\n",

                            reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton("cancel this order", callback_data=f"canceling_order_{Purchase[6]}")]]
                            ),
                        )
                    

            conn.commit()
    elif message == "Products":
        database_file = "shopkeeper.db"
        with sqlite3.connect(database_file) as conn:

            cursor = conn.cursor()
            products = database.get_all_products(cursor)

            for product in products:

                Add_to_cart_markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Add to cart", callback_data=f"Add to cart_{product[0]}"
                            )
                        ]
                    ]
                )
                await update.message.reply_photo(
                    product[1],
                    f"Product Name: {product[2]} \n Remaining quantity: {product[3]} \n Price: {product[4]} \n Description: {product[5]}",
                    reply_markup=Add_to_cart_markup,
                )

            conn.commit()
    elif message == "Wallet":
        pass
    else:

        await update.message.reply_text("I didn't understand.")


async def Add_to_Cart_button_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):

    product = update.callback_query
    product_id = int(product.data.split("_")[1])
    Quantity = [
        [InlineKeyboardButton("1", callback_data=f"1_{product_id}")],
        [InlineKeyboardButton("2", callback_data=f"2_{product_id}")],
        [InlineKeyboardButton("3", callback_data=f"3_{product_id}")],
        [InlineKeyboardButton("4", callback_data=f"4_{product_id}")],
        [InlineKeyboardButton("5", callback_data=f"5_{product_id}")],
        [InlineKeyboardButton("6", callback_data=f"6_{product_id}")],
        [InlineKeyboardButton("7", callback_data=f"7_{product_id}")],
        [InlineKeyboardButton("8", callback_data=f"8_{product_id}")],
        [InlineKeyboardButton("9", callback_data=f"9_{product_id}")],
        [InlineKeyboardButton("10", callback_data=f"10_{product_id}")],
        [InlineKeyboardButton("More", callback_data=f"More_{product_id}")],
    ]

    Product_Quantity_Button = InlineKeyboardMarkup(Quantity)

    await update.callback_query.answer()

    await update.callback_query.message.reply_text(
        "How many of this product do you want?", reply_markup=Product_Quantity_Button
    )


async def Quantity_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query
    quantity = int(message.data.split("_")[0])
    product_id = int(message.data.split("_")[1])
    Telegram_id = update.effective_user.id
    await update.callback_query.message.reply_text(
        Check_Availability_And_Purchase(product_id, quantity, Telegram_id),
    )


async def More_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query
    product_id = int(message.data.split("_")[1])

    await update.callback_query.answer()

    await update.callback_query.message.reply_text(
        "Enter the desired quantity.",
    )
    context.user_data["more_quantity"] = product_id


async def Receive_Typed_Quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "more_quantity" in context.user_data:

        if update.message.text.isdigit():
            product_id = int(context.user_data["more_quantity"])
            quantity = int(update.message.text)
            Telegram_id = update.effective_user.id
            await update.message.reply_text(
                Check_Availability_And_Purchase(product_id, quantity, Telegram_id),
            )
            del context.user_data["more_quantity"]

        else:
            await update.message.reply_text("Please enter only your order.")
        raise ApplicationHandlerStop()
    else:
        return


async def Address_Form(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    await update.callback_query.message.reply_text("Enter your new adress")
    context.user_data["adress_form"] = {"step": "adress_text", "data": {}}


async def Address_Form_Handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "adress_form" in context.user_data:

        if "adress_text" in context.user_data["adress_form"]["step"]:

            await update.message.reply_text(
                "Enter your postal code.",
            )
            context.user_data["adress_form"]["data"][
                "adress_text"
            ] = update.message.text
            context.user_data["adress_form"]["step"] = "Postal_code"
            raise ApplicationHandlerStop()

        elif "Postal_code" in context.user_data["adress_form"]["step"]:

            await update.message.reply_text(
                "What name would you give this address?",
            )
            context.user_data["adress_form"]["data"][
                "Postal_code"
            ] = update.message.text
            context.user_data["adress_form"]["step"] = "adress_name"
            raise ApplicationHandlerStop()

        elif "adress_name" in context.user_data["adress_form"]["step"]:

            Telegram_id = update.effective_user.id
            context.user_data["adress_form"]["data"][
                "adress_name"
            ] = update.message.text

            adress_data = context.user_data["adress_form"]["data"]

            await update.message.reply_text("The address was successfully registered.")
            await update.message.reply_text(
                f"Your name address:{adress_data['adress_name']}\n Your address:{adress_data['adress_text']}\n Postal code: {adress_data['Postal_code']} ",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "confirm this address",
                                callback_data="confirm_address",
                            )
                        ]
                    ]
                ),
            )

            raise ApplicationHandlerStop()

        else:
            await update.message.reply_text("I didn't understand.")

            raise ApplicationHandlerStop()
    else:
        return


async def Confirm_address(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "adress_form" in context.user_data:

        Telegram_id = update.effective_user.id
        database_file = "shopkeeper.db"
        with sqlite3.connect(database_file) as conn:
            adress_data = context.user_data["adress_form"]["data"]

            cursor = conn.cursor()
            user_id = database.find_user_id(cursor, Telegram_id)[0]
            adress_id = database.add_address(
                cursor,
                user_id,
                adress_data["adress_name"],
                adress_data["adress_text"],
                adress_data["Postal_code"],
            )
            order_id = database.show_order_id(cursor, user_id)[0]

            database.finalize_order(cursor, order_id, adress_id)

            conn.commit()
        await update.callback_query.answer()

        await update.callback_query.message.reply_text(
            "Everything is all set; you can complete your purchase.",
            reply_markup=InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "Proceed to payment gateway",
                callback_data="Payment_Gateway",
            )
        ]
    ]
     
    )
            
        )

        del context.user_data["adress_form"]
    else:
        return


async def Payment_Gateway(update: Update, context: ContextTypes.DEFAULT_TYPE):

    Telegram_id = update.effective_user.id
    database_file = "shopkeeper.db"
    with sqlite3.connect(database_file) as conn:

        cursor = conn.cursor()
        user_id = database.find_user_id(cursor, Telegram_id)[0]
        order_id = database.show_order_id_awaiting(cursor, user_id)[0]
        database.Payment_Gateway(cursor, order_id)

        conn.commit()

    await update.callback_query.message.reply_text(
        "Thank you for your purchase.",
         reply_markup=markup1,
        
    )


async def Confirm_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query
    order_id = int(message.data.split("_")[2])
    await update.callback_query.message.reply_text(

    "Are you sure you want to cancel your purchase?",

    reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("cancel this order", callback_data=f"confirm_cancel_{order_id}")]]
    ),
    )   


async def Cancel_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query
    order_id = int(message.data.split("_")[2])
    Telegram_id = update.effective_user.id
    database_file = "shopkeeper.db"
    with sqlite3.connect(database_file) as conn:

        cursor = conn.cursor()
        user_id = database.find_user_id(cursor, Telegram_id)[0]   
        database.cancel_order(cursor, user_id, order_id)    

        conn.commit()
        await update.callback_query.message.reply_text(
        "Your purchase has been successfully cancelled.",
         reply_markup=markup1,
        
    )


def Check_Availability_And_Purchase(product_id, quantity, Telegram_id):

    database_file = "shopkeeper.db"
    with sqlite3.connect(database_file) as conn:

        cursor = conn.cursor()
        product_quantity = database.Product_Equilibrium_Analysis(
            cursor, product_id, quantity
        )[0]
        price = database.Product_Equilibrium_Analysis(cursor, product_id)[1]
        if product_quantity < quantity:
            return "The number of orders exceeds the number of products."

        else:
            user_id = database.find_user_id(cursor, Telegram_id)[0]
            database.add_to_cart(cursor, product_id, quantity, user_id, price)

            return "Your purchase has been recorded in the shopping cart."

        conn.commit()


def main():

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_Command))
    application.add_handler(
        MessageHandler(
            filters=filters.TEXT & ~filters.COMMAND,
            callback=Address_Form_Handler,
            ),
            group=0,
        )
    application.add_handler(
        MessageHandler(
            filters=filters.TEXT & ~filters.COMMAND,
            callback=Receive_Typed_Quantity,
        ),
        group=1,
    )
    application.add_handler(
        MessageHandler(
            filters=filters.TEXT & ~filters.COMMAND,
            callback=Menu_message_handler,
        ),
        group=2,
    )
    application.add_handler(
        CallbackQueryHandler(
            pattern="^Add to cart_", callback=Add_to_Cart_button_handler
        )
    )
    application.add_handler(
        CallbackQueryHandler(pattern="^[0-9]", callback=Quantity_button_handler)
    )
    application.add_handler(
        CallbackQueryHandler(pattern="^More", callback=More_button_handler)
    )
    application.add_handler(
        CallbackQueryHandler(pattern="^adress_form", callback=Address_Form)
    )
    application.add_handler(
        CallbackQueryHandler(pattern="^confirm_address", callback=Confirm_address)
    )
    application.add_handler(
        CallbackQueryHandler(pattern="^Payment_Gateway", callback=Payment_Gateway)
    )
    application.add_handler(
        CallbackQueryHandler(pattern="^canceling_order", callback=Confirm_cancel)
    )
    application.add_handler(
    CallbackQueryHandler(pattern="^confirm_cancel", callback=Cancel_purchase)
    )
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":

    main()
