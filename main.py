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
                
                for Shopping in Shopping_Cart:
                    Description = ""
                    Description += f"Product Name: {Shopping[0]} \n Quantity: {Shopping[1]} \n Price {Shopping[2]} \n Status{Shopping[3]}\n"
                    if Shopping[3] == "Awaiting payment":
                        address = database.show_adress(cursor, user_id)
                        await update.message.reply_text(
                            Description
                            + f"Total products{Shopping[4]} , Total price of products{Shopping[5]}"
                            + f"adress name : {address[0]} \n adress : {address[1]}",
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton(
                                            "Proceed to payment gateway",
                                            callback_data=f"Payment_Gateway_{Shopping[6]}",
                                        )
                                    ]
                                ]
                            ),
                        )
                    else:
                        await update.message.reply_text(
                            Description
                            + f"Total products{Shopping[4]} , Total price of products{Shopping[5]}",
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton(
                                            "adress", callback_data="adress_form"
                                        )
                                    ]
                                ]
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
                                [
                                    [
                                        InlineKeyboardButton(
                                            "cancel this order",
                                            callback_data=f"canceling_order_{Purchase[6]}",
                                        )
                                    ]
                                ]
                            ),
                        )

            conn.commit()
    elif message == "Products":
        database_file = "shopkeeper.db"
        with sqlite3.connect(database_file) as conn:

            cursor = conn.cursor()
            products = database.get_all_products(cursor)

            for product in products:

                await update.message.reply_photo(
                    product[1],
                    f"Product Name: {product[2]} \n Remaining quantity: {product[3]} \n Price: {product[4]} \n Description: {product[5]}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Add to cart",
                                    callback_data=f"Add to cart_{product[0]}",
                                )
                            ]
                        ]
                    ),
                )

            conn.commit()
    elif message == "Wallet":
        database_file = "shopkeeper.db"
        with sqlite3.connect(database_file) as conn:
            Telegram_id = update.effective_user.id
            cursor = conn.cursor()
            user_id = database.find_user_id(cursor, Telegram_id)[0]
            Wallet_Balance = database.Checking_wallet_balance(cursor, user_id)[0]
            conn.commit()
            await update.message.reply_text(
                f"Wallet Balance :{Wallet_Balance} ",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Top up wallet", callback_data=f"Top up wallet"
                            ),
                            InlineKeyboardButton(
                                "Withdrawal of funds",
                                callback_data=f"Withdrawal_of_funds",
                            ),
                        ]
                    ]
                ),
            )

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
            wallet = database.Checking_wallet_balance(cursor, user_id)[0]
            price = database.Checking_price_order(cursor, order_id)[0]
            conn.commit()
        if wallet >= price:
            await update.callback_query.answer()

            await update.callback_query.message.reply_text(
                "Everything is all set; you can complete your purchase. \n"
                + f"Wallet Balance : {wallet}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Payment from wallet balance",
                                callback_data=f"Payment_wallet_{order_id}",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "Proceed to payment gateway",
                                callback_data=f"Payment_Gateway_{order_id}",
                            )
                        ],
                    ]
                ),
            )
        else:
            await update.callback_query.answer()

            await update.callback_query.message.reply_text(
                "Everything is all set; you can complete your purchase.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Proceed to payment gateway",
                                callback_data=f"Payment_Gateway_{order_id}",
                            )
                        ]
                    ]
                ),
            )

        del context.user_data["adress_form"]
    else:
        return


async def Payment_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    Telegram_id = update.effective_user.id
    message = update.callback_query
    order_id = int(message.data.split("_")[2])
    database_file = "shopkeeper.db"
    with sqlite3.connect(database_file) as conn:

        cursor = conn.cursor()
        user_id = database.find_user_id(cursor, Telegram_id)[0]
        price = database.Checking_price_order(cursor, order_id)[0]
        database.Payment_Gateway(cursor, order_id)
        database.record_wallet_transaction(
            cursor, user_id, "Purchase", price, "Out", "To purchase", order_id
        )
        conn.commit()

    await update.callback_query.message.reply_text(
        "Thank you for your purchase.",
        reply_markup=markup1,
    )


