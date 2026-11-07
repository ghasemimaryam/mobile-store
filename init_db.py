import sqlite3
from werkzeug.security import generate_password_hash

con = sqlite3.connect("database.db")
con.executescript(open("schema.sql").read())

cur = con.execute("INSERT INTO categories (name) VALUES (?)", ("Phones",))
phones_id = cur.lastrowid
cur = con.execute("INSERT INTO categories (name) VALUES (?)", ("Headphones",))
headphones_id = cur.lastrowid
cur = con.execute("INSERT INTO categories (name) VALUES (?)", ("Power Banks",))
powerbanks_id = cur.lastrowid

con.execute(
    "INSERT INTO products (name, brand, price, category_id, image, rating, is_new) VALUES (?, ?, ?, ?, ?, ?, ?)",
    ("Galaxy S24", "Samsung", 42000000, phones_id, "samsung.jpg", 3.9, 1)
)
con.execute(
    "INSERT INTO products (name, brand, price, category_id, image, rating, is_new) VALUES (?, ?, ?, ?, ?, ?, ?)",
    ("iPhone 15", "Apple", 54000000, phones_id, "iphone15.jpg", 4.5, 1)
)
con.execute(
    "INSERT INTO products (name, brand, price, category_id, image, rating, is_new) VALUES (?, ?, ?, ?, ?, ?, ?)",
    ("QCY Wireless Earbuds", "QCY", 1450000, headphones_id, "qcy.jpg", 4.0, 0)
)
con.execute(
    "INSERT INTO products (name, brand, price, category_id, image, rating, is_new) VALUES (?, ?, ?, ?, ?, ?, ?)",
    ("Konfulon M17W", "KONFULON", 4000000, powerbanks_id, "konfulon.jpg", 4.3, 1)
)
con.execute(
    "INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, ?)",
    ("Admin", "admin@example.com", generate_password_hash("admin123"), 1)
)
con.commit()
con.close()

print("دیتابیس ساخته شد ✅")