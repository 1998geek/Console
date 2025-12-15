import psycopg2
import streamlit as st
from app_config.keys_config import (
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_NAME,
    DATABASE_USER,
    DATABASE_PASSWORD,
)


class DatabaseManager:
    # 数据库连接配置
    DB_CONFIG = {
        "host": DATABASE_HOST,
        "port": DATABASE_PORT,
        "database": DATABASE_NAME,
        "user": DATABASE_USER,
        "password": DATABASE_PASSWORD,
    }

    def __init__(self):
        self.config = self.DB_CONFIG

    def get_connection(self):
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except Exception as e:
            st.error(f"数据库连接失败: {str(e)}")
            return None

    def init_db(self):
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                # 检查 email 列是否存在
                cur.execute(
                    """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'email'
                """
                )
                email_exists = cur.fetchone() is not None

                if not email_exists:
                    # 添加 email 列
                    cur.execute("ALTER TABLE users ADD COLUMN email VARCHAR(100)")
                    conn.commit()

                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(256) NOT NULL,
                        email VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                conn.commit()
            finally:
                cur.close()
                conn.close()

    def register_user(self, username, hashed_password):
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, hashed_password),
                )
                conn.commit()
                return True
            except Exception as e:
                st.error(f"注册失败: {str(e)}")
                return False
            finally:
                cur.close()
                conn.close()

    def verify_user(self, username, hashed_password):
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT * FROM users WHERE username = %s AND password = %s",
                    (username, hashed_password),
                )
                user = cur.fetchone()
                return user is not None
            except Exception as e:
                st.error(f"登录失败: {str(e)}")
                return False
            finally:
                cur.close()
                conn.close()

    def get_all_users(self):
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT username, email, created_at FROM users")
                columns = [desc[0] for desc in cur.description]
                results = []
                for row in cur.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            finally:
                cur.close()
                conn.close()
        return []

    def delete_user(self, username):
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM users WHERE username = %s", (username,))
                conn.commit()
                return True
            except Exception as e:
                st.error(f"删除用户失败: {str(e)}")
                return False
            finally:
                cur.close()
                conn.close()
        return False

    def add_user(self, username, password, email):
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                    (username, password, email),
                )
                conn.commit()
                return True
            except Exception as e:
                st.error(f"添加用户失败: {str(e)}")
                return False
            finally:
                cur.close()
                conn.close()
        return False
