from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from flask_mail import Message, Mail
import smtplib
orders_bp = Blueprint('orders', __name__, template_folder='templates')
mail = Mail()

# Route to display the main dashboard page
@orders_bp.route('/orders', methods=['GET', 'POST'])
def order_main():
    """Main dashboard page where logged-in users can access menu and other options."""
    if 'user_id' not in session:
        # If the user is not logged in, display a prompt to log in
        flash('You must be logged in to place an order. Please log in.', 'warning')
        return redirect(url_for('auth.login'))  # Redirect to login page

    # Welcome message
    user_name = session.get('user_name', 'Guest')  # Get the username from session (if available)

    return render_template('order_main_dashboard.html', user_name=user_name)


@orders_bp.route('/menu', methods=['GET'])
def menu():
    query = request.args.get('query')  # Get the search query from URL if any
    conn = get_db_connection()
    cursor = conn.cursor()

    if query:
        # If query exists, search for menu items matching the query
        cursor.execute("SELECT menu_item_id, name, description, price, image, category FROM menu_items WHERE name LIKE ?", ('%' + query + '%',))
    else:
        # If no query, fetch all menu items
        cursor.execute("SELECT menu_item_id, name, description, price, image, category FROM menu_items")

    menu_items = cursor.fetchall()  # Fetch the results
    conn.close()

    # Render the template with the menu items and query (if any)
    return render_template('menu_item.html', menu_items=menu_items, query=query)


@orders_bp.route('/add_to_cart/<int:item_id>', methods=['GET', 'POST'])
def add_to_cart(item_id):
    print('add to cart',item_id)
    item_id = str(item_id)
    # Check if user is logged in
    if 'user_id' not in session:
        flash('You need to be logged in to add items to the cart.', 'danger')
        return redirect(url_for('auth.login'))  # Redirect to login page
    
    # Fetch the item from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT menu_item_id, name, price FROM menu_items WHERE menu_item_id=?", (item_id,))
    item = cursor.fetchone()
    conn.close()

    if item:
        # Get the quantity from the form, default to 1 if not provided
        quantity = int(request.form.get('quantity', 1))
        
        # Add the item to the user's cart (stored in session for simplicity)
        cart = session.get('cart', {})
        print('cart0', cart)

        # Ensure the item_id is stored as an integer in the cart
        if item_id in cart:
            cart[item_id]['quantity'] += quantity
        else:
            # Store item_id as integer and create a cart entry
            cart[item_id] = {'name': item[1], 'price': float(item[2]), 'quantity': quantity}
        
        print('carteee',cart)

        session['cart'] = cart  # Save cart to session
        flash(f'Added {item[1]} to your cart.', 'success')  # Correct use of numeric indexing for the name
        print('now returning')
        return redirect(url_for('orders.menu'))  # Redirect to the menu page

    flash('Item not found!', 'danger')
    return redirect(url_for('orders.menu'))  # If item not found, go back to the menu page



@orders_bp.route('/cart', methods=['GET'])
def cart():
    # Check if the cart exists in the session
    if 'cart' not in session:
        flash('Your cart is empty!', 'info')
        return redirect(url_for('orders.menu'))

    cart = session['cart']

    # Calculate the total amount by multiplying price and quantity, making sure price is a float
    total = sum(float(item['price']) * item['quantity'] for item in cart.values())

    # Render the cart template with the cart items and total amount
    return render_template('cart.html', cart=cart, total=total)

@orders_bp.route('/remove_item/<int:item_id>', methods=['GET'])
def remove_item(item_id):
    # Check if the cart exists in the session
    if 'cart' in session:
        cart = session['cart']
        print('cartIN',cart, item_id)
        # Check if the item exists in the cart
        if item_id in cart:
            del cart[item_id]  # Remove the item from the cart
            print('new cart',cart)
            session['cart'] = cart  # Update the session with the modified cart
            flash('Item removed from your cart.', 'success')
        else:
            flash('Item not found in your cart.', 'danger')
    else:
        flash('Your cart is empty.', 'info')
    
    return redirect(url_for('orders.cart'))  # Redirect back to the cart page


