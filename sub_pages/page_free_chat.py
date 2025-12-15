# page_free_chat.py

import streamlit as st
# 【改动】只导入统一的 AzureAiClient 和 stream_processor
from function.AzureAIClient import AzureAiClient, stream_processor 
# 【改动】导入新的 REST API 终结点配置
from app_config.keys_config import AZURE_OPENAI_TOKEN, AZURE_OPENAI_ENDPOINT, AZURE_GROK3_REST_ENDPOINT

# --- 缓存 AI 客户端实例 (更新以包含 REST 终结点) ---
@st.cache_resource
def get_ai_client():
    # 【改动】增加对 AZURE_REST_ENDPOINT 的检查
    if not all([AZURE_OPENAI_TOKEN, AZURE_OPENAI_ENDPOINT, AZURE_GROK3_REST_ENDPOINT]) or \
       "YOUR_AZURE" in AZURE_OPENAI_TOKEN:
        st.error("请配置你的 Azure OpenAI 凭据，包括 SDK 和 REST 的 Endpoint。")
        return None
    # 【改动】将 rest_endpoint 传入客户端
    return AzureAiClient(
        api_key=AZURE_OPENAI_TOKEN, 
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        rest_endpoint=AZURE_GROK3_REST_ENDPOINT 
    )

ai_client = get_ai_client()
if not ai_client:
    st.stop()

col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
with col1:
    # 【改动】在模型列表中加入新的 Grok 模型
    chat_model = st.selectbox(
        '请选择一个聊天模型:',
        ["grok-3-mini", "grok-3", "gpt-4.1", "gpt-4.1-nano", "gpt-4.1-mini", "o3-mini","gpt-4o-mini", "gpt-4o"]
    )
with col2:
    if st.button('清空聊天记录', use_container_width=True, type="primary"):
        st.session_state.messages_free_chat = []
        st.rerun()

# --- 聊天记录初始化和显示 (无变化) ---
if "messages_free_chat" not in st.session_state:
    st.session_state.messages_free_chat = []

for message in st.session_state.messages_free_chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 聊天输入逻辑 ---
if prompt := st.chat_input("请输入你的问题..."):
    st.session_state.messages_free_chat.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("AI 正在思考中..."):
        with st.chat_message("assistant"):
            # 准备发送给 API 的消息历史 (无变化)
            history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages_free_chat]
            
            # 【核心改动】调用已封装好的客户端方法，无需关心具体实现
            stream = ai_client.get_chat_completion(
                messages=history,
                model=chat_model,
                # 可以继续传递其他参数，如 max_tokens
                # max_tokens=2048 
            )
            
            # 【核心改动】使用统一的流式处理器，代码更简洁
            # 它会自动处理来自 SDK 或 REST API 的不同响应格式
            response = st.write_stream(stream_processor(stream)) 
            st.session_state.messages_free_chat.append({"role": "assistant", "content": response})