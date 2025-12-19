import psycopg2
import hashlib
from app.core.config import settings

class DatabaseManager:
    def __init__(self):
        self.config = {
            "host": settings.DATABASE_HOST,
            "port": settings.DATABASE_PORT,
            "database": settings.DATABASE_NAME,
            "user": settings.DATABASE_USER,
            "password": settings.DATABASE_PASSWORD,
        }

    def get_connection(self):
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except Exception as e:
            print(f"Database connection failed: {str(e)}")
            return None

    def verify_user(self, username, input_password):
        """
        验证用户逻辑（兼容明文密码和 SHA256 哈希密码）
        """
        conn = self.get_connection()
        if not conn:
            return False
            
        try:
            cur = conn.cursor()
            # 1. 只根据用户名查询 stored_password
            # 注意：这里假设你的表里密码字段叫 'password'，如果叫别的请自行修改
            cur.execute(
                "SELECT password FROM users WHERE username = %s",
                (username,)
            )
            result = cur.fetchone()
            
            if not result:
                return False # 用户不存在
                
            stored_password = result[0] # 获取数据库里的密码字符串

            # 2. 验证逻辑 A: 尝试明文直接匹配 (针对老数据)
            if input_password == stored_password:
                return True

            # 3. 验证逻辑 B: 尝试 SHA256 哈希匹配 (针对新数据)
            input_hashed = hashlib.sha256(input_password.encode()).hexdigest()
            if input_hashed == stored_password:
                return True
                
            return False

        except Exception as e:
            print(f"Login verification failed: {str(e)}")
            return False
        finally:
            if cur: cur.close()
            conn.close()
