import streamlit as st
from src.services.api_client import api_client
from src.utils.ui import TaskProgress # [引入新工具]

def show():
    st.title(":material/format_list_numbered: Word 文档自动编号")
    
    if "numbering_results" not in st.session_state:
        st.session_state.numbering_results = []

    with st.container():
        st.info("💡 **功能说明**：自动识别文档中的标题结构，并进行规范化重新编号。")
        files = st.file_uploader("上传 Word 文档", type=["docx"], accept_multiple_files=True)
        run = st.button("🚀 开始整理", type="primary", use_container_width=True)

    if run and files:
        st.session_state.numbering_results = []
        progress = TaskProgress(title="开始解析文档结构...") # [使用新工具]
        total = len(files)

        for idx, f in enumerate(files, start=1):
            base_p = int(((idx - 1) / total) * 100)
            progress.update(base_p, f"正在分析 ({idx}/{total}): {f.name} ...")
            
            content = f.getvalue()
            files_payload = {"file": (f.name, content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            
            progress.update(base_p + 30, f"正在重构 {f.name} 的编号体系...")
            res_content, _ = api_client.upload_and_download("/doc-tools/heading-numbering", files=files_payload)
            
            if res_content:
                dl_name = f"formatted_{f.name}"
                st.session_state.numbering_results.append({
                    "original_name": f.name,
                    "default_name": dl_name,
                    "data": res_content,
                    "key": f"num_{idx}_{f.name}"
                })
            else:
                st.error(f"❌ {f.name} 处理失败。")
            
        progress.finish("✅ 文档整理完成！")

    if st.session_state.numbering_results:
        st.divider()
        st.subheader("处理结果")
        for i, res in enumerate(st.session_state.numbering_results):
            with st.container(border=True):
                c1, c2 = st.columns([3, 1], vertical_alignment="bottom") # [关键] 底部对齐
                with c1:
                    st.markdown(f"**📄 原文件:** `{res['original_name']}`")
                    new_name = st.text_input("保存文件名", value=res['default_name'], key=f"rename_num_{i}")
                with c2:
                    st.download_button(
                        "⬇️ 下载文档",
                        data=res['data'],
                        file_name=new_name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True,
                        key=res['key']
                    )

render = show