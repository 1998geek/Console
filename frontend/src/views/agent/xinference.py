import streamlit as st

def render():
    st.title(":material/rocket_launch: XInference - 本地模型平台集成")
    base_url = st.text_input("平台地址", "http://localhost:9997")
    model = st.selectbox("选择模型", ["qwen2", "llama3", "mistral"], index=0)
    st.write("对话")
    user_input = st.chat_input("请输入消息")
    if user_input:
        st.chat_message("user").write(user_input)
        st.chat_message("assistant").write("TODO: 调用 api_client")
