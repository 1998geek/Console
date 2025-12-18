import streamlit as st
import base64
from src.services.api_client import api_client

def _file_to_base64(uploaded_file):
    if uploaded_file is None:
        return None
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode("utf-8")

def show():
    st.subheader(":material/perm_media: 多模态对话助手 (Azure)")

    if "multimodal_messages" not in st.session_state:
        st.session_state.multimodal_messages = []
    if "multimodal_last_image_b64" not in st.session_state:
        st.session_state.multimodal_last_image_b64 = None

    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        chat_model = st.selectbox(
            "请选择一个聊天模型:",
            options=["gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-mini", "o3-mini"],
            index=0
        )
    with col2:
        if st.button("清空聊天记录", type="primary", use_container_width=True):
            st.session_state.multimodal_messages = []
            st.session_state.multimodal_last_image_b64 = None
            st.rerun()

    st.markdown("---")

    uploaded_img = st.file_uploader("上传图片 (可选)", type=["png", "jpg", "jpeg"])
    if uploaded_img:
        st.session_state.multimodal_last_image_b64 = _file_to_base64(uploaded_img)
        st.image(uploaded_img, caption="已选择的图片", use_column_width=True)

    for message in st.session_state.multimodal_messages:
        with st.chat_message(message["role"]):
            content = message.get("content")
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "text":
                        st.markdown(part.get("text", ""))
                    elif part.get("type") == "image_url":
                        url = part.get("image_url", {}).get("url")
                        if url and url.startswith("data:image"):
                            try:
                                b64 = url.split(",")[-1]
                                st.image(base64.b64decode(b64))
                            except Exception:
                                st.caption("图片显示失败")
            else:
                st.markdown(str(content))

    if prompt := st.chat_input("请输入消息..."):
        user_content = None
        b64 = st.session_state.multimodal_last_image_b64
        if b64:
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        else:
            user_content = prompt

        user_msg = {"role": "user", "content": user_content}
        st.session_state.multimodal_messages.append(user_msg)

        with st.chat_message("user"):
            if isinstance(user_content, list):
                st.markdown(prompt)
                if b64:
                    try:
                        st.image(base64.b64decode(b64))
                    except Exception:
                        st.caption("图片显示失败")
            else:
                st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_text = ""
            try:
                payload = {
                    "model": chat_model,
                    "messages": st.session_state.multimodal_messages
                }
                stream = api_client.stream_post("/agent/multimodal/chat", json=payload)
                for chunk in stream:
                    if chunk:
                        full_text += chunk
                        placeholder.markdown(full_text + "▌")
                placeholder.markdown(full_text)
                st.session_state.multimodal_messages.append({"role": "assistant", "content": full_text})
            except Exception as e:
                placeholder.error(f"调用多模态聊天接口失败: {e}")

        st.session_state.multimodal_last_image_b64 = None

render = show
