import sqlite3

# محصولات تستی: (عکس، اسم، تعداد، قیمت، توضیحات)
# عکس رو فعلاً None می‌ذاریم چون گفتی فعلاً عکس نمی‌خوای
test_products = [
    ("https://picsum.photos/seed/tshirt/500/500", "تیشرت مشکی", 20, 150000, "تیشرت نخی ساده، سایز فری"),
    ("https://picsum.photos/seed/tshirt/500/500", "کفش اسپرت", 10, 890000, "کفش اسپرت راحتی، ضدآب"),
    ("https://picsum.photos/seed/tshirt/500/500", "کیف پول چرم", 15, 320000, "کیف پول چرم طبیعی دست‌دوز"),
    ("https://picsum.photos/seed/tshirt/500/500", "ساعت مچی", 5, 1250000, "ساعت مچی کلاسیک، ضدضربه"),
    ("https://picsum.photos/seed/tshirt/500/500", "عینک آفتابی", 12, 275000, "عینک آفتابی با لنز UV400"),
]

database_file = "shopkeeper.db"

with sqlite3.connect(database_file) as conn:
    cursor = conn.cursor()
    for product in test_products:
        cursor.execute(
            "INSERT INTO Products (Products_image, Products_name, Quantity, Price, Information) VALUES (?, ?, ?, ?, ?)",
            product,
        )
    conn.commit()

print(f"{len(test_products)} محصول تستی با موفقیت اضافه شد.")