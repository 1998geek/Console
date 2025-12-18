import streamlit as st
from src.services.api_client import api_client

def show():
    st.title(":material/g_translate: 文档翻译 - 云端资源集成")
    files = st.file_uploader("上传文件", type=["docx", "pdf", "xlsx", "pptx"], accept_multiple_files=True)
    tgt = st.selectbox("目标语言", ["中文", "英语", "日语", "韩语", "德语", "法语"])
    run = st.button("开始云端翻译", type="primary")
    if run:
        if not files:
            st.warning("请上传文件")
            return
        lang_map = {
            "中文": "zh-Hans",
            "英语": "en",
            "日语": "ja",
            "韩语": "ko",
            "德语": "de",
            "法语": "fr",
        }
        target_lang = lang_map.get(tgt, "zh-Hans")
        for idx, f in enumerate(files, start=1):
            name = f.name
            ext = name.split(".")[-1].lower() if "." in name else ""
            if ext == "docx":
                mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext == "xlsx":
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif ext == "pptx":
                mime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            elif ext == "pdf":
                mime = "application/pdf"
            else:
                mime = "application/octet-stream"
            content = f.getvalue()
            files_payload = {"file": (name, content, mime)}
            data_payload = {"target_lang": target_lang, "mode": "cloud"}
            res_content, _ = api_client.upload_and_download("/doc-tools/translate/document", files=files_payload, data=data_payload)
            if res_content:
                download_name = f"trans_{name}"
                st.download_button("下载翻译结果", data=res_content, file_name=download_name, type="primary", key=f"dl_{idx}_{name}")
        st.success("翻译完成")

render = show