async def Payment_Gateway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query
    if "topup" in message.data.split("_")[2]:
        amount = int(message.data.split("_")[3])
        await update.callback_query.message.reply_text(
            "Since this is a test project, we are not using the actual payment gateway; instead, we are using a mock version. Please select an option to proceed.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Successful payment",
                            callback_data=f"top_up_Confirm_{amount}_1",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Payment failed",
                            callback_data=f"top_up_Confirm_{amount}_0",
                        )
                    ],
                ]
            ),
        )
    else:
        order_id = int(message.data.split("_")[2])
        await update.callback_query.answer()

        await update.callback_query.message.reply_text(
            "Since this is a test project, we are not using the actual payment gateway; instead, we are using a mock version. Please select an option to proceed.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Successful payment",
                            callback_data=f"Payment_Confirmation_{order_id}_1",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Payment failed",
                            callback_data=f"Payment_Confirmation_{order_id}_0",
                        )
                    ],
                ]
            ),
        )


async def Payment_Confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query
    order_id = int(message.data.split("_")[2])
    payment_confirmation = int(message.data.split("_")[3])
    if payment_confirmation == 0:
        await update.callback_query.message.reply_text(
            "Your payment was unsuccessful.\n Please try again.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Repayment",
                            callback_data=f"Payment_Gateway_{order_id}",
                        )
                    ]
                ]
            ),
        )
    else:
        database_file = "shopkeeper.db"
        with sqlite3.connect(database_file) as conn:

            cursor = conn.cursor()
            database.Payment_Gateway(cursor, order_id)
            conn.commit()
        await update.callback_query.message.reply_text(
            "The operation was successful. Thank you for your purchase.",
        )


async def Confirm_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query
    order_id = int(message.data.split("_")[2])
    await update.callback_query.message.reply_text(
        "Are you sure you want to cancel your purchase?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "cancel this order", callback_data=f"confirm_cancel_{order_id}"
                    )
                ]
            ]
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


async def Top_up_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.callback_query.answer()

    await update.callback_query.message.reply_text(
        "Enter the desired quantity.",
    )
    context.user_data["Top_up_wallet"] = True


async def Amount_top_up_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "Top_up_wallet" in context.user_data:
        amount = int(update.message.text)
        await update.message.reply_text(
            f"The amount by which you want to top up your wallet : {amount}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Confirm", callback_data=f"Payment_Gateway_topup_{amount}"
                        )
                    ]
                ]
            ),
        )
        del context.user_data["Top_up_wallet"]

        raise ApplicationHandlerStop()
    else:
        return


async def top_up_Confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query
    amount = int(message.data.split("_")[3])
    payment_confirmation = int(message.data.split("_")[4])
    if payment_confirmation == 0:
        await update.callback_query.message.reply_text(
            "Your payment was unsuccessful.\n Please try again.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Repayment",
                            callback_data=f"Payment_Gateway_topup_{amount}",
                        )
                    ]
                ]
            ),
        )
    else:
        Telegram_id = update.effective_user.id
        database_file = "shopkeeper.db"
        with sqlite3.connect(database_file) as conn:
            cursor = conn.cursor()

            user_id = database.find_user_id(cursor, Telegram_id)[0]
            database.record_wallet_transaction(
                cursor, user_id, "Top_up", amount, "In", f"Top up your wallet"
            )
            

            conn.commit()
        await update.callback_query.message.reply_text(
            "Your wallet has been successfully topped up.",
        )


async def Withdrawal_of_funds(update: Update, context: ContextTypes.DEFAULT_TYPE):

    Telegram_id = update.effective_user.id
    database_file = "shopkeeper.db"
    with sqlite3.connect(database_file) as conn:

        cursor = conn.cursor()
        user_id = database.find_user_id(cursor, Telegram_id)[0]

        wallet = database.Checking_wallet_balance(cursor, user_id)[0]

        conn.commit()
    await update.callback_query.answer()

    await update.callback_query.message.reply_text(
        f"Your wallet balance : {wallet} \n"
        + "How much do you want to deduct from your account balance?",
    )
    context.user_data["Withdrawal_of_funds"] = {
        "amount": "",
        "sheba_number": "",
        "step": 1,
    }