@orders_bp.route('/confirmation')
def confirmation():
    order_id = request.args.get('order_id')
    total_amount = request.args.get('total_amount')
    delivery_instructions = request.args.get('delivery_instructions')

    if not order_id:
        flash('Order not found!', 'danger')
        return redirect(url_for('orders.menu'))  # Redirect to menu if no order_id

    return render_template('order_confirmation.html', order_id=order_id, total_amount=total_amount, delivery_instructions=delivery_instructions)


@orders_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!', 'info')
        return redirect(url_for('orders.menu'))

    # Check if the user is logged in and the email exists in session
    if 'user_id' not in session:
        flash('You must be logged in to proceed to checkout.', 'warning')
        return redirect(url_for('auth.login'))  # Redirect to login if email not in session
    
    # Handle GET request to fetch user's email and show the checkout page
    if request.method == 'GET':
        user_id = session['user_id']

        # Fetch the user's email from the database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT email FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        print('user',user)
        conn.close()

        if user:
            email = user[0]  # Access the email as a dictionary
            session['email'] = email  # Store the email in session if not already done
        else:
            flash('Error retrieving user information.', 'danger')
            return redirect(url_for('auth.login'))  # Redirect if no user found

        # Render the checkout page with the user's email
        return render_template('checkout.html', email=email)
    
    # Handle POST request
    if request.method == 'POST':
        # Get the order details from the form
        address = request.form['address']
        instructions = request.form['delivery_instructions']
        email = session['email']  # Get the email from session
        
        cart = session['cart']
        total_amount = sum(float(item['price']) * item['quantity'] for item in cart.values())
        try:
            total_amount = float(total_amount) if total_amount else 0.0  # Default to 0.0 if empty
        except ValueError:
            total_amount = 0.0  # Default to 0.0 if conversion fails

        try:
            latitude = float(request.form['latitude']) if request.form['latitude'] else 0.0  # Default to 0.0 if empty
        except ValueError:
            latitude = 0.0  # Default to 0.0 if conversion fails

        try:
            longitude = float(request.form['longitude']) if request.form['longitude'] else 0.0  # Default to 0.0 if empty
        except ValueError:
            longitude = 0.0  # Default to 0.0 if conversion fails

        # Save the order to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create a new order and get the order_id using OUTPUT INSERTED.id
        cursor.execute("""
            INSERT INTO Orders (user_id, total_amount, address, email, delivery_instructions, latitude, longitude, status)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session['user_id'], total_amount, address, email, instructions, latitude, longitude, 'pending'))

        # Get the order ID of the newly created order using OUTPUT INSERTED.id
        order_id = cursor.fetchone()[0]  # Fetch the first column of the result (which contains the order_id)
        conn.commit()

        # Add the order items to the Order_Items table
        for item_id, item in cart.items():
            cursor.execute("""
                INSERT INTO Order_Items (order_id, menu_item_id, quantity, price)
                VALUES (?, ?, ?, ?)
            """, (order_id, item_id, item['quantity'], item['price']))
        conn.commit()

        msg = Message("Your Order Confirmation", recipients=[email])
        msg.body = f"Thank you for your order! Your order ID is {order_id}. We are processing your order."
        msg.html = render_template('order_confirmation.html', order_id=order_id, total_amount=total_amount)

        try:
            # mail.send(msg)
            flash('Your order has been placed successfully! A confirmation email has been sent.', 'success')
        except Exception as e:
            flash(f"Error sending email: {e}", 'error')

        session.pop('cart', None)  # Clear the cart after successful order
        return redirect(url_for('orders.confirmation', order_id=order_id, total_amount=total_amount, delivery_instructions=instructions))
    
    return render_template('checkout.html')




# Function to send order confirmation email
def send_order_email(user_email, order_id):
    msg = Message('Order Confirmation',
                  sender='your_email@example.com',  # Your email here
                  recipients=[user_email])

    msg.body = f"Thank you for your order! Your order ID is {order_id}. You can track your order on our website."

    try:
        mail.send(msg)
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")
        

@orders_bp.route('/track_order/<int:order_id>', methods=['GET'])
def track_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM Order_Tracking WHERE order_id=?", (order_id,))
    tracking = cursor.fetchall()

    if tracking:
        status = tracking[-1][0]  # Get the latest status
    else:
        status = "No updates yet."

    return render_template('track_order.html', order_id=order_id, status=status)
