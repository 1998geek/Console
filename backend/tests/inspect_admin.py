import os
import sys

# 添加父目录到 path 以便读取 app 配置 (如果需要)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 加载环境变量
# 注意：在 Docker 容器中运行时，环境变量通常已经由 Docker 注入，
# 但如果有 .env 文件，load_dotenv 会尝试加载它。
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)

def check_admin():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ 错误: 未找到 DATABASE_URL 环境变量")
        return

    print(f"🔌 正在连接数据库...")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # 1. 检查表结构 (列出所有列名，防止字段猜错)
            print("\n📋 表结构 (users):")
            # 注意：information_schema 是标准 SQL，但具体实现可能略有不同。
            # 对于 PostgreSQL，这通常是有效的。
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"))
            columns = [row[0] for row in result]
            print(columns)

            # 2. 查询 admin 用户
            print("\n👤 查询 Admin 用户:")
            # 注意：这里假设表名是 users，字段包含 username
            query = text("SELECT * FROM users WHERE username = 'admin'")
            result = conn.execute(query)
            admin_user = result.fetchone()
            
            if admin_user:
                print("✅ 找到 Admin 账号!")
                # 将 Row 对象转换为字典打印
                # SQLAlchemy row._mapping 在较新版本可用
                try:
                    print(dict(admin_user._mapping))
                except AttributeError:
                    # 兼容旧版本 SQLAlchemy
                    print(dict(admin_user))
            else:
                print("⚠️ 未找到 username='admin' 的记录。")
                
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    check_admin()
