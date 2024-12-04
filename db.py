import pyodbc

# Database connection settings
DATABASE_CONFIG = {
    'server': 'LAPTOP-JN4FC3RI',
    'database': 'FoodCartDB',
    'driver': '{ODBC Driver 17 for SQL Server}',
    'trusted_connection': "yes"  # Adjust if needed
}

def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = pyodbc.connect(
            f'DRIVER={DATABASE_CONFIG["driver"]};'
            f'SERVER={DATABASE_CONFIG["server"]};'
            f'DATABASE={DATABASE_CONFIG["database"]};'
            f'TRUSTED_CONNECTION={DATABASE_CONFIG["trusted_connection"]};'
        )
        return conn
    except pyodbc.Error as e:
        print("Error while connecting to the database:", e)
        return None

def fetch_data(query, params=None):
    """Fetch data from the database."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return results
        except pyodbc.Error as e:
            print("Error executing query:", e)
            return None
        finally:
            cursor.close()
            conn.close()
    return None

def execute_query(query, params=None):
    """Execute an insert, update, or delete query."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return True
        except pyodbc.Error as e:
            print("Error executing query:", e)
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def init_db():
    """Verify the database connection (tables must already be created in SSMS)."""
    conn = get_db_connection()
    if conn:
        print("Database connection successful.")
        conn.close()
    else:
        print("Database connection failed.")
        
def fetch_groceries_by_store(store):
    """Fetch groceries for a specific store."""
    query = "SELECT id, name, quantity, category FROM grocery_items WHERE store = ?"
    return fetch_data(query, (store,))



