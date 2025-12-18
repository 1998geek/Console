import requests
from app.core.config import settings

class DifyService:
    def __init__(self):
        self.api_key = settings.DIFY_API_KEY
        self.api_base = settings.DIFY_API_BASE or "https://api.dify.ai/v1"
        self.endpoint = f"{self.api_base}/chat-messages"

    def chat(self, query: str, user: str, conversation_id: str | None = None, inputs: dict | None = None) -> dict:
        if not self.api_key:
            raise ValueError("DIFY_API_KEY is not configured")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": inputs or {},
            "query": query,
            "response_mode": "blocking",
            "user": user,
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id
        resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            try:
                msg = resp.json()
            except Exception:
                msg = resp.text
            raise RuntimeError(f"Dify error {resp.status_code}: {msg}")
        data = resp.json()
        answer = data.get("answer") or data.get("data", {}).get("answer") or ""
        conv_id = data.get("conversation_id") or data.get("data", {}).get("conversation_id")
        return {"answer": answer, "conversation_id": conv_id or conversation_id}
