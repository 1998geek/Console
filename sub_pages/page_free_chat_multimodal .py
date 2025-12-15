import streamlit as st
from function.AzureAIClient import AzureAiClient, stream_processor, get_image_base64
from app_config.keys_config import AZURE_OPENAI_TOKEN, AZURE_OPENAI_ENDPOINT, AZURE_GROK3_REST_ENDPOINT

@st.cache_resource
def get_ai_client():
    if not all([AZURE_OPENAI_TOKEN, AZURE_OPENAI_ENDPOINT, AZURE_GROK3_REST_ENDPOINT]) or \
       "YOUR_AZURE" in AZURE_OPENAI_TOKEN:
        st.error("请配置你的 Azure OpenAI 凭据，包括 SDK 和 REST 的 Endpoint。")
        return None
    
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
    chat_model = st.selectbox(
        '请选择一个聊天模型:',
        ["gpt-4o-mini", "gpt-4o","gpt-4.1","gpt-4.1-nano","gpt-4.1-mini","o3-mini"])
with col2:
    if st.button('清空聊天记录', use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

# --- 聊天记录初始化和显示 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for item in message["content"]:
            if item["type"] == "text":
                st.markdown(item["text"])
            elif item["type"] == "image_url":
                st.image(item["image_url"]["url"], width=200)

# --- 聊天输入逻辑 ---
if submission := st.chat_input(
    "输入消息或上传图片...", 
    accept_file=True,
    file_type=["png", "jpg", "jpeg"]
):
    user_message_content = [{"type": "text", "text": submission.text}]
    for uploaded_file in submission.files:
        base64_image = get_image_base64(uploaded_file)
        user_message_content.append({
            "type": "image_url",
            "image_url": {"url": base64_image}
        })
    
    st.session_state.messages.append({"role": "user", "content": user_message_content})

    with st.chat_message("user"):
        for item in user_message_content:
            if item["type"] == "text":
                st.markdown(item["text"])
            elif item["type"] == "image_url":
                st.image(item["image_url"]["url"], width=200)

    with st.spinner("AI 正在思考中..."):
        with st.chat_message("assistant"):
            stream = ai_client.get_chat_completion(
                messages=[msg for msg in st.session_state.messages],
                model=chat_model
            )
            response = st.write_stream(stream_processor(stream))
            st.session_state.messages.append({"role": "assistant", "content": [{"type": "text", "text": response}]})