import streamlit as st
from src.services.api_client import api_client
from urllib.parse import unquote

def render():
    st.title("📄 Word 标题层级与编号修正器")
    st.markdown("""
    这个工具首先修正您 Word 文档中的标题层级，然后为它们生成正确的编号。
    
    **核心功能:**
    - **智能层级压缩**: 工具会分析每个章节，如果存在跳级（例如，只有1、3、5级），它会自动将它们压缩为连续的级别（1、2、3级）。
    - **自动生成编号**: 在层级修正后，为所有标题添加或更新为正确的层级编号 (例如: 1.2.1 标题文本)。
    - **保留格式**: 在操作时，会尽量保留您原有的标题文字格式（如加粗、颜色等）。
    
    请上传您的 .docx 文件开始。同时自动保留原样式。不需要设置最大标题层级，应该自己检测。
    """)
    
    file = st.file_uploader("上传 .docx 文件", type=["docx"])
    
    if st.button("开始整理", type="primary"):
        if file:
            with st.spinner("正在处理文档..."):
                files = {"file": (file.name, file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                # Call the backend endpoint /doc-tools/numbering
                # api_client base_url is .../api, so we use /doc-tools/numbering
                content, headers = api_client.upload_and_download("/doc-tools/numbering", files=files)
                
                if content:
                    # Extract filename from Content-Disposition header if available
                    filename = "numbered_document.docx"
                    if headers and "Content-Disposition" in headers:
                        cd = headers["Content-Disposition"]
                        if "filename*=" in cd:
                            filename = unquote(cd.split("filename*=")[1].replace("utf-8''", ""))
                        elif "filename=" in cd:
                            filename = cd.split("filename=")[1].strip('"')
                    
                    st.success("✅ 整理完成！")
                    output_name = st.text_input("保存文件名", value=filename, key=f"numbering_name_{filename}")
                    st.download_button(
                        label="下载整理后的文档",
                        data=content,
                        file_name=output_name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
        else:
            st.warning("请先上传文件")
