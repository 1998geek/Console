import requests
import sys

# 后端 API 地址 (容器内可以直接用 http://backend:8000，但在宿主机上需要用 localhost:8000)
# 假设你在本地运行测试脚本，映射端口是 8000
API_URL = "http://localhost:8000/api"

def test_login(username, password):
    print(f"🔄 尝试登录用户: {username} ...")
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ 登录成功! Token: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

if __name__ == "__main__":
    # 测试 admin / admin123456 (明文密码)
    print("--- 测试远程 Admin 账号 (明文密码) ---")
    token = test_login("admin", "admin123456")
    
    if not token:
        sys.exit(1)
