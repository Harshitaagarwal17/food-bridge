"""
FoodBridge - Database Configuration & Connection Pooling
Uses pymysql with DBUtils for connection pooling.
"""
import os
import pymysql
from dbutils.pooled_db import PooledDB

# ── MySQL Connection Settings ──────────────────────────────
DB_CONFIG = {
    'host':     os.environ.get('MYSQLHOST', 'localhost'),
    'port':     int(os.environ.get('MYSQLPORT', 3306)),
    'user':     os.environ.get('MYSQLUSER', 'root'),
    'password': os.environ.get('MYSQLPASSWORD', 'root'),
    'database': os.environ.get('MYSQLDATABASE', 'foodbridge'),
    'charset':  'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# ── Connection Pool ────────────────────────────────────────
pool = PooledDB(
    creator=pymysql,
    maxconnections=20,
    mincached=2,
    maxcached=5,
    blocking=True,
    **DB_CONFIG
)

def get_connection():
    """Get a connection from the pool."""
    return pool.connection()
