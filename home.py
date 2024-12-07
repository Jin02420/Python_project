from flask import Blueprint, render_template, redirect, url_for, session, flash

# Create the blueprint for the home page
home_bp = Blueprint('home', __name__)

# Route to the homepage
@home_bp.route('/')
def home_page():
    """The homepage of the application."""
    # Check if the user is logged in
    if 'user_id' not in session:
        # If not logged in, display a flash message and redirect to the login page
        flash('You must be logged in to access the homepage.', 'warning')
        return redirect(url_for('auth.login'))  # Redirect to the login page

    # Otherwise, display the home page (You can add logic to fetch user info if needed)
    user_name = session.get('user_name', 'Guest')  # Get the username from session (if available)
    return render_template('order_main_dashboard.html', user_name=user_name)  # Render the home page template
