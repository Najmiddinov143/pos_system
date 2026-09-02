import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from .config import config

class Database:
    def __init__(self):
        self.pool = None
    
    def connect(self):
        self.pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        return self
    
    @contextmanager
    def get_connection(self):
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                yield cursor
    
    def execute_query(self, query, params=None):
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def execute_one(self, query, params=None):
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    
    def execute_insert(self, query, params=None):
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()[0]
    
    def execute_update(self, query, params=None):
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.rowcount

db = Database().connect()