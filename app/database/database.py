import psycopg2
from psycopg2 import Error
from psycopg2.extras import DictCursor
import os
import json

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'database': os.getenv('DB_NAME', 'threed_db')
}

def create_database():
    try:
        # 连接到默认的postgres数据库
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_CONFIG['database']}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print("Database created successfully")
            
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        if 'conn' in locals():
            if 'cursor' in locals():
                cursor.close()
            conn.close()

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            cursor_factory=DictCursor
        )
        print("Database connected successfully")
        return connection
    except Error as e:
        print(f"Error connecting to PostgreSQL Database: {e}")
        return None

def check_tables_exist():
    """检查必要的表是否存在"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            )
        """)
        users_exists = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'user_data'
            )
        """)
        user_data_exists = cursor.fetchone()[0]
        
        return users_exists and user_data_exists
    except Error as e:
        print(f"Error checking tables: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def init_db():
    """初始化数据库表"""
    # 创建数据库
    create_database()
    
    # 如果表已存在，则不需要初始化
    if check_tables_exist():
        print("Database tables already exist")
        return
        
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    hashed_password VARCHAR(100) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建用户数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_data (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    content JSONB DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            connection.commit()
            print("Database tables created successfully")
            
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()

if __name__ == "__main__":
    init_db()