import streamlit as st
from src.services.api_client import api_client

def show():
    st.title(":material/frame_inspect: 图片识别")
    img = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"], accept_multiple_files=False)
    prompt = st.text_input("提示词", value="这张图片里有什么？")
    if img:
        st.image(img)
    run = st.button("开始分析", type="primary")
    if run:
        if not img:
            st.warning("请上传图片")
            return
        content = img.getvalue()
        files_payload = {"file": (img.name, content, "image/jpeg")}
        data_payload = {"prompt": prompt}
        with st.spinner("AI 正在分析图片，请稍候..."):
            res = api_client.upload_file_get_json("/multimodal/vision/analyze", files=files_payload, data=data_payload)
        if res and res.get("description"):
            st.markdown(res["description"])
        else:
            st.error("分析失败")

render = show
