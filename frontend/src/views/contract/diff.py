import streamlit as st
from src.services.api_client import api_client
from src.utils.ui import TaskProgress # [引入新工具]

def show():
    st.title(":material/compare_arrows: Word 文档智能比对")

    if "diff_result" not in st.session_state:
        st.session_state.diff_result = None

    with st.container():
        st.markdown("💡 **提示**：上传两个版本的 Word 文档，AI 将识别并在新文档中标记出差异。")
        col1, col2 = st.columns(2)
        with col1:
            file_base = st.file_uploader("📂 上传基准文档 (旧版)", type=["docx"], key="base_doc")
        with col2:
            file_target = st.file_uploader("📂 上传对比文档 (新版)", type=["docx"], key="target_doc")
        use_ai = st.toggle("启用 AI 语义增强对比", value=False)
        btn = st.button("🚀 开始比对", type="primary", disabled=not (file_base and file_target), use_container_width=True)

    if btn and file_base and file_target:
        st.session_state.diff_result = None
        
        # [使用新工具]：单任务阶段进度条
        progress = TaskProgress(title="初始化比对引擎...")
        
        try:
            # 阶段 1
            progress.update(10, "正在读取文档内容...")
            files_payload = [
                ("base_file", (file_base.name, file_base.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
                ("target_file", (file_target.name, file_target.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
            ]
            data_payload = {"use_ai": str(use_ai).lower()}

            # 阶段 2
            progress.update(30, "正在上传并进行段落对齐...")
            # 阶段 3 (耗时最长)
            progress.update(50, "正在生成修订模式 (请稍候)...")
            
            res_content, _ = api_client.upload_and_download("/contract/compare", files=files_payload, data=data_payload, timeout=300)

            # 阶段 4
            progress.update(90, "比对完成，正在生成报告...")
            
            if res_content:
                default_name = f"diff_{file_target.name}"
                st.session_state.diff_result = {
                    "base_name": file_base.name,
                    "target_name": file_target.name,
                    "default_name": default_name,
                    "data": res_content
                }
                progress.finish("✅ 比对报告已生成！")
            else:
                progress.fail("❌ 比对失败")
                st.error("无法生成比对结果，请检查后端服务。")
        except Exception as e:
            progress.fail("❌ 发生错误")
            st.error(f"Error: {e}")

    if st.session_state.diff_result:
        res = st.session_state.diff_result
        st.divider()
        with st.container(border=True):
            st.subheader("📊 比对报告")
            c1, c2 = st.columns([3, 1], vertical_alignment="bottom") # [关键] 底部对齐
            with c1:
                st.markdown(f"**基准:** `{res['base_name']}` vs **对比:** `{res['target_name']}`")
                new_name = st.text_input("重命名结果文件:", value=res['default_name'])
            with c2:
                st.download_button(
                    label="⬇️ 下载报告",
                    data=res['data'],
                    file_name=new_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )

render = show