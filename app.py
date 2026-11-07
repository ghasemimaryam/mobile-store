import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

@app.route("/")
def index():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    products = con.execute("SELECT * FROM products").fetchall()

    wishlist_ids = []
    if "user_id" in session:
        wishlist_rows = con.execute(
            "SELECT product_id FROM wishlist_items WHERE user_id = ?",
            (session["user_id"],)
        ).fetchall()
        wishlist_ids = [row["product_id"] for row in wishlist_rows]

    con.close()
    return render_template("index.html", products=products, wishlist_ids=wishlist_ids)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    product = con.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    con.close()

    if product is None:
        return render_template("404.html"), 404

    return render_template("product.html", product=product)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row

        existing = con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            con.close()
            return render_template("register.html", error="This email is already registered.")

        hashed_password = generate_password_hash(password)
        con.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )
        con.commit()
        con.close()
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        user = con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        con.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["is_admin"] = user["is_admin"]
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    existing = con.execute(
        "SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?",
        (session["user_id"], product_id)
    ).fetchone()

    if existing:
        con.execute(
            "UPDATE cart_items SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?",
            (session["user_id"], product_id)
        )
    else:
        con.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
            (session["user_id"], product_id, 1)
        )

    con.commit()
    con.close()

    return redirect(url_for("index"))

@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    items = con.execute(
        """SELECT cart_items.id AS cart_item_id, cart_items.quantity,
                  products.name, products.price, products.image
           FROM cart_items
           JOIN products ON cart_items.product_id = products.id
           WHERE cart_items.user_id = ?""",
        (session["user_id"],)
    ).fetchall()
    total=0
    for item in items:
        total += item["price"] * item["quantity"]
    con.close()

    return render_template("cart.html", items=items, total=total)

@app.route("/cart/update/<int:cart_item_id>/<action>", methods=["POST"])
def update_cart(cart_item_id, action):
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    if action == "increase":
        con.execute(
            "UPDATE cart_items SET quantity = quantity + 1 WHERE id = ? AND user_id = ?",
            (cart_item_id, session["user_id"])
        )
    elif action == "decrease":
        item = con.execute(
            "SELECT quantity FROM cart_items WHERE id = ? AND user_id = ?",
            (cart_item_id, session["user_id"])
        ).fetchone()

        if item and item["quantity"] > 1:
            con.execute(
                "UPDATE cart_items SET quantity = quantity - 1 WHERE id = ? AND user_id = ?",
                (cart_item_id, session["user_id"])
            )
        else:
            con.execute(
                "DELETE FROM cart_items WHERE id = ? AND user_id = ?",
                (cart_item_id, session["user_id"])
            )

    con.commit()
    con.close()

    return redirect(url_for("cart"))

@app.route("/checkout")
def checkout():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    items = con.execute(
        """SELECT cart_items.id AS cart_item_id, cart_items.quantity,
                  products.id AS product_id, products.name, products.price
           FROM cart_items
           JOIN products ON cart_items.product_id = products.id
           WHERE cart_items.user_id = ?""",
        (session["user_id"],)
    ).fetchall()
    con.close()

    total = 0
    for item in items:
        total += item["price"] * item["quantity"]

    return render_template("checkout.html", items=items, total=total)

@app.route("/checkout/confirm", methods=["POST"])
def confirm_order():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    items = con.execute(
        """SELECT cart_items.quantity, products.id AS product_id, products.price
           FROM cart_items
           JOIN products ON cart_items.product_id = products.id
           WHERE cart_items.user_id = ?""",
        (session["user_id"],)
    ).fetchall()

    total = 0
    for item in items:
        total += item["price"] * item["quantity"]

    cur = con.execute(
        "INSERT INTO orders (user_id, total) VALUES (?, ?)",
        (session["user_id"], total)
    )
    order_id = cur.lastrowid
    for item in items:
        con.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
            (order_id, item["product_id"], item["quantity"], item["price"])
        )
    con.execute("DELETE FROM cart_items WHERE user_id = ?", (session["user_id"],))
    con.commit()
    con.close()
    return redirect(url_for("index"))

