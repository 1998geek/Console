import json
import logging
import requests
import base64
from openai import AzureOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class AzureLLMService:
    """
    Service for Azure OpenAI and other LLM interactions.
    Migrated from legacy AzureAiClient.
    """
    def __init__(self):
        self.api_key = settings.AZURE_OPENAI_TOKEN
        self.azure_endpoint = settings.AZURE_OPENAI_ENDPOINT
        self.rest_endpoint = settings.AZURE_GROK3_REST_ENDPOINT
        self.api_version = "2025-01-01-preview"
        self.vision_deployment = settings.AZURE_OPENAI_VISION_DEPLOYMENT
        
        if not self.api_key or not self.azure_endpoint:
            logger.warning("Azure OpenAI credentials are missing in settings.")

        # Initialize OpenAI SDK client
        self.sdk_client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version,
        )

        # REST API settings for Grok
        self.rest_api_version = "2024-05-01-preview"
        self.rest_only_models = ["grok-3", "grok-3-mini"]

    def _get_chat_completion_sdk(self, messages: list, model: str, stream: bool, **kwargs):
        """Internal method for OpenAI SDK chat completion."""
        return self.sdk_client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            **kwargs
        )

    def _get_chat_completion_rest(self, messages: list, model: str, stream: bool, **kwargs):
        """Internal method for REST API chat completion (e.g. Grok)."""
        if not self.rest_endpoint:
            raise ValueError("AZURE_GROK3_REST_ENDPOINT is not configured.")

        url = f"{self.rest_endpoint}/models/chat/completions?api-version={self.rest_api_version}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "messages": messages,
            "model": model,
            "stream": stream,
        }

        # Model-specific parameters
        if model == "grok-3-mini":
            payload.update({
                "max_completion_tokens": kwargs.get('max_tokens', 16000),
                "temperature": kwargs.get('temperature', 1.0),
                "top_p": kwargs.get('top_p', 1.0)
            })
        elif model == "grok-3":
            payload.update({
                "max_completion_tokens": kwargs.get('max_tokens', 2048),
                "temperature": kwargs.get('temperature', 1.0),
                "top_p": kwargs.get('top_p', 1.0),
                "frequency_penalty": kwargs.get('frequency_penalty', 0),
                "presence_penalty": kwargs.get('presence_penalty', 0)
            })
        else:
            payload.update({
                "max_completion_tokens": kwargs.get('max_tokens', 2048),
                "temperature": kwargs.get('temperature', 1.0),
                "top_p": kwargs.get('top_p', 1.0)
            })

        try:
            response = requests.post(url, headers=headers, json=payload, stream=stream)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP Error in REST API call: {err.response.text}")
            raise err

    def get_chat_completion(self, messages: list, model: str, stream: bool = True, **kwargs):
        """
        Public method to get chat completions.
        Dispatches to SDK or REST based on model name.
        """
        try:
            if model in self.rest_only_models:
                return self._get_chat_completion_rest(messages, model, stream, **kwargs)
            else:
                return self._get_chat_completion_sdk(messages, model, stream, **kwargs)
        except Exception as e:
            logger.error(f"Error calling Azure AI service ({model}): {e}")
            raise e

    # Stream processors (Static methods or helper functions)
    @staticmethod
    def stream_processor(response_object):
        """Generator that yields content from response."""
        if isinstance(response_object, requests.Response):
            yield from AzureLLMService._stream_processor_rest(response_object)
        else:
            yield from AzureLLMService._stream_processor_sdk(response_object)

    @staticmethod
    def _stream_processor_sdk(response):
        if response:
            for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content

    @staticmethod
    def _stream_processor_rest(response):
        if response:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[6:]
                        if json_str.strip() == '[DONE]':
                            return
                        try:
                            data = json.loads(json_str)
                            if data.get('choices'):
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

    def analyze_image(self, image_bytes: bytes, prompt: str = "Describe this image") -> str:
        try:
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                }
            ]
            resp = self.sdk_client.chat.completions.create(
                model=self.vision_deployment,
                messages=messages,
                stream=False
            )
            if hasattr(resp, "choices") and resp.choices:
                return resp.choices[0].message.content.strip()
            return ""
        except Exception as e:
            logger.error(f"Vision analyze error: {e}")
            raise e
