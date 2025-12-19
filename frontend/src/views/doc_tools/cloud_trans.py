import streamlit as st
from src.services.api_client import api_client
from src.utils.ui import TaskProgress  # [引入新工具]

def show():
    st.title(":material/g_translate: 文档翻译 - 云端资源集成")
    
    if "cloud_trans_results" not in st.session_state:
        st.session_state.cloud_trans_results = []

    with st.container():
        st.info("💡 提示：云端模式支持 PDF、Word、PPT、Excel 格式。")
        files = st.file_uploader("上传文件", type=["docx", "pdf", "xlsx", "pptx"], accept_multiple_files=True)
        tgt = st.selectbox("目标语言", ["中文", "英语", "日语", "韩语", "德语", "法语"])
        
        run = st.button("🚀 开始云端翻译", type="primary", use_container_width=True)
    
    if run and files:
        st.session_state.cloud_trans_results = []
        
        # [使用新工具] 初始化进度条
        progress = TaskProgress(title="准备开始翻译任务...")
        
        lang_map = {"中文": "zh-Hans", "英语": "en", "日语": "ja", "韩语": "ko", "德语": "de", "法语": "fr"}
        target_lang = lang_map.get(tgt, "zh-Hans")
        total_files = len(files)

        for idx, f in enumerate(files, start=1):
            # 计算当前文件的进度百分比范围
            # 例如共2个文件：文件1占 0-50%，文件2占 50-100%
            base_p = int(((idx - 1) / total_files) * 100)
            target_p = int((idx / total_files) * 100)
            
            progress.update(base_p, f"正在处理 ({idx}/{total_files}): {f.name} ...")
            
            # 模拟上传阶段进度
            progress.update(base_p + 10, f"正在上传 {f.name}...")

            ext = f.name.split(".")[-1].lower() if "." in f.name else ""
            mime_map = {
                "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "pdf": "application/pdf"
            }
            mime = mime_map.get(ext, "application/octet-stream")
            
            content = f.getvalue()
            files_payload = {"file": (f.name, content, mime)}
            data_payload = {"target_lang": target_lang, "mode": "cloud"}
            
            # 等待后端
            progress.update(base_p + 40, f"AI 正在翻译 {f.name} (请稍候)...")
            res_content, _ = api_client.upload_and_download("/doc-tools/translate/document", files=files_payload, data=data_payload)
            
            if res_content:
                download_name = f"trans_{f.name}"
                st.session_state.cloud_trans_results.append({
                    "original_name": f.name,
                    "default_name": download_name,
                    "data": res_content,
                    "mime": mime,
                    "key": f"dl_{idx}_{f.name}"
                })
            else:
                st.error(f"❌ 文件 {f.name} 翻译失败")

            # 完成当前文件
            progress.update(target_p, f"文件 {f.name} 处理完毕")

        progress.finish("✅ 所有翻译任务完成！")

    # 结果展示
    if st.session_state.cloud_trans_results:
        st.divider()
        st.subheader(f"翻译结果 ({len(st.session_state.cloud_trans_results)})")
        
        for i, res in enumerate(st.session_state.cloud_trans_results):
            with st.container(border=True):
                c1, c2 = st.columns([3, 1], vertical_alignment="bottom") # [关键] 底部对齐
                with c1:
                    st.markdown(f"**📄 原文件:** `{res['original_name']}`")
                    new_name = st.text_input("重命名下载文件:", value=res['default_name'], key=f"rename_cloud_{i}")
                with c2:
                    st.download_button(
                        label="⬇️ 下载文件",
                        data=res['data'],
                        file_name=new_name,
                        mime=res['mime'],
                        type="primary",
                        key=res['key'],
                        use_container_width=True
                    )

render = show