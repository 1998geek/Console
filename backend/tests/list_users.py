import os
import sys

# 添加父目录到 path 以便读取 app 配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)

def list_users():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ 错误: 未找到 DATABASE_URL 环境变量")
        return

    print(f"🔌 正在连接数据库: {db_url}")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print("\n👥 用户列表:")
            query = text("SELECT id, username, email, is_active, is_admin, hashed_password FROM users")
            result = conn.execute(query)
            users = result.fetchall()
            
            if users:
                print(f"{'ID':<5} {'Username':<15} {'Email':<25} {'Active':<8} {'Admin':<8} {'Hashed Password (Prefix)'}")
                print("-" * 100)
                for user in users:
                    # Convert row to dict-like access for safety if needed, or just use index
                    uid = user[0]
                    username = user[1]
                    email = user[2]
                    is_active = user[3]
                    is_admin = user[4]
                    hashed_pw = user[5]
                    
                    # Truncate hash for display to keep it clean, but show enough to verify
                    hash_display = hashed_pw[:30] + "..." if hashed_pw else "None"
                    
                    print(f"{uid:<5} {username:<15} {email:<25} {str(is_active):<8} {str(is_admin):<8} {hash_display}")
                print("-" * 100)
                print(f"总计: {len(users)} 个用户")
            else:
                print("⚠️ 数据库中没有找到任何用户。")
                
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    list_users()
