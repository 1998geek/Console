import streamlit as st
from src.services.api_client import api_client

def show():
    st.title(":material/description: 合同智能初审")
    tab_text, tab_file = st.tabs(["文本审查", "文档审查"])
    with tab_text:
        txt_input = st.text_area("请输入合同文本", height=300)
        btn_text = st.button("开始审查 (文本)")
        if btn_text:
            if not txt_input.strip():
                st.warning("请输入合同文本")
            else:
                with st.spinner("AI 正在审查合同，请稍候..."):
                    res = api_client.post("/contract/review/text", json={"text": txt_input})
                if res and res.get("analysis"):
                    st.markdown(res["analysis"])
                else:
                    st.error("审查失败")
    with tab_file:
        uploaded_file = st.file_uploader("上传合同文件", type=["txt", "md"])
        btn_file = st.button("开始审查 (文件)")
        if btn_file:
            if not uploaded_file:
                st.warning("请上传合同文件")
            else:
                content = uploaded_file.getvalue()
                files_payload = {"file": (uploaded_file.name, content, "text/plain")}
                with st.spinner("AI 正在审查合同，请稍候..."):
                    res = api_client.upload_file_get_json("/contract/review/file", files=files_payload)
                if res and res.get("analysis"):
                    st.markdown(res["analysis"])
                else:
                    st.error("审查失败")

render = show
