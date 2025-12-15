#!/usr/bin/env python3
"""
AIPortal API 测试脚本
演示如何使用 FastAPI 接口
"""
import requests
import json
from pprint import pprint

# API 基础 URL
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


def print_section(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_health_check():
    """测试健康检查"""
    print_section("1. 健康检查")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    pprint(response.json())
    return response.status_code == 200


def test_login():
    """测试登录"""
    print_section("2. 用户登录")
    response = requests.post(
        f"{API_V1}/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    print(f"状态码: {response.status_code}")
    data = response.json()
    pprint(data)
    
    if response.status_code == 200:
        return data["access_token"]
    return None


def test_get_user_info(token):
    """测试获取用户信息"""
    print_section("3. 获取当前用户信息")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_V1}/auth/me", headers=headers)
    print(f"状态码: {response.status_code}")
    pprint(response.json())


def test_text_translation(token):
    """测试文本翻译"""
    print_section("4. 文本翻译")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_V1}/translate/text",
        headers=headers,
        json={
            "text": "你好，世界！欢迎使用 AIPortal API。",
            "source_lang": "zh-Hans",
            "target_lang": "en",
            "use_cloud": True
        }
    )
    print(f"状态码: {response.status_code}")
    pprint(response.json())


def test_get_languages():
    """测试获取支持的语言"""
    print_section("5. 获取支持的语言")
    response = requests.get(f"{API_V1}/translate/languages")
    print(f"状态码: {response.status_code}")
    pprint(response.json())


def test_chat_completion(token):
    """测试对话"""
    print_section("6. AI 对话")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_V1}/chat/completion",
        headers=headers,
        json={
            "message": "请用一句话介绍 FastAPI",
            "model": "gpt-4",
            "temperature": 0.7
        }
    )
    print(f"状态码: {response.status_code}")
    pprint(response.json())


def test_get_models():
    """测试获取可用模型"""
    print_section("7. 获取可用 AI 模型")
    response = requests.get(f"{API_V1}/chat/models")
    print(f"状态码: {response.status_code}")
    pprint(response.json())


def main():
    """主测试函数"""
    print("\n" + "🚀"*30)
    print("   AIPortal FastAPI 功能测试")
    print("🚀"*30)
    
    try:
        # 1. 健康检查
        if not test_health_check():
            print("❌ API 服务未响应，请检查服务是否启动")
            return
        
        # 2. 登录
        token = test_login()
        if not token:
            print("❌ 登录失败")
            return
        
        print(f"\n✅ 登录成功! Token: {token[:50]}...")
        
        # 3. 获取用户信息
        test_get_user_info(token)
        
        # 4. 文本翻译
        test_text_translation(token)
        
        # 5. 获取支持的语言
        test_get_languages()
        
        # 6. AI 对话
        test_chat_completion(token)
        
        # 7. 获取可用模型
        test_get_models()
        
        print_section("✅ 所有测试完成!")
        print("📖 查看完整文档: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到 API 服务")
        print("请确保 FastAPI 服务正在运行:")
        print("  cd /home/user/webapp && python -m uvicorn api.main:app --reload")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")


if __name__ == "__main__":
    main()
