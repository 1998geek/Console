import os
import requests

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
                # For OAuth2 form data
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
                # Try to parse error message
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

api_client = APIClient()
