import streamlit as st

def render():
    st.title(":material/chat_bubble: Dify - 智能体集成")
    st.markdown("与智能体交互的对话界面，保留旧版外观。")
    chat = st.container()
    with chat:
        st.write("🤖 智能体对话")
        st.chat_message("assistant").write("您好，我是智能体助手。")
        user_input = st.chat_input("请输入消息")
        if user_input:
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write("TODO: 调用 api_client")
