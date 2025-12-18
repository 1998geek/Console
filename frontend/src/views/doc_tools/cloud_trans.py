import streamlit as st

def render():
    st.title(":material/g_translate: 文档翻译 - 云端资源集成")
    st.markdown("支持上传并翻译多种办公文档，界面与旧版保持一致。")
    col1, col2 = st.columns([2, 1])
    with col1:
        files = st.file_uploader("上传文件", type=["docx", "pptx", "pdf", "xlsx", "txt"], accept_multiple_files=True)
        src = st.selectbox("源语言", ["自动检测", "中文", "英文", "日文", "韩文", "德文", "法文"])
        tgt = st.selectbox("目标语言", ["中文", "英文", "日文", "韩文", "德文", "法文"])
        keep_layout = st.toggle("保留版式")
        submitted = st.button("开始翻译", type="primary")
    with col2:
        st.subheader("进度")
        st.progress(0)
        st.caption("等待任务开始")
    if submitted:
        if files:
            st.info("TODO: 调用 api_client")
            st.success("已提交翻译任务")
        else:
            st.warning("请上传文件")
