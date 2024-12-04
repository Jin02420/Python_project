
from flask import Flask,  redirect, url_for,session,flash,render_template



from auth import auth_bp
from grocery import grocery_bp
from recipes import recipes_bp
from orders import orders_bp
from config import Config
from admin import admin_bp
from search import search_bp 
from myaccount import profile_bp
from db import init_db
from cart import cart_bp
 

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure key in production
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # For profile picture uploads


# Verify database connection
try:
    init_db()
except Exception as e:
    print(f"Error during database initialization: {e}")
    raise
        

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(grocery_bp, url_prefix='/grocery')
app.register_blueprint(recipes_bp, url_prefix='/recipes')
app.register_blueprint(orders_bp, url_prefix='/orders')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(profile_bp, url_prefix='/myaccount')
app.register_blueprint(cart_bp, url_prefix='/cart')


# Default Route
@app.route('/')
def home():
    return redirect(url_for('orders.order_main'))

# @app.route('/orders')
# def order_main():
#     """Main orders page."""
#     if 'user_id' not in session:
#         flash('Please log in to access this page.', 'warning')
#         return redirect(url_for('auth.login'))
#     return render_template('orders.order_main.html', user_id=session.get('user_id'))

if __name__ == '__main__':
    app.run(debug=True)
