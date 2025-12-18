import streamlit as st

def render():
    st.title(":material/chat_bubble: 多模型问答 - 多模态")
    st.write("支持文本与图片的多模态对话。")
    img = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"], accept_multiple_files=False)
    prompt = st.chat_input("输入消息")
    if prompt:
        st.chat_message("user").write(prompt)
        if img:
            st.image(img)
        st.chat_message("assistant").write("TODO: 调用 api_client")
