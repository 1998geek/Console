import os
import sys
import urllib.parse
from sqlalchemy import create_engine, text

def list_remote_users():
    host = "c-cosmos-pg-comlan.yca6d4g7qznr6b.postgres.cosmos.azure.com"
    port = "5432"
    dbname = "citus"
    user = "citus"
    password = "!@#qwe123qwe"

    # 使用 URL 编码的密码
    encoded_password = urllib.parse.quote_plus(password)
    db_url = f"postgresql://{user}:{encoded_password}@{host}:{port}/{dbname}?sslmode=require"

    print(f"🔌 正在连接远程数据库: {host}...")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print("\n✅ 连接成功！")
            
            # 1. 检查 users 表的列
            print("🔍 检查 'users' 表结构:")
            try:
                # 使用 information_schema 查询列名
                cols_query = text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")
                cols_result = conn.execute(cols_query)
                columns = [row[0] for row in cols_result]
                print(f"列名: {columns}")
                
                if not columns:
                    print("⚠️ 未找到 'users' 表或该表没有列。")
                    # 列出所有表
                    print("\n📋 数据库中的所有表:")
                    tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                    for table in tables:
                        print(f" - {table[0]}")
                    return
                
                # 2. 根据存在的列构建查询
                # 至少应该有 username/email 和某种 password 字段
                select_cols = []
                # 常见字段名猜测
                possible_cols = ['id', 'username', 'name', 'email', 'password', 'hashed_password', 'is_active', 'is_admin', 'role', 'created_at']
                
                for col in possible_cols:
                    if col in columns:
                        select_cols.append(col)
                
                # 如果没有匹配到常用字段，就查所有 (只取前几行)
                if not select_cols:
                    print("⚠️ 未识别出常用字段，将查询所有列。")
                    query_str = "SELECT * FROM users"
                else:
                    query_str = f"SELECT {', '.join(select_cols)} FROM users"
                
                print(f"\n🚀 执行查询: {query_str}")
                result = conn.execute(text(query_str))
                users = result.fetchall()
                
                if users:
                    # 动态打印表头
                    header = " | ".join([f"{col:<15}" for col in select_cols]) if select_cols else "All Columns"
                    print("\n" + header)
                    print("-" * len(header))
                    
                    for row in users:
                        # 将 row 转换为字符串列表以便打印
                        row_str = " | ".join([str(val)[:15] + "..." if len(str(val)) > 15 else str(val).ljust(15) for val in row])
                        print(row_str)
                    print("-" * 100)
                    print(f"总计: {len(users)} 个用户")
                else:
                    print("⚠️ 表中没有数据。")

            except Exception as e:
                print(f"❌ 查询过程中出错: {e}")

    except Exception as e:
        print(f"❌ 连接失败: {e}")

if __name__ == "__main__":
    list_remote_users()
