# Mobile Store

#### Video Demo: https://youtu.be/hOmhHP-dgMs

Mobile Store is a web application that allows users to browse products and purchase them online. Registered users can add items to their cart, adjust quantities, and complete checkout. The application also includes an admin panel where administrators can manage the product catalog (add, edit, and delete products) and manage registered users, including the ability to delete user accounts.
I built this as my final project for CS50x because web applications are a complete way to apply everything I learned throughout the course — from Python and SQL to HTML, CSS, and web development fundamentals.

## Features

- User registration and login with secure password hashing
- Browse and purchase products
- View detailed information for each product
- Shopping cart with the ability to adjust quantities and remove items
- Checkout process that creates an order and clears the cart
- Wishlist feature to save favorite products for later
- About and Contact pages
- Custom 404 error page for invalid product links
- Duplicate email prevention during registration
- Admin panel for managing products (add, edit, delete) and users (view, delete)

## Technologies Used

- Python for the backend
- Flask for the web framework
- SQLite3 for the database
- HTML and CSS for the frontend
- Bootstrap Icons for UI icons

## Installation

1. Clone this repository or download the project files

2. Navigate to the project folder:

```
   cd mobile-store
```

3. Create a virtual environment:

```
   python -m venv venv
```

4. Activate the virtual environment:

   On Windows:

```
   venv\Scripts\Activate.ps1
```

On macOS/Linux:

```
   source venv/bin/activate
```

5. Install the required packages:

```
   pip install -r requirements.txt
```

6. Create and seed the database:

```
   python init_db.py
```

7. Run the application:

```
   python app.py
```

8. Open your browser and go to:

```
   http://127.0.0.1:5000
```

### Admin Access

An admin account is created automatically when you run `init_db.py`:

- Email: admin@example.com
- Password: admin123

## Design Decisions

**Normalized database structure:** Instead of storing all information in a single table, the database is split into seven related tables (`users`,`categories`, `products`, `cart_items`, `wishlist_items`, `orders`,`order_items`).
This design means that when something needs to change, I only need to update one place instead of modifying data across the entire database. For example, if a category name changes, it only needs to be updated once in the `categories` table, and every product referencing it automatically reflects the change.

**Storing price history in orders:** The `order_items` table stores the price of each product at the time of purchase, separately from the
`products` table. This is intentional: if a product's price changes later, past orders should still reflect the price the customer actually paid, not the current price.

**Password hashing:** User passwords are never stored as plain text.
Instead, they are hashed using Werkzeug's `generate_password_hash` before being saved to the database. This means that even if someone gained unauthorized access to the database, they would not be able to see or recover users' actual passwords, protecting user accounts.

**Preventing duplicate cart entries:** When a user clicks "Add to Cart" for a product they already have in their cart, the application increases the `quantity` of the existing row instead of creating a new one. Without this check, adding the same product multiple times would create several separate rows in `cart_items` for the same product, making it harder to display an accurate quantity and total price, and cluttering the cart with duplicate entries.

**Separate layout for the admin panel:** The admin panel uses its own
base template (`admin_base.html`) instead of extending the main site's
layout (`base.html`). The admin panel is a completely different context from the storefront — it doesn't need a search bar, shopping cart icon, or category dropdown. Giving it a dedicated sidebar layout keeps the interface focused on admin tasks and avoids confusing customer-facing elements with management tools.

## Challenges

**Handling duplicate items in the cart:** One of the trickier problems was making sure that clicking "Add to Cart" multiple times for the same product didn't create duplicate rows in the `cart_items` table. Initially, every click created a new row with `quantity = 1`, so the same product could appear several times in the cart instead of showing a single entry with an updated quantity. I solved this by first checking whether a row already existed for that user and product combination — if it did, I updated the existing `quantity` instead of inserting a new row.

**Managing user sessions and permissions:** Another challenge was figuring out how the application could reliably know which user was logged in, and what that user was allowed to do, across different pages. Since HTTP requests don't retain memory between page loads, I used Flask's `session` to store the logged-in user's ID after login. I then used this session data to determine ownership of cart items and orders (so users could only modify their own data) and to restrict admin-only routes to users with `is_admin` equal to 1, redirecting anyone else back to the homepage.

## Future Improvements

- Add product filtering (by brand, price range, and category) on the homepage
- Make category links functional, so clicking a category shows only products
  from that category on a dedicated page
- Add a "Best Sellers" section based on order history
- Add support for discounts and sale prices on products
- Integrate a real payment gateway (such as Stripe in test mode) instead of
  the current demo checkout
- Add a working search bar that actually queries the database by product
  name or brand

## File Structure

```
mobile-store/
├── app.py                    # Main Flask application with all routes
├── schema.sql                # Database schema (table definitions)
├── init_db.py                # Script to create and seed the database
├── database.db               # SQLite database file
├── templates/
│   ├── base.html                  # Main site layout (navbar, footer)
│   ├── auth_base.html             # Layout for login/register pages
│   ├── admin_base.html            # Layout for admin panel
│   ├── index.html                 # Homepage with product listing
│   ├── product.html               # Product detail page
│   ├── cart.html                  # Shopping cart page
│   ├── checkout.html              # Checkout page
│   ├── login.html                 # Login form
│   ├── register.html              # Registration form
│   ├── admin_products.html        # Admin product list
│   ├── admin_new_product.html     # Add product form
│   ├── admin_edit_product.html    # Edit product form
│   ├── admin_users.html           # Admin user list
│   ├── wishlist.html              # User's wishlist page
│   ├── about.html                 # About us page
│   ├── contact.html               # Contact form page
│   └── 404.html                   # Custom not-found error page
└── static/
    ├── css/
    │   └── style.css              # All site styling
    └── img/
        └── logo.svg               # Site logo
```
