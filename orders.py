from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection

orders_bp = Blueprint('orders', __name__, template_folder='templates')

orders_bp = Blueprint('orders', __name__, template_folder='templates')

@orders_bp.route('/', methods=['GET'])
def order_main():
    """Main orders page."""
  
    return render_template('order_main.html')

@orders_bp.route('/', methods=['GET'])
def orders():
    """Display all orders for the logged-in user."""
    if 'user_id' not in session:
        flash('Please log in to view your orders.', 'warning')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Orders WHERE user_id = ?", (user_id,))
    user_orders = cursor.fetchall()
    conn.close()
    
    return render_template('orders.html', title="Orders", orders=user_orders)

@orders_bp.route('/add', methods=['GET', 'POST'])
def add_order():
    """Add a new order."""
    if 'user_id' not in session:
        flash('Please log in to place an order.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        user_id = session['user_id']
        order_date = request.form['order_date']
        total_price = request.form['total_price']
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Orders (user_id, order_date, total_price, status) VALUES (?, ?, ?, ?)",
                (user_id, order_date, total_price, status)
            )
            conn.commit()
            flash('Order placed successfully!', 'success')
            return redirect(url_for('orders.orders'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
        finally:
            conn.close()

    return render_template('add_order.html', title="Place Order")

@orders_bp.route('/edit/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    """Edit an existing order."""
    if 'user_id' not in session:
        flash('Please log in to edit orders.', 'warning')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Orders WHERE order_id = ?", (order_id,))
    order = cursor.fetchone()

    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('orders.orders'))

    if request.method == 'POST':
        total_price = request.form['total_price']
        status = request.form['status']
        try:
            cursor.execute(
                "UPDATE Orders SET total_price = ?, status = ? WHERE order_id = ?",
                (total_price, status, order_id)
            )
            conn.commit()
            flash('Order updated successfully!', 'success')
            return redirect(url_for('orders.orders'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
        finally:
            conn.close()

    conn.close()
    return render_template('edit_order.html', title="Edit Order", order=order)

@orders_bp.route('/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    """Delete an order."""
    if 'user_id' not in session:
        flash('Please log in to delete orders.', 'warning')
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Orders WHERE order_id = ?", (order_id,))
        conn.commit()
        flash('Order deleted successfully!', 'success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
    finally:
        conn.close()

    return redirect(url_for('orders.order_main'))