@app.route("/admin/products")
def admin_products():
    if "user_id" not in session or session.get("is_admin") != 1:
        return redirect(url_for("index"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    products = con.execute("SELECT * FROM products").fetchall()
    con.close()

    return render_template("admin_products.html", products=products)

@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if "user_id" not in session or session.get("is_admin") != 1:
        return redirect(url_for("index"))

    con = sqlite3.connect("database.db")
    con.execute("DELETE FROM products WHERE id = ?", (product_id,))
    con.commit()
    con.close()

    return redirect(url_for("admin_products"))

@app.route("/admin/products/new")
def new_product_form():
    if "user_id" not in session or session.get("is_admin") != 1:
        return redirect(url_for("index"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    categories = con.execute("SELECT * FROM categories").fetchall()
    con.close()

    return render_template("admin_new_product.html", categories=categories)

@app.route("/admin/add_product",methods=["POST"])
def add_product():
    if "user_id" not in session or session.get("is_admin") != 1:
            return redirect(url_for("index"))
    name=request.form["name"]
    price=int(request.form["price"])
    brand=request.form["brand"]
    category_id = int(request.form["category_id"])
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    con.execute(
                "INSERT INTO products (name, price, brand, category_id) VALUES (?, ?, ?, ?)",
                (name, price, brand, category_id)
            )
    con.commit()
    con.close()
    return redirect(url_for("admin_products"))

@app.route("/admin/products/edit/<int:product_id>")
def edit_product_form(product_id):
    if "user_id" not in session or session.get("is_admin") != 1:
        return redirect(url_for("index"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    product = con.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    categories = con.execute("SELECT * FROM categories").fetchall()
    con.close()

    return render_template("admin_edit_product.html", product=product, categories=categories)

@app.route("/admin/products/update/<int:product_id>", methods=["POST"])
def update_product(product_id):
    if "user_id" not in session or session.get("is_admin") != 1:
        return redirect(url_for("index"))

    name = request.form["name"]
    brand = request.form["brand"]
    price = int(request.form["price"])
    category_id = int(request.form["category_id"])

    con = sqlite3.connect("database.db")
    con.execute(
        "UPDATE products SET name = ?, brand = ?, price = ?, category_id = ? WHERE id = ?",
        (name, brand, price, category_id, product_id)
    )
    con.commit()
    con.close()

    return redirect(url_for("admin_products"))

@app.route("/admin/users")
def admin_users():
    if "user_id" not in session or session.get("is_admin") != 1:
        return redirect(url_for("index"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    users = con.execute("SELECT * FROM users").fetchall()
    con.close()

    return render_template("admin_users.html", users=users)

@app.route("/admin/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if "user_id" not in session or session.get("is_admin") != 1:
        return redirect(url_for("index"))

    if user_id == session["user_id"]:
        return redirect(url_for("admin_users"))

    con = sqlite3.connect("database.db")
    con.execute("DELETE FROM users WHERE id = ?", (user_id,))
    con.commit()
    con.close()

    return redirect(url_for("admin_users"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/wishlist/toggle/<int:product_id>", methods=["POST"])
def toggle_wishlist(product_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    existing = con.execute(
        "SELECT * FROM wishlist_items WHERE user_id = ? AND product_id = ?",
        (session["user_id"], product_id)
    ).fetchone()

    if existing:
        con.execute(
            "DELETE FROM wishlist_items WHERE user_id = ? AND product_id = ?",
            (session["user_id"], product_id)
        )
    else:
        con.execute(
            "INSERT INTO wishlist_items (user_id, product_id) VALUES (?, ?)",
            (session["user_id"], product_id)
        )

    con.commit()
    con.close()

    return redirect(url_for("index"))

@app.route("/wishlist")
def wishlist():
    if "user_id" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    items = con.execute(
        """SELECT products.id, products.name, products.price, products.image
           FROM wishlist_items
           JOIN products ON wishlist_items.product_id = products.id
           WHERE wishlist_items.user_id = ?""",
        (session["user_id"],)
    ).fetchall()
    con.close()

    return render_template("wishlist.html", items=items)

if __name__ == "__main__":
    app.run(debug=True)