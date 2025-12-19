import streamlit as st
from src.services.api_client import api_client
from src.utils.ui import TaskProgress # [引入新工具]

def show():
    st.title(":material/letter_switch: 文档翻译 - 本地模型算力")
    
    if "local_trans_results" not in st.session_state:
        st.session_state.local_trans_results = []

    with st.container():
        st.markdown("💡 **提示**：利用本地/Azure OpenAI 模型进行精准语义翻译。")
        files = st.file_uploader("上传文件", type=["docx", "pptx", "xlsx"], accept_multiple_files=True)
        tgt = st.selectbox("目标语言", ["中文", "英文", "日文", "韩文", "德文", "法文"])
        submitted = st.button("🚀 开始 AI 翻译", type="primary", use_container_width=True)

    if submitted and files:
        st.session_state.local_trans_results = []
        progress = TaskProgress(title="启动 AI 翻译引擎...") # [使用新工具]
        
        lang_map = {"中文": "zh-Hans", "英文": "en", "日文": "ja", "韩文": "ko", "德文": "de", "法文": "fr"}
        target_lang = lang_map.get(tgt, "zh-Hans")
        total = len(files)

        for idx, f in enumerate(files, start=1):
            base_p = int(((idx - 1) / total) * 100)
            
            progress.update(base_p, f"正在准备 ({idx}/{total}): {f.name} ...")
            
            ext = f.name.split(".")[-1].lower() if "." in f.name else ""
            mime_map = {
                "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            }
            mime = mime_map.get(ext, "application/octet-stream")

            content = f.getvalue()
            files_payload = {"file": (f.name, content, mime)}
            data_payload = {"target_lang": target_lang, "mode": "local"}
            
            progress.update(base_p + 20, f"AI 正在深度思考并翻译 {f.name} (大文件可能耗时较长)...")
            res_content, _ = api_client.upload_and_download("/doc-tools/translate/document", files=files_payload, data=data_payload, timeout=600)
            
            if res_content:
                download_name = f"ai_trans_{f.name}"
                st.session_state.local_trans_results.append({
                    "original_name": f.name,
                    "default_name": download_name,
                    "data": res_content,
                    "mime": mime,
                    "key": f"dl_loc_{idx}_{f.name}"
                })
            else:
                st.error(f"❌ {f.name} 翻译失败")
            
        progress.finish("✅ 所有 AI 翻译任务完成！")

    if st.session_state.local_trans_results:
        st.divider()
        st.subheader(f"翻译结果 ({len(st.session_state.local_trans_results)})")
        for i, res in enumerate(st.session_state.local_trans_results):
            with st.container(border=True):
                c1, c2 = st.columns([3, 1], vertical_alignment="bottom") # [关键] 底部对齐
                with c1:
                    st.markdown(f"**🧠 AI 翻译文件:** `{res['original_name']}`")
                    new_name = st.text_input("重命名:", value=res['default_name'], key=f"rename_loc_{i}")
                with c2:
                    st.download_button(
                        label="⬇️ 下载结果",
                        data=res['data'],
                        file_name=new_name,
                        mime=res['mime'],
                        type="primary",
                        key=res['key'],
                        use_container_width=True
                    )

render = show