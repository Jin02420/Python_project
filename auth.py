from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
import re

auth_bp = Blueprint('auth', __name__, template_folder='templates')
ADMIN_EMAIL = "bigdata@gmail.com"
ADMIN_PASSWORD_HASH = generate_password_hash("9696")  # This can be stored securely



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if the login is for the admin
        conn = get_db_connection()
        cursor = conn.cursor()
        if email == ADMIN_EMAIL and check_password_hash(ADMIN_PASSWORD_HASH, password):
            # Insert admin details into the database if not already present
            cursor.execute("SELECT * FROM Users WHERE email=?", (ADMIN_EMAIL,))
            admin_record = cursor.fetchone()
            if not admin_record:
                try:
                    cursor.execute(
                        "INSERT INTO Users (name, email, role) VALUES (?, ?, ?)",
                        ("Admin", ADMIN_EMAIL, "Admin")
                    )
                    conn.commit()
                except Exception as e:
                    flash(f"Error adding admin to the database: {str(e)}", 'danger')

            session['user_id'] = "admin"  # Mark the user as admin
            session['is_admin'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        
        # If not admin, check against the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password FROM Users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            flash('You don\'t have an account. Please register first.', 'warning')
        elif user and check_password_hash(user[1], password):  # Verify password
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect(url_for('orders.order_main'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html', title='Login')


# Password Regex for validation
password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # Get plain password from the form
        
        
        # Hash the password after validation
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert user into the database
            cursor.execute("INSERT INTO Users (name, email, password) VALUES (?, ?, ?)", (name, email, password_hash))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'An error occurred while registering: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return render_template('register.html', title='Register')


@auth_bp.route('/logout')
def logout():
    """Log out the user."""
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


