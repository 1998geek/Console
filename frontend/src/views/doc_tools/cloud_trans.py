import time
import requests
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
        
        # Create a container for each file to show progress
        for idx, f in enumerate(files, start=1):
            with st.container(border=True):
                st.subheader(f"📄 {f.name}")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                name = f.name
                ext = name.split(".")[-1].lower() if "." in name else ""
                
                # Determine mime type
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
                
                status_text.text("正在上传并启动任务...")
                
                # 1. Submit Task
                res = api_client.upload_file_get_json("/doc-tools/translate/document/task", files=files_payload, data=data_payload)
                
                if res and "task_id" in res:
                    task_id = res["task_id"]
                    
                    # 2. Poll Status
                    while True:
                        try:
                            task_status = api_client.get(f"/tasks/{task_id}")
                        except Exception as e:
                            status_text.error(f"获取任务状态失败: {e}")
                            break
                        if not task_status:
                            status_text.error("无法获取任务状态")
                            break
                            
                        state = task_status.get("status")
                        progress = task_status.get("progress", 0)
                        message = task_status.get("message", "")
                        
                        try:
                            progress_value = int(progress)
                        except Exception:
                            progress_value = 0
                        progress_value = max(0, min(100, progress_value))

                        progress_bar.progress(progress_value)
                        status_text.text(f"{message} ({progress}%)")
                        
                        if state == "completed":
                            result = task_status.get("result", {})
                            download_url = result.get("download_url")
                            if download_url:
                                st.success("翻译完成")
                                output_name = st.text_input("保存文件名", value=name, key=f"cloud_trans_name_{task_id}")
                                try:
                                    resp = requests.get(download_url, timeout=300)
                                    resp.raise_for_status()
                                    st.download_button(
                                        label="📥 下载翻译结果",
                                        data=resp.content,
                                        file_name=output_name,
                                        mime=mime,
                                        type="primary",
                                        key=f"cloud_trans_dl_{task_id}"
                                    )
                                except Exception:
                                    st.markdown(f"### [📥 点击下载翻译结果]({download_url})")
                            else:
                                st.error("翻译完成但未找到下载链接")
                            break
                        elif state == "failed":
                            st.error(f"任务失败: {task_status.get('error')}")
                            break
                        
                        time.sleep(1)
                else:
                    status_text.error("任务启动失败，请检查网络或重试")

render = show
