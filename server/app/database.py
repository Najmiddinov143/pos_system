import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.pool = None

    def connect(self):
        # Railway da DATABASE_URL dan ulanish
        database_url = os.environ.get("DATABASE_URL")
        
        if not database_url:
            print("❌ DATABASE_URL topilmadi!")
            exit(1)
        
        print(f"🔍 Ulanish: {database_url[:50]}...")
        
        self.pool = psycopg2.pool.SimpleConnectionPool(
            1, 10, dsn=database_url
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
