import streamlit as st

def render():
    st.title(":material/compare_arrows: Word 文档智能比对 (分词增强)")
    st.markdown("""
上传两个 `.docx` 文件，本工具通过中文分词实现字词级比对，并以修订模式高亮差异。
- <span style="background-color: #e6ffe6;">绿色背景</span> 代表新增内容
- <span style="background-color: #ffe6e6; text-decoration: line-through;">红色删除线</span> 代表删除内容
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.header("文档 A (原始版本)")
        f1 = st.file_uploader("上传第一个 .docx 文件", type=["docx"], key="file1")
    with col2:
        st.header("文档 B (修订版本)")
        f2 = st.file_uploader("上传第二个 .docx 文件", type=["docx"], key="file2")
    if st.button("🚀 开始比对"):
        if f1 and f2:
            st.info("TODO: 调用 api_client")
            st.success("比对任务已提交")
        else:
            st.warning("请同时上传两个文件")
