from flask import Blueprint, render_template, request, flash, redirect, url_for
from db import get_db_connection

search_bp = Blueprint('search', __name__)

# Route to display the search page
@search_bp.route('/search', methods=['GET', 'POST'])
def search_items():
    query = request.args.get('query')  # Get the query parameter from the URL
    results = []
    
    if query:
        # Perform the search if a query is provided
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT menu_item_id, name, description, price, image, category FROM menu_items WHERE name LIKE ?", ('%' + query + '%',))
        results = cursor.fetchall()
        conn.close()

    return render_template('search_results.html', results=results, query=query)

