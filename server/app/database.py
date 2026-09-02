import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.pool = None

    def connect(self):
        # Railway PostgreSQL manzili
        database_url = os.environ.get("DATABASE_URL")
        
        if not database_url:
            # Agar DATABASE_URL bo'lmasa, alohida parametrlardan yig'amiz
            host = os.environ.get("PGHOST", "localhost")
            port = os.environ.get("PGPORT", "5432")
            dbname = os.environ.get("PGDATABASE", "pos_db")
            user = os.environ.get("PGUSER", "postgres")
            password = os.environ.get("PGPASSWORD", "postgres123")
            database_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        
        print(f"🔍 Ulanish: {database_url.replace(password, '****') if password else database_url}")
        
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
