from flask import Blueprint, render_template, session

profile_bp = Blueprint('myaccount', __name__, template_folder='templates')

@profile_bp.route('/myaccount')
def view_profile():
    if 'user_id' not in session:
        return render_template('myaccount.html', user_id=session['user_id'])