async def Operations_Withdrawal_of_funds(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if "Withdrawal_of_funds" in context.user_data:
        if context.user_data["Withdrawal_of_funds"]["step"] == 1:

            amount = context.user_data["Withdrawal_of_funds"]["amount"] = int(
                update.message.text
            )
            Telegram_id = update.effective_user.id
            database_file = "shopkeeper.db"
            with sqlite3.connect(database_file) as conn:

                cursor = conn.cursor()
                user_id = database.find_user_id(cursor, Telegram_id)[0]
                wallet = database.Checking_wallet_balance(cursor, user_id)[0]

                conn.commit()
            if amount > wallet:
                await update.message.reply_text(
                    "The requested amount exceeds your wallet balance; please submit the request again.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Withdrawal of funds",
                                    callback_data=f"Withdrawal_of_funds",
                                )
                            ]
                        ]
                    ),
                )

                raise ApplicationHandlerStop()
            else:
                await update.message.reply_text(
                    "Please enter your Sheba number.",
                )
                context.user_data["Withdrawal_of_funds"]["step"] = 2
                raise ApplicationHandlerStop()
        elif context.user_data["Withdrawal_of_funds"]["step"] == 2:

            sheba_number = context.user_data["Withdrawal_of_funds"]["sheba_number"] = (
                update.message.text
            )
            if not (
                sheba_number.startswith("IR")
                and len(sheba_number) == 26
                and sheba_number[2:].isdigit()
            ):
                await update.message.reply_text(
                    "Your Sheba number is incorrect; please try again.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Withdrawal of funds",
                                    callback_data=f"Withdrawal_of_funds",
                                )
                            ]
                        ]
                    ),
                )
                raise ApplicationHandlerStop()
            else:
                amount = context.user_data["Withdrawal_of_funds"]["amount"]
                Telegram_id = update.effective_user.id
                database_file = "shopkeeper.db"
                with sqlite3.connect(database_file) as conn:
                    cursor = conn.cursor()
                    user_id = database.find_user_id(cursor, Telegram_id)[0]
                    database.Withdrawal_of_funds(cursor, user_id, sheba_number, amount)
                    conn.commit()
                await update.message.reply_text(
                    "Your request has been received and will be reviewed as soon as possible.",
                    reply_markup=markup1,
                )

                del context.user_data["Withdrawal_of_funds"]
                raise ApplicationHandlerStop()

    else:
        return


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
            callback=Amount_top_up_wallet,
        ),
        group=2,
    )
    application.add_handler(
        MessageHandler(
            filters=filters.TEXT & ~filters.COMMAND,
            callback=Operations_Withdrawal_of_funds,
        ),
        group=3,
    )
    application.add_handler(
        MessageHandler(
            filters=filters.TEXT & ~filters.COMMAND,
            callback=Menu_message_handler,
        ),
        group=4,
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
        CallbackQueryHandler(pattern="^Payment_wallet", callback=Payment_wallet)
    )
    application.add_handler(
        CallbackQueryHandler(
            pattern="^Payment_Confirmation", callback=Payment_Confirmation
        )
    )
    application.add_handler(
        CallbackQueryHandler(pattern="^canceling_order", callback=Confirm_cancel)
    )
    application.add_handler(
        CallbackQueryHandler(pattern="^confirm_cancel", callback=Cancel_purchase)
    )
    application.add_handler(
        CallbackQueryHandler(pattern="^Top up wallet", callback=Top_up_wallet)
    )
    application.add_handler(
        CallbackQueryHandler(pattern="^top_up_Confirm", callback=top_up_Confirm)
    )
    application.add_handler(
        CallbackQueryHandler(
            pattern="^Withdrawal_of_funds", callback=Withdrawal_of_funds
        )
    )
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":

    main()
