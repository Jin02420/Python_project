from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
import re

auth_bp = Blueprint('auth', __name__, template_folder='templates')

# Password Regex for validation
password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Zaage\d]{8,}$'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check against the Users table in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password FROM Users WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            flash('You don\'t have an account. Please register first.', 'warning')
        elif check_password_hash(user[1], password):  # Verify password
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect(url_for('order_main'))  # Redirect to the orders page
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html', title='Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # Get plain password from the form

        # Password validation
        if not re.match(password_regex, password):
            flash('Password must be at least 8 characters long and contain at least one letter and one number.', 'danger')
            return redirect(url_for('auth.register'))

        # Hash the password after validation
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        # Check if the email already exists in the Users table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE email=?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('This email is already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

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
