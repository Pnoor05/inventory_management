'''



import mysql.connector.pooling
from config import Config

class Database:
    _pool = None
    
    @classmethod
    def initialize(cls):
        if not cls._pool:
            cls._pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="inventory_pool",
                pool_size=5,
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=True
            )
    
    @classmethod
    def get_connection(cls):
        return cls._pool.get_connection()
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        conn = cls.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            return None
        finally:
            cursor.close()
            conn.close()

            '''

import mysql.connector.pooling
from config import Config

class Database:
    _pool = None
    
    @classmethod
    def initialize(cls):
        if not cls._pool:
            cls._pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="inventory_pool",
                pool_size=5,
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=True
            )
    
    @classmethod
    def get_connection(cls):
        return cls._pool.get_connection()
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        conn = cls.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            return None
        finally:
            cursor.close()
            conn.close()