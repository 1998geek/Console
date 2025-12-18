from .api_client import api_client
import streamlit as st

def login(username, password):
    try:
        # OAuth2PasswordRequestForm expects username and password in form data
        data = {
            "username": username,
            "password": password
        }
        # Call backend login endpoint
        response = api_client.post("/auth/login", data=data, form_data=True)
        token = response.get("access_token")
        if token:
            api_client.set_token(token)
            st.session_state.token = token
            return {"success": True, "token": token, "username": username}
        return {"success": False, "message": "No token received"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def register(username, password, email=None):
    try:
        data = {
            "username": username,
            "password": password,
            "email": email
        }
        response = api_client.post("/auth/register", json=data)
        return {"success": True, "user": response}
    except Exception as e:
        return {"success": False, "message": str(e)}
