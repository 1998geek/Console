from openai import OpenAI

from app_config.keys_config import XINFERENCE_BASE_URL
class XinferenceChatClient:
    """
    一个用于与 Xinference 服务进行交互的客户端类。

    该类封装了所有底层的 API 调用逻辑，包括：
    - 初始化 OpenAI 客户端。
    - 根据模型特性处理特定的请求参数（例如 Qwen3 的思考过程）。
    """
    def __init__(self, base_url: str = XINFERENCE_BASE_URL, api_key: str = "not_used"):
        """
        初始化客户端。

        Args:
            base_url (str): Xinference 服务的 OpenAI 兼容接口地址。
            api_key (str, optional): API 密钥，对于本地 Xinference 服务通常不需要。
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def chat(self, model: str, messages: list, show_thinking: bool = False, stream: bool = True):
        """
        与指定的模型进行对话。

        Args:
            model (str): 要调用的模型名称 (UID)。
            messages (list): 发送到模型的对话历史记录。
            show_thinking (bool, optional): 是否显示 Qwen3 的思考过程。默认为 False。
            stream (bool, optional): 是否以流式方式返回响应。默认为 True。

        Returns:
            一个可以迭代的流式响应对象 (stream)。
        """
        # 创建一个消息列表的副本，以防修改原始列表
        messages_for_api = list(messages)

        # 核心逻辑：根据模型和设置，自动处理特殊的系统指令
        # 这个复杂的逻辑被封装在类内部，主应用无需关心。
        if "qwen3" in model and not show_thinking:
            # 如果是 qwen3 且用户不希望看到思考过程，则在消息列表最前加入“关闭思考”的系统指令
            messages_for_api.insert(0, {"role": "system", "content": " /no_think"})

        # 调用 OpenAI SDK 发起请求
        # 注意：这里我们不再需要 extra_body，因为 /no_think 指令更可靠
        return self.client.chat.completions.create(
            model=model,
            messages=messages_for_api,
            stream=stream,
        )