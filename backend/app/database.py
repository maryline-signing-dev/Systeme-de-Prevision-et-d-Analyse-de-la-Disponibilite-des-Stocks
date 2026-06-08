import mysql.connector
from mysql.connector import pooling

_pool = None

def init_pool(app):
    global _pool
    _pool = pooling.MySQLConnectionPool(
        pool_name="stock_pool",
        pool_size=5,
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

def get_connection():
    return _pool.get_connection()