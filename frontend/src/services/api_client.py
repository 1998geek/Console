import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://backend:8000/api")

class APIClient:
    def __init__(self):
        self.base_url = API_URL
        self.token = None

    def set_token(self, token: str):
        self.token = token

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def post(self, endpoint: str, data: dict = None, json: dict = None, form_data: bool = False):
        url = f"{self.base_url}{endpoint}"
        try:
            if form_data:
                headers = self._get_headers()
                if "Content-Type" in headers:
                    del headers["Content-Type"]
                response = requests.post(url, data=data, headers=headers)
            else:
                response = requests.post(url, json=json, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if e.response is not None:
                try:
                    detail = e.response.json().get("detail", str(e))
                    raise Exception(detail)
                except:
                    raise Exception(str(e))
            raise e

    def get(self, endpoint: str):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise e

    def upload_and_download(self, endpoint: str, files: dict, data: dict | None = None, timeout: int = 300):
        if "token" in st.session_state and st.session_state.get("token"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
        elif self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
        else:
            st.error("请先登录")
            return None, None
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=timeout, stream=True)
            if response.status_code == 200:
                return response.content, response.headers
            else:
                try:
                    msg = response.json().get("detail", response.text)
                except Exception:
                    msg = response.text
                st.error(f"请求失败 ({response.status_code}): {msg}")
                return None, None
        except Exception as e:
            st.error(f"网络连接错误: {str(e)}")
            return None, None

    def upload_file_get_json(self, endpoint: str, files: dict, data: dict | None = None, timeout: int = 180):
        if "token" in st.session_state and st.session_state.get("token"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
        elif self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
        else:
            st.error("请先登录")
            return None
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            try:
                msg = e.response.json().get("detail", e.response.text if e.response else str(e))
            except Exception:
                msg = str(e)
            st.error(f"请求失败: {msg}")
            return None

api_client = APIClient()
