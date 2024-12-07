import pyodbc

# Database connection settings
DATABASE_CONFIG = {
    'server': 'LAPTOP-JN4FC3RI',
    'database': 'FoodCartDB',
    'driver': '{ODBC Driver 17 for SQL Server}',
    'trusted_connection': 'yes'  # Adjust if needed
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

# Fetch all menu items from the database
def fetch_menu_items():
    """Fetch menu items for displaying in the menu."""
    query = "SELECT item_id, name, price FROM Menu_Items"
    return fetch_data(query)

# Fetch an individual menu item by ID
def fetch_menu_item_by_id(item_id):
    """Fetch a specific menu item by its ID."""
    query = "SELECT item_id, name, price FROM Menu_Items WHERE item_id = ?"
    return fetch_data(query, (item_id,))

# Create a new order and return the order ID
def create_order(total_amount):
    """Create a new order and return the order ID."""
    query = "INSERT INTO Orders (total_amount) VALUES (?)"
    success = execute_query(query, (total_amount,))
    if success:
        # Get the last inserted order ID (to add items to Order_Items)
        query = "SELECT SCOPE_IDENTITY()"
        result = fetch_data(query)
        return result[0][0] if result else None
    return None

# Add items to the Order_Items table
def add_order_items(order_id, cart):
    """Insert order items into the Order_Items table."""
    for item_id, item in cart.items():
        query = """
        INSERT INTO Order_Items (order_id, item_name, quantity, price) 
        VALUES (?, ?, ?, ?)
        """
        success = execute_query(query, (order_id, item['name'], item['quantity'], item['price']))
        if not success:
            print(f"Failed to insert order item {item['name']}")
            return False
    return True

# Fetch the cart items for the checkout process
def fetch_cart_items(cart):
    """Fetch the details of items in the cart from the database."""
    cart_items = []
    for item_id, item_data in cart.items():
        item = fetch_menu_item_by_id(item_id)
        if item:
            cart_items.append(item[0])
    return cart_items
