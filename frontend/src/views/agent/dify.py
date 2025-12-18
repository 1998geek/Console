import streamlit as st
from src.services.api_client import api_client

def show():
    st.title(":material/chat_bubble: Dify - 智能体集成")
    if "dify_messages" not in st.session_state:
        st.session_state.dify_messages = []
    if "dify_conversation_id" not in st.session_state:
        st.session_state.dify_conversation_id = None
    col_clear, _ = st.columns([1, 9])
    with col_clear:
        if st.button("清空对话"):
            st.session_state.dify_messages = []
            st.session_state.dify_conversation_id = None
            st.rerun()
    for msg in st.session_state.dify_messages:
        st.chat_message(msg["role"]).write(msg["content"])
    prompt = st.chat_input("向 Dify 提问...")
    if prompt:
        st.chat_message("user").write(prompt)
        st.session_state.dify_messages.append({"role": "user", "content": prompt})
        payload = {
            "query": prompt,
            "conversation_id": st.session_state.dify_conversation_id
        }
        with st.spinner("智能体思考中..."):
            res = api_client.post("/agent/dify/chat", json=payload)
        if res and isinstance(res, dict) and res.get("answer") is not None:
            if res.get("conversation_id"):
                st.session_state.dify_conversation_id = res["conversation_id"]
            answer = res.get("answer", "")
            st.chat_message("assistant").write(answer)
            st.session_state.dify_messages.append({"role": "assistant", "content": answer})
        else:
            st.error("对话失败，请稍后重试")
            st.session_state.dify_messages.append({"role": "assistant", "content": "服务暂时不可用"})

render = show
