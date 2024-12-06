from flask import Flask, redirect, url_for, session, flash
from flask_mail import Mail, Message
from auth import auth_bp
from recipes import recipes_bp
from orders import orders_bp
from config import Config
from admin import admin_bp
from search import search_bp
from myaccount import profile_bp
from db import init_db
from cart import cart_bp

app = Flask(__name__)  # Initialize Flask app here

# Configuration for the Flask app
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'mysecret_key_hetvi_1901'  # Set a unique secret key
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # For profile picture uploads

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your mail server (Gmail in this case)
app.config['MAIL_PORT'] = 465  # Port for SSL
app.config['MAIL_USE_SSL'] = True  # Use SSL
app.config['MAIL_USERNAME'] = 'hetvisoni1901@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'Hetvi@1901'  # Your email password (consider using environment variables)
app.config['MAIL_DEFAULT_SENDER'] = 'hetvisoni1901@gmail.com'  # Default sender for all emails
app.config['MAIL_MAX_EMAILS'] = None  # No limit on the number of emails
app.config['MAIL_ASCII_ATTACHMENTS'] = False  # Allow non-ASCII attachments

# Initialize Flask-Mail
mail = Mail(app)

# Verify database connection
try:
    init_db()
except Exception as e:
    print(f"Error during database initialization: {e}")
    raise

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(recipes_bp, url_prefix='/recipes')
app.register_blueprint(orders_bp, url_prefix='/orders')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(profile_bp, url_prefix='/myaccount')
app.register_blueprint(cart_bp, url_prefix='/cart')

# Default route for home
@app.route('/')
def home():
    return redirect(url_for('orders.order_main'))  # Redirect to the order page directly

# Route to the main orders page
@app.route('/orders')
def order_main():
    """Main orders page."""
    if 'user_id' not in session:
        flash('Please log in to view the menu and place orders.', 'warning')
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in
    return redirect(url_for('orders.order_main'))  # Redirect to the menu page if logged in

# Route to send a test email
@app.route('/send_email')
def send_email():
    msg = Message("Your Order Confirmation", recipients=["user_email@example.com"])
    msg.body = "Thank you for your order. Your order is being processed!"
    msg.html = "<h1>Thank you for your order!</h1><p>Your order is being processed.</p>"

    try:
        mail.send(msg)
        return "Email sent successfully"
    except Exception as e:
        return f"Error sending email: {e}"

if __name__ == '__main__':
    app.run(debug=True)
