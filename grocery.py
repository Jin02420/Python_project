from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection

grocery_bp = Blueprint('grocery', __name__, template_folder='templates')


@grocery_bp.route('/')
def grocery_list():
    """List all grocery items. Users can view items and add them to the cart. Admins can edit and delete items."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, quantity, category FROM grocery_items")
        items = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching grocery items: {e}", "danger")
        items = []
    finally:
        if conn:
            conn.close()

    is_admin = session.get('is_admin', False)
    return render_template('grocery_list.html', items=items, is_admin=is_admin)


@grocery_bp.route('/add', methods=['GET', 'POST'])
def add_grocery():
    """Admins can add new grocery items."""
    if not session.get('is_admin'):
        flash("You are not authorized to add items.", "danger")
        return redirect(url_for('grocery.grocery_list'))

    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        category = request.form.get('category')

        if not name or not quantity or not category:
            flash("All fields are required.", "warning")
            return render_template('grocery_add.html')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO grocery_items (name, quantity, category) VALUES (?, ?, ?)",
                (name, quantity, category)
            )
            conn.commit()
            flash("Grocery item added successfully!", "success")
        except Exception as e:
            flash(f"Error adding grocery item: {e}", "danger")
        finally:
            if conn:
                conn.close()

        return redirect(url_for('grocery.grocery_list'))
    return render_template('grocery_add.html')


@grocery_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_grocery(item_id):
    """Admins can edit grocery items."""
    if not session.get('is_admin'):
        flash("You are not authorized to edit items.", "danger")
        return redirect(url_for('grocery.grocery_list'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, quantity, category FROM grocery_items WHERE id = ?", (item_id,))
        item = cursor.fetchone()

        if not item:
            flash("Item not found!", "danger")
            return redirect(url_for('grocery.grocery_list'))

        if request.method == 'POST':
            name = request.form.get('name')
            quantity = request.form.get('quantity')
            category = request.form.get('category')

            if not name or not quantity or not category:
                flash("All fields are required.", "warning")
                return render_template('grocery_edit.html', item=item)

            cursor.execute(
                "UPDATE grocery_items SET name = ?, quantity = ?, category = ? WHERE id = ?",
                (name, quantity, category, item_id)
            )
            conn.commit()
            flash("Grocery item updated successfully!", "success")
            return redirect(url_for('grocery.grocery_list'))

    except Exception as e:
        flash(f"Error editing grocery item: {e}", "danger")
    finally:
        if conn:
            conn.close()

    return render_template('grocery_edit.html', item=item)


@grocery_bp.route('/delete/<int:item_id>', methods=['POST'])
def delete_grocery(item_id):
    """Admins can delete grocery items."""
    if not session.get('is_admin'):
        flash("You are not authorized to delete items.", "danger")
        return redirect(url_for('grocery.grocery_list'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM grocery_items WHERE id = ?", (item_id,))
        conn.commit()
        flash("Grocery item deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting grocery item: {e}", "danger")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('grocery.grocery_list'))


@grocery_bp.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    """Users can add items to their cart."""
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to add items to your cart.", "danger")
        return redirect(url_for('auth.login'))

    quantity = int(request.form.get('quantity', 1))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT quantity FROM grocery_items WHERE id = ?",
            (item_id,)
        )
        item = cursor.fetchone()

        if not item or item.quantity < quantity:
            flash("Not enough stock available.", "warning")
            return redirect(url_for('grocery.grocery_list'))

        cursor.execute(
            "INSERT INTO cart (user_id, item_id, quantity) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE quantity = quantity + ?",
            (user_id, item_id, quantity, quantity)
        )
        conn.commit()
        flash("Item added to cart successfully!", "success")
    except Exception as e:
        flash(f"Error adding to cart: {e}", "danger")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('grocery.grocery_list'))


@grocery_bp.route('/cart', methods=['GET', 'POST'])
def cart():
    """View and manage the cart."""
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your cart.", "danger")
        return redirect(url_for('auth.login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch items in the user's cart
        cursor.execute(
            "SELECT c.id, g.name, c.quantity, g.category FROM cart c JOIN grocery_items g ON c.item_id = g.id WHERE c.user_id = ?",
            (user_id,)
        )
        cart_items = cursor.fetchall()

    except Exception as e:
        flash(f"Error fetching cart: {e}", "danger")
        cart_items = []
    finally:
        if conn:
            conn.close()

    return render_template('cart.html', cart_items=cart_items)


@grocery_bp.route('/update_cart/<int:cart_id>', methods=['POST'])
def update_cart(cart_id):
    """Update the quantity of an item in the cart."""
    new_quantity = int(request.form.get('quantity', 1))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE cart SET quantity = ? WHERE id = ?", (new_quantity, cart_id))
        conn.commit()
        flash("Cart updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating cart: {e}", "danger")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('grocery.cart'))
