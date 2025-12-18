from app.services.azure_ai import AzureLLMService
from app.services.prompts import CONTRACT_REVIEW_SYSTEM_PROMPT

class ContractReviewer:
    def __init__(self):
        self.llm = AzureLLMService()
        self.model = "gpt-4.1-mini"

    def review_text(self, text: str) -> str:
        messages = [
            {"role": "system", "content": CONTRACT_REVIEW_SYSTEM_PROMPT},
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

    def review_document(self, file_content: bytes) -> str:
        try:
            text = file_content.decode("utf-8", errors="ignore")
        except Exception:
            text = file_content.decode("latin-1", errors="ignore")
        return self.review_text(text)
