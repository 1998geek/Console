# 文件名: app.py (或者您的Streamlit主文件名)

import streamlit as st
import traceback

# 确保这些翻译函数位于正确的路径
from function.local.docx_translator import translate_docx_in_memory
from function.local.pptx_translator import translate_pptx_in_memory
from function.local.xlsx_translator import translate_xlsx_in_memory

st.title(":material/letter_switch: 带格式的文档翻译工具")
st.markdown("上传您的 `.docx`, `.pptx` 或 `.xlsx` 文件，选择目标语言，即可获得保留原始格式的翻译文件。注意：请使用Microsoft Office 官方文件，其他软件导出的兼容格式可能会导致翻译错误。")

# --- 用户输入组件 ---
uploaded_file = st.file_uploader(
    "1. 请在此处上传您的文件", 
    type=["docx","xlsx","pptx"]
)

target_language = st.selectbox(
    "2. 请选择目标语言",
    ("English", "中文", "日本語", "Français", "Deutsch", "Español", "Italiano", "Português", "Русский", "한국어"),
    index=1 # 默认选择中文
)

# =================================================================
#  新增：为XLSX文件提供专属选项
# =================================================================
# 初始化一个变量来存储开关的状态
translate_sheet_names_option = False

# 仅当上传了文件且文件是 .xlsx 类型时，才显示此选项
if uploaded_file is not None and uploaded_file.name.endswith('.xlsx'):
    st.info("检测到 Excel 文件，您可以选择是否翻译工作表名称。")
    translate_sheet_names_option = st.toggle(
        "翻译工作表名称 (Sheet Names)",
        value=False,  # 默认关闭以确保安全
        help="启用此项会翻译Excel中工作表的名称（例如Sheet1, Sheet2）。警告：这可能会破坏引用了这些工作表名称的单元格公式！"
    )

# --- 主程序逻辑 ---
if st.button("🚀 开始翻译", type="primary"):
    if uploaded_file is not None and target_language:
        
        with st.spinner(f"正在将文档翻译成 {target_language}，请稍候..."):
            try:
                progress_bar = st.progress(0, text="翻译进度")
                
                def update_progress(percentage):
                    percentage = min(1.0, max(0.0, percentage))
                    progress_bar.progress(percentage, text=f"翻译进度: {int(percentage * 100)}%")

                translated_file_buffer = None
                output_filename = f"翻译_{uploaded_file.name}"
                mime_type = None
                
                file_ext = uploaded_file.name.split('.')[-1]

                if file_ext == "docx":
                    st.info("检测到 Word (.docx) 文件，开始处理...")
                    translated_file_buffer = translate_docx_in_memory(
                        input_file_obj=uploaded_file,
                        target_language=target_language,
                        progress_callback=update_progress
                    )
                    mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

                elif file_ext == "pptx":
                    st.info("检测到 PowerPoint (.pptx) 文件，开始处理...")
                    translated_file_buffer = translate_pptx_in_memory(
                        input_file_obj=uploaded_file,
                        target_language=target_language,
                        progress_callback=update_progress
                    )
                    mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                
                elif file_ext == "xlsx":
                    st.info("检测到 Excel (.xlsx) 文件，开始处理...")
                    # ===========================================================
                    #  修改：将UI开关的状态传递给后端函数
                    # ===========================================================
                    translated_file_buffer = translate_xlsx_in_memory(
                        input_file_obj=uploaded_file,
                        target_language=target_language,
                        translate_sheet_names=translate_sheet_names_option, # 传递UI选项
                        progress_callback=update_progress
                    )
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                if translated_file_buffer:
                    # 使用 session_state 来持久化存储文件信息，防止重跑时丢失
                    st.session_state['translated_file'] = translated_file_buffer
                    st.session_state['output_filename'] = output_filename
                    st.session_state['mime_type'] = mime_type
                    
                    progress_bar.empty()
                    st.success("🎉 翻译完成！您现在可以下载文件了。")
                else:
                    st.error("无法处理该文件类型，请检查文件。")

            except Exception as e:
                st.error(f"翻译过程中发生错误: {e}")
                traceback.print_exc()
                if 'translated_file' in st.session_state:
                    del st.session_state['translated_file']

# --- 下载按钮 ---
# 检查 session_state 中是否有可供下载的文件
if 'translated_file' in st.session_state:
    st.download_button(
        label="📥 下载翻译后的文档",
        data=st.session_state['translated_file'],
        file_name=st.session_state['output_filename'],
        mime=st.session_state.get('mime_type')
    )