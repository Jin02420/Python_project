from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import get_db_connection

admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('is_admin'):
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('auth.login'))

    # Fetch data for the dashboard (e.g., user stats, orders, etc.)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', title='Admin Dashboard', users=users)

@admin_bp.route('/user-management')
def user_management():                                                                                                     
    if not session.get('is_admin'):
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('auth.login'))

    # Logic to view and manage users
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    conn.close()

    return render_template('user_management.html', title='User Management', users=users)

