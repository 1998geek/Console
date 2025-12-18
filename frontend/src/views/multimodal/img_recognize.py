import streamlit as st

def render():
    st.title(":material/frame_inspect: 员工违规操作识别")
    imgs = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    run = st.button("开始识别", type="primary")
    if run:
        if imgs:
            st.info("TODO: 调用 api_client")
            st.success("识别任务已提交")
        else:
            st.warning("请上传图片")
