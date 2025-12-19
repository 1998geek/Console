import requests
import streamlit as st
import os

# 获取后端地址
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")

def _get_headers():
    """获取带 Token 的请求头"""
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

# === 认证相关 API ===

def login_request(username, password):
    """登录获取 Token"""
    url = f"{BACKEND_URL}/api/v1/auth/token"
    # FastAPI OAuth2PasswordRequestForm requires form data
    payload = {"username": username, "password": password}
    try:
        response = requests.post(url, data=payload, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"连接后端失败: {e}")
        return None

def get_current_user_info(token):
    """
    获取用户信息 (占位符，防止 login.py 报错)
    如果后端没有实现 /users/me 接口，这里直接返回空字典即可，不影响登录
    """
    return {} 
    
    # 待后端实现 /users/me 后，可启用以下代码：
    # url = f"{BACKEND_URL}/api/v1/users/me"
    # headers = {"Authorization": f"Bearer {token}"}
    # try:
    #     response = requests.get(url, headers=headers, timeout=5)
    #     if response.status_code == 200:
    #         return response.json()
    #     return None
    # except:
    #     return None

# === 翻译相关 API ===

def upload_file_for_translation(file_obj, target_language):
    """
    上传文件并启动翻译任务
    Returns: task_id (str) or None
    """
    url = f"{BACKEND_URL}/api/v1/translate/upload"
    headers = _get_headers()
    
    # 准备 Multipart/form-data
    files = {"file": (file_obj.name, file_obj, file_obj.type)}
    data = {"language": target_language}
    
    try:
        # requests 自动处理 Content-Type
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            return response.json().get("task_id")
        else:
            st.error(f"上传失败: {response.text}")
            return None
    except Exception as e:
        st.error(f"请求异常: {e}")
        return None

def get_translation_status(task_id):
    """
    查询任务进度
    Returns: dict (progress, message, status, download_url)
    """
    url = f"{BACKEND_URL}/api/v1/translate/status/{task_id}"
    headers = _get_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None
