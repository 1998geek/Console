#!/usr/bin/env python3
"""
Test authentication flow
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test the complete authentication flow"""
    
    print("=" * 60)
    print("🧪 Testing Authentication Flow")
    print("=" * 60)
    
    # Step 1: Login
    print("\n📝 Step 1: Login")
    login_url = f"{BASE_URL}/api/v1/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"   POST {login_url}")
    print(f"   Body: {json.dumps(login_data, indent=2)}")
    
    response = requests.post(login_url, json=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 200:
        print("❌ Login failed!")
        return
    
    # Extract token
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"\n✅ Login successful!")
    print(f"   Access Token (first 50 chars): {access_token[:50]}...")
    
    # Step 2: Test /me endpoint
    print("\n📝 Step 2: Test /me endpoint")
    me_url = f"{BASE_URL}/api/v1/auth/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    print(f"   GET {me_url}")
    print(f"   Headers: Authorization: Bearer {access_token[:50]}...")
    
    response = requests.get(me_url, headers=headers)
    print(f"   Status: {response.status_code}")
    
    try:
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"   Response Text: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ /me endpoint successful!")
    else:
        print(f"\n❌ /me endpoint failed with status {response.status_code}")
    
    # Step 3: Test logout endpoint
    print("\n📝 Step 3: Test /logout endpoint")
    logout_url = f"{BASE_URL}/api/v1/auth/logout"
    
    print(f"   POST {logout_url}")
    print(f"   Headers: Authorization: Bearer {access_token[:50]}...")
    
    response = requests.post(logout_url, headers=headers)
    print(f"   Status: {response.status_code}")
    
    try:
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"   Response Text: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ Logout successful!")
    else:
        print(f"\n❌ Logout failed with status {response.status_code}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        test_auth_flow()
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
