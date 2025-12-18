import requests
import sys
import time

BASE_URL = "http://localhost:8000/api"

def test_auth_flow():
    print("Wait for backend to be ready...")
    # Simple retry logic
    for i in range(10):
        try:
            requests.get("http://localhost:8000/")
            break
        except requests.exceptions.ConnectionError:
            print(f"Waiting for backend... ({i+1}/10)")
            time.sleep(2)
    
    # 1. Register
    username = f"testuser_{int(time.time())}"
    password = "testpassword123"
    email = f"{username}@example.com"
    
    print(f"\n1. Testing Registration for user: {username}")
    reg_payload = {
        "username": username,
        "password": password,
        "email": email
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
        if response.status_code == 200:
            print("✅ Registration Successful")
            print(response.json())
        else:
            print(f"❌ Registration Failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Registration Exception: {e}")
        return

    # 2. Login
    print(f"\n2. Testing Login for user: {username}")
    login_payload = {
        "username": username,
        "password": password
    }
    
    try:
        # OAuth2PasswordRequestForm expects form data, not JSON
        response = requests.post(f"{BASE_URL}/auth/login", data=login_payload)
        if response.status_code == 200:
            print("✅ Login Successful")
            token_data = response.json()
            print(f"Token: {token_data.get('access_token')[:20]}...")
            return token_data['access_token']
        else:
            print(f"❌ Login Failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Login Exception: {e}")
        return None

if __name__ == "__main__":
    token = test_auth_flow()
    if token:
        print("\n🎉 Auth Flow Verified Successfully!")
    else:
        print("\n💥 Auth Flow Failed.")
        sys.exit(1)
