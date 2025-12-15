import streamlit as st
from function.local.XinferenceChatClient import XinferenceChatClient
import re

# --- 配置 ---
AVAILABLE_MODELS = ["qwen3", "qwen2.5-vl-instruct"]

# # --- 页面设置 ---
# st.set_page_config(
#     page_title="Xorbits Inference Chat",
#     page_icon="🤖",
#     layout="wide"
# )

st.subheader(":material/rocket_launch: Xorbits Inference Chat")

# --- 客户端初始化 ---
# 使用 Streamlit 的缓存机制来创建和缓存我们的客户端实例
@st.cache_resource
def get_chat_client():
    """返回 XinferenceChatClient 的一个单例。"""
    client = XinferenceChatClient()
    return client

chat_client = get_chat_client()

# --- 侧边栏设置 ---
with st.sidebar:
    st.header("模型配置")
    selected_model = st.selectbox(
        "选择一个模型进行对话:",
        options=AVAILABLE_MODELS,
        index=0  # 默认选择 qwen3
    )
    st.info(f"当前选择的模型: **{selected_model}**")

    # 思考过程控制开关，逻辑保持不变
    show_thinking_process = False
    if "qwen3" in selected_model:
        show_thinking_process = st.toggle(
            "显示思考过程 (Show Thinking)",
            value=False, # 默认关闭
            help="开启后，Qwen3模型将展示其`<think>`...`</think>`的思考步骤。"
        )

    if 'qwen2.5-vl' in selected_model:
        st.warning("提示: 您选择的是一个多模态模型 (VL)，但此界面仅支持文本对话。")

    if st.button("清除聊天记录", type="primary"):
        st.session_state.xinference_messages = []
        st.rerun()

# --- 聊天逻辑 ---
if "xinference_messages" not in st.session_state:
    st.session_state.xinference_messages = []

for message in st.session_state.xinference_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("请输入您的问题..."):
    st.session_state.xinference_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        raw_full_response = ""

        try:
            # 【核心调用简化】现在我们直接调用我们封装好的类的方法
            stream = chat_client.chat(
                model=selected_model,
                messages=st.session_state.xinference_messages,
                show_thinking=show_thinking_process
            )

            # 流式响应的处理逻辑保持不变
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    raw_full_response += chunk.choices[0].delta.content

                    # 后处理仍然保留，以防模型输出空的<think></think>标签或指令未完全生效
                    cleaned_response = re.sub(r"<think>.*?</think>", "", raw_full_response, flags=re.DOTALL).strip()
                    message_placeholder.markdown(cleaned_response + "▌")

            cleaned_response = re.sub(r"<think>.*?</think>", "", raw_full_response, flags=re.DOTALL).strip()
            message_placeholder.markdown(cleaned_response)
            final_response_to_save = cleaned_response

        except Exception as e:
            st.error(f"调用模型时出错: {e}")
            final_response_to_save = f"抱歉，与模型 `{selected_model}` 通信时发生错误。"
            message_placeholder.markdown(final_response_to_save)

        # 存储到历史记录的是清理后的回复
        st.session_state.xinference_messages.append({"role": "assistant", "content": final_response_to_save})