from db import get_db_connection

# Example function for adding a user
def add_user(name, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    conn.close()

# Example function for fetching recipes
def get_recipes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipes")
    recipes = cursor.fetchall()
    conn.close()
    return recipes
