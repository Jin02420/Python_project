import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')  # Set your secret key
    DB_SERVER = 'LAPTOP-JN4FC3RI'  # Replace with your server name
    DB_NAME = 'grocery_app'        # Database name
    CONNECTION_STRING = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes;"
