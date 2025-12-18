from app.services.azure_ai import AzureLLMService
from app.services.prompts import CONTRACT_REVIEW_SYSTEM_PROMPT

class ContractReviewer:
    def __init__(self):
        self.llm = AzureLLMService()
        self.model = "gpt-4.1-mini"

    @staticmethod
    def _build_system_prompt(review_points: list[str] | None) -> str:
        base = CONTRACT_REVIEW_SYSTEM_PROMPT.strip()
        if review_points:
            joined = "\n".join([f"- {p}" for p in review_points if p])
            extra = f"\n请重点围绕以下用户关注要点进行审查：\n{joined}\n"
            return base + extra
        return base

    def review_text(self, text: str, review_points: list[str] | None = None) -> str:
        system_prompt = self._build_system_prompt(review_points)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]
        response = self.llm.get_chat_completion(messages, model=self.model, stream=False)
        if hasattr(response, "choices"):
            return response.choices[0].message.content.strip()
        elif hasattr(response, "json"):
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
        raise Exception("Unexpected response format")

    def review_document(self, file_content: bytes, review_points: list[str] | None = None) -> str:
        try:
            text = file_content.decode("utf-8", errors="ignore")
        except Exception:
            text = file_content.decode("latin-1", errors="ignore")
        return self.review_text(text, review_points)
