import streamlit as st
from src.services.api_client import api_client
from src.utils.ui import TaskProgress # [引入新工具]

def show():
    st.title(":material/policy: 标书智能审查")

    if "bidding_results" not in st.session_state:
        st.session_state.bidding_results = []

    with st.container():
        st.info("💡 **说明**：上传招标文件，AI 将自动分析关键条款、风险点并生成审查报告。")
        files = st.file_uploader("上传标书文件", type=["docx", "pdf"], accept_multiple_files=True)
        run = st.button("🚀 开始审查", type="primary", use_container_width=True)

    if run and files:
        st.session_state.bidding_results = []
        progress = TaskProgress(title="开始审查任务...") # [使用新工具]
        total = len(files)

        for idx, f in enumerate(files, start=1):
            base_p = int(((idx - 1) / total) * 100)
            progress.update(base_p, f"正在分析 ({idx}/{total}): {f.name} (耗时较长)...")
            
            content = f.getvalue()
            mime = "application/pdf" if f.name.lower().endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            files_payload = {"file": (f.name, content, mime)}
            
            progress.update(base_p + 20, f"AI 正在提取 {f.name} 的关键条款...")
            res_content, _ = api_client.upload_and_download("/contract/review-bidding", files=files_payload, timeout=600)
            
            if res_content:
                report_name = f"审查报告_{f.name.split('.')[0]}.docx"
                st.session_state.bidding_results.append({
                    "original_name": f.name,
                    "default_name": report_name,
                    "data": res_content,
                    "key": f"bid_{idx}_{f.name}"
                })
            else:
                st.error(f"❌ {f.name} 审查失败。")
            
        progress.finish("✅ 审查完成！请下载报告。")

    if st.session_state.bidding_results:
        st.divider()
        st.subheader("审查报告")
        for i, res in enumerate(st.session_state.bidding_results):
            with st.container(border=True):
                c1, c2 = st.columns([3, 1], vertical_alignment="bottom") # [关键] 底部对齐
                with c1:
                    st.markdown(f"**📑 来源标书**: `{res['original_name']}`")
                    new_name = st.text_input("重命名报告:", value=res['default_name'], key=f"rename_bid_{i}")
                with c2:
                    st.download_button(
                        label="⬇️ 下载报告",
                        data=res['data'],
                        file_name=new_name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True,
                        key=res['key']
                    )

render = show