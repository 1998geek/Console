import streamlit as st
import time
from api_client import upload_file_for_translation, get_translation_status

# --- 1. 页面布局与配置 ---
st.subheader(':material/g_translate: 文档翻译 (云端加速版)')

lunages = [
    ["zh-Hans", "简体中文"],
    ["en", "English"],
    ["ja", "日本語"],
    ["ko", "한국어"],
    ["fr", "Français"],
    ["de", "Deutsch"],
    ["es", "Español"],
    ["it", "Italiano"],
    ["pt", "Português"],
    ["ru", "Русский"],
    ["ar", "العربية"],
    ["tr", "Türkçe"],
    ["pl", "Polski"],
    ["nl", "Nederlands"],
    ["sv", "Svenska"],
]

supported_types = ["pdf", "docx", "pptx", "txt", "xlsx", "html", "xml", "markdown", "md"]
MAX_FILE_SIZE = 40 * 1024 * 1024  # 40MB

# --- 2. 状态初始化 ---
if 'current_task_id' not in st.session_state:
    st.session_state.current_task_id = None
if 'translation_result' not in st.session_state:
    st.session_state.translation_result = None # 存储 {url: '...', filename: '...'}

# --- 3. 用户输入 ---
selected = st.selectbox("请选择目标语言", options=lunages, format_func=lambda x: x[1], index=None)
disabled = True if selected is None else False

# 如果已经有结果，先清空上传框，强制用户点“开始新任务”来清理状态
if st.session_state.translation_result:
    st.success("🎉 上一次翻译任务已完成！")
    st.markdown(f"**[点击下载翻译文件]({st.session_state.translation_result['url']})**")
    
    if st.button("开始新的翻译任务", type="primary"):
        st.session_state.translation_result = None
        st.session_state.current_task_id = None
        st.rerun()
else:
    # 正常上传流程
    uploaded_file = st.file_uploader("请选择文件 (小于40MB)", type=supported_types, disabled=disabled)

    if uploaded_file and st.button("开始翻译", type="primary", disabled=disabled):
        with st.spinner("正在上传文件并唤醒 Azure 翻译引擎 (约需5-10秒)..."):
            task_id = upload_file_for_translation(uploaded_file, selected[0])
            if task_id:
                st.session_state.current_task_id = task_id
                st.toast("任务提交成功！Azure 正在处理...", icon="🚀")
                st.rerun() # 强制刷新进入轮询模式
            else:
                st.error("任务提交失败，请检查后端日志。")

# --- 4. 进度轮询 (独立逻辑块) ---
if st.session_state.current_task_id and not st.session_state.translation_result:
    task_id = st.session_state.current_task_id
    
    st.divider()
    st.info("💡 提示：Azure 文档翻译需要排队和保持排版，通常需要 30-60 秒，请耐心等待。")
    
    progress_bar = st.progress(0)
    log_placeholder = st.empty()
    
    while True:
        status_data = get_translation_status(task_id)
        
        if not status_data:
            time.sleep(2)
            continue
        
        progress = status_data.get("progress", 0)
        message = status_data.get("message", "")
        state = status_data.get("status", "processing")
        download_url = status_data.get("download_url")
        
        # 更新 UI
        try:
            progress_value = int(progress)
        except Exception:
            progress_value = 0
        progress_value = max(0, min(100, progress_value))

        progress_bar.progress(progress_value)
        log_placeholder.code(f"[{time.strftime('%H:%M:%S')}] {message}")
        
        # 完成状态处理
        if state == "completed":
            progress_bar.progress(100)
            if download_url:
                # 存入 Session，确保按钮不消失
                st.session_state.translation_result = {
                    "url": download_url, 
                    "filename": "translated_file"
                }
                st.session_state.current_task_id = None # 结束任务
                st.rerun() # 刷新页面显示结果卡片
            else:
                log_placeholder.error("错误：后端返回了完成状态，但没有下载链接！")
            break
            
        elif state == "failed":
            log_placeholder.error(f"❌ 翻译失败: {message}")
            if st.button("重试"):
                st.session_state.current_task_id = None
                st.rerun()
            break
        
        time.sleep(2)
