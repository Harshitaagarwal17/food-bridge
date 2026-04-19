"""
FoodBridge - Database Configuration & Connection Pooling
Uses pymysql with DBUtils for connection pooling.
"""

import pymysql
from dbutils.pooled_db import PooledDB

# ── MySQL Connection Settings ──────────────────────────────
DB_CONFIG = {
    'host':       'localhost',
    'port':       3306,
    'user':       'root',
    'password':   'root',           # ← Put your MySQL root password here
    'database':   'foodbridge',
    'charset':    'utf8mb4',
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
