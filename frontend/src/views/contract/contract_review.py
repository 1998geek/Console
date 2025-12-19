import streamlit as st
from src.services.api_client import api_client
from src.utils.ui import TaskProgress # [引入新工具]

def show():
    st.title(":material/description: 合同智能初审")

    if "contract_results" not in st.session_state:
        st.session_state.contract_results = []

    with st.container():
        st.markdown("💡 **功能**：上传合同草稿，AI 助手将检查常见法律陷阱、条款缺失及合规性问题。")
        files = st.file_uploader("上传合同文件", type=["docx", "pdf"], accept_multiple_files=True)
        col1, col2 = st.columns(2)
        with col1:
            contract_type = st.selectbox("合同类型", ["通用合同", "销售合同", "采购合同", "劳动合同", "保密协议"])
        with col2:
            st.write("") 
            st.write("")
            run = st.button("🚀 开始初审", type="primary", use_container_width=True)

    if run and files:
        st.session_state.contract_results = []
        progress = TaskProgress(title="启动法律助手...") # [使用新工具]
        total = len(files)

        for idx, f in enumerate(files, start=1):
            base_p = int(((idx - 1) / total) * 100)
            progress.update(base_p, f"正在审查 ({idx}/{total}): {f.name} ...")
            
            content = f.getvalue()
            mime = "application/pdf" if f.name.lower().endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            
            files_payload = {"file": (f.name, content, mime)}
            data_payload = {"type": contract_type}
            
            progress.update(base_p + 30, f"AI 正在检查 {f.name} 的合规风险...")
            res_content, _ = api_client.upload_and_download("/contract/review-general", files=files_payload, data=data_payload, timeout=300)
            
            if res_content:
                report_name = f"初审意见_{f.name.split('.')[0]}.docx"
                st.session_state.contract_results.append({
                    "original_name": f.name,
                    "default_name": report_name,
                    "data": res_content,
                    "key": f"ctr_{idx}_{f.name}"
                })
            else:
                st.error(f"❌ {f.name} 审查失败。")

        progress.finish("✅ 初审完成！")

    if st.session_state.contract_results:
        st.divider()
        st.subheader("初审意见书")
        for i, res in enumerate(st.session_state.contract_results):
            with st.container(border=True):
                c1, c2 = st.columns([3, 1], vertical_alignment="bottom") # [关键] 底部对齐
                with c1:
                    st.markdown(f"**📝 合同原件**: `{res['original_name']}`")
                    new_name = st.text_input("重命名意见书:", value=res['default_name'], key=f"rename_ctr_{i}")
                with c2:
                    st.download_button(
                        label="⬇️ 下载意见",
                        data=res['data'],
                        file_name=new_name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True,
                        key=res['key']
                    )

render = show