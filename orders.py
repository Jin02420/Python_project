from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db_connection

orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/', methods=['GET'])
def order_main():
    # """Main orders page."""
    # if 'user_id' not in session:
    #     flash('Please log in or register to place an order.', 'warning')
    #     return redirect(url_for('auth.login'))

    # Fetch menu items from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM MenuItems")
    menu_items = cursor.fetchall()
    conn.close()
    print(menu_items)
    return render_template('order_main.html')


@orders_bp.route('/menu', methods=['GET'])
def view_menu():
    """View the menu page with items."""
    if 'user_id' not in session:
        flash('Please log in to view the menu.', 'warning')
        return redirect(url_for('auth.login'))

    # Fetch menu items from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM MenuItems")
    menu_items = cursor.fetchall()
    conn.close()

    return render_template('menu.html', menu_items=menu_items)

@orders_bp.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    """Add items to the cart."""
    if 'user_id' not in session:
        flash('You need to be logged in to add items to the cart.', 'warning')
        return redirect(url_for('auth.login'))

    # Get the quantity from the form
    quantity = int(request.form['quantity'])

    # Add item to the session cart
    if 'cart' not in session:
        session['cart'] = {}

    if item_id in session['cart']:
        session['cart'][item_id] += quantity
    else:
        session['cart'][item_id] = quantity

    session.modified = True
    flash('Item added to cart!', 'success')
    return redirect(url_for('orders.view_cart'))

@orders_bp.route('/cart', methods=['GET'])
def view_cart():
    """View the user's cart."""
    if 'user_id' not in session:
        flash('You need to be logged in to view the cart.', 'warning')
        return redirect(url_for('auth.login'))

    if 'cart' not in session or len(session['cart']) == 0:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('orders.order_main'))

    # Fetch cart items from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cart_items = []
    for item_id, quantity in session['cart'].items():
        cursor.execute("SELECT * FROM MenuItems WHERE id=?", (item_id,))
        item = cursor.fetchone()
        cart_items.append({'item': item, 'quantity': quantity})
    conn.close()

    return render_template('cart.html', cart_items=cart_items)

@orders_bp.route('/place_order', methods=['POST'])
def place_order():
    """Place the order."""
    if 'user_id' not in session:
        flash('You need to be logged in to place an order.', 'warning')
        return redirect(url_for('auth.login'))

    # Place order logic
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    total_price = 0
    for item_id, quantity in session['cart'].items():
        cursor.execute("SELECT price FROM MenuItems WHERE id=?", (item_id,))
        item = cursor.fetchone()
        total_price += item['price'] * quantity

    cursor.execute(
        "INSERT INTO Orders (user_id, total_price, status) VALUES (?, ?, ?)",
        (user_id, total_price, 'Pending')
    )
    conn.commit()
    order_id = cursor.lastrowid

    # Add order items
    for item_id, quantity in session['cart'].items():
        cursor.execute(
            "INSERT INTO OrderItems (order_id, item_id, quantity) VALUES (?, ?, ?)",
            (order_id, item_id, quantity)
        )
    conn.commit()
    session.pop('cart', None)  # Clear the cart after placing the order
    conn.close()

    flash('Your order has been placed successfully!', 'success')
    return redirect(url_for('orders.view_cart'))
