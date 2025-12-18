import streamlit as st 
from src.services.api_client import api_client 
 
def show(): 
    st.title(":material/letter_switch: 带格式的文档翻译工具 (本地模型版)") 
    st.markdown("上传您的 `.docx`, `.pptx` 或 `.xlsx` 文件，选择目标语言，即可获得保留原始格式的翻译文件。注意：请使用Microsoft Office 官方文件。") 
 
    uploaded_file = st.file_uploader( 
        "1. 请在此处上传您的文件", 
        type=["docx","xlsx","pptx"] 
    ) 
 
    target_language = st.selectbox( 
        "2. 请选择目标语言", 
        ("English", "中文", "日本語", "Français", "Deutsch", "Español", "Italiano", "Português", "Русский", "한국어"), 
        index=1 
    ) 
     
    lang_map = {"English": "en", "中文": "zh-Hans", "日本語": "ja", "Français": "fr", "Deutsch": "de"} 
    target_code = lang_map.get(target_language, "zh-Hans") 
 
    translate_sheet_names_option = False 
    if uploaded_file is not None and uploaded_file.name.endswith('.xlsx'): 
        st.info("检测到 Excel 文件，您可以选择是否翻译工作表名称。") 
        translate_sheet_names_option = st.toggle( 
            "翻译工作表名称 (Sheet Names)", 
            value=False, 
            help="启用此项会翻译Excel中工作表的名称（例如Sheet1, Sheet2）。警告：这可能会破坏引用了这些工作表名称的单元格公式！" 
        ) 
 
    if st.button("🚀 开始翻译", type="primary"): 
        if uploaded_file and target_language: 
            with st.spinner(f"正在将文档翻译成 {target_language}，请稍候..."): 
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)} 
                data = { 
                    "target_lang": target_code, 
                    "mode": "local", 
                    "translate_sheet_names": str(translate_sheet_names_option).lower() 
                } 
                 
                res_content, _ = api_client.upload_and_download("/doc-tools/translate/document", files=files, data=data) 
                 
                if res_content: 
                    st.success("🎉 翻译完成！您现在可以下载文件了。") 
                    output_name = st.text_input("保存文件名", value=uploaded_file.name, key=f"local_trans_name_{uploaded_file.name}") 
                    st.download_button( 
                        label="📥 下载翻译后的文档", 
                        data=res_content, 
                        file_name=output_name, 
                        mime="application/octet-stream" 
                    ) 
                else: 
                    st.error("翻译失败，请检查后端日志。") 
        else: 
             st.warning("请先上传文件。") 
 
render = show
