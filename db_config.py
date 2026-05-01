"""
FoodBridge - Database Configuration & Connection Pooling
Uses pymysql with DBUtils for connection pooling.
"""
import os
import pymysql
from dbutils.pooled_db import PooledDB

# ── MySQL Connection Settings ──────────────────────────────
DB_CONFIG = {
    'host':     os.environ.get('MYSQLHOST') or os.environ.get('MYSQL_HOST', 'localhost'),
    'port':     int(os.environ.get('MYSQLPORT') or os.environ.get('MYSQL_PORT', 3306)),
    'user':     os.environ.get('MYSQLUSER') or os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQLPASSWORD') or os.environ.get('MYSQL_ROOT_PASSWORD', 'root'),
    'database': os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DATABASE', 'foodbridge'),
    'charset':  'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# ── Connection Pool ────────────────────────────────────────
pool = PooledDB(
    creator=pymysql,
    maxconnections=20,
    mincached=0,
    maxcached=5,
    blocking=True,
    **DB_CONFIG
)

def get_connection():
    """Get a connection from the pool."""
    return pool.connection()
