import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.pool = None

    def connect(self):
        # MUHIM: Railway da DATABASE_URL ni ishlatish kerak!
        database_url = os.environ.get("DATABASE_URL")
        
        print(f"🔍 DATABASE_URL mavjud: {database_url is not None}")
        if database_url:
            print("✅ DATABASE_URL dan ulanish...")
            self.pool = psycopg2.pool.SimpleConnectionPool(
                1, 10, dsn=database_url
            )
        else:
            print("⚠️ Localhost ga ulanish...")
            self.pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME", "pos_db"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "postgres123")
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
