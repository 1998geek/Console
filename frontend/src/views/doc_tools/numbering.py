import streamlit as st

def render():
    st.title(":material/frame_inspect: word文档整理 - 上传文件")
    st.markdown("将文档标题按层级自动编号与规范化，保持旧版布局。")
    file = st.file_uploader("上传 .docx 文件", type=["docx"])
    level = st.selectbox("最大标题层级", ["1", "2", "3", "4", "5"], index=2)
    keep_style = st.toggle("保留原始样式")
    run = st.button("开始整理", type="primary")
    if run:
        if file:
            st.info("TODO: 调用 api_client")
            st.success("已提交整理任务")
        else:
            st.warning("请上传文件")
