import streamlit as st
import streamlit.components.v1 as components
from src.services.api_client import api_client

def show():
    st.title(":material/compare_arrows: Word 文档智能比对 (分词增强)")
    st.markdown("""
上传两个 `.docx` 文件，本工具将通过**中文分词技术**，实现**字词级别**的精准比对，
并以“修订模式”高亮显示两个文档之间的差异。注意：请使用Microsoft Office 官方文件。

- <span style="background-color: #e6ffe6;">绿色背景</span> 代表新增的内容。
- <span style="background-color: #ffe6e6; text-decoration: line-through;">红色删除线</span> 代表删除的内容。
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.header("文档 A (原始版本)")
        file1 = st.file_uploader("上传第一个 .docx 文件", type=['docx'], key="file1")
    with col2:
        st.header("文档 B (修订版本)")
        file2 = st.file_uploader("上传第二个 .docx 文件", type=['docx'], key="file2")
    if st.button("🚀 开始比对", type="primary"):
        if file1 and file2:
            with st.spinner('正在转换、分词和比对文档，请稍候...'):
                files = {
                    "file_original": (file1.name, file1.getvalue(), file1.type),
                    "file_revised": (file2.name, file2.getvalue(), file2.type)
                }
                res = api_client.upload_file_get_json("/contract/diff", files=files)
            if res and res.get("html_diff"):
                st.header("比对结果 (修订模式视图)")
                components.html(res["html_diff"], height=800, scrolling=True)
                output_name = st.text_input(
                    "保存文件名",
                    value="diff.html",
                    key=f"diff_name_{file1.name}_{file2.name}"
                )
                st.download_button(
                    label="📥 下载比对结果 (HTML)",
                    data=res["html_diff"].encode("utf-8"),
                    file_name=output_name,
                    mime="text/html"
                )
            else:
                st.error("比对失败，后端未返回有效的 HTML 差异数据。")
        else:
            st.error("❌ 请确保两个文件都已成功上传！")

render = show
