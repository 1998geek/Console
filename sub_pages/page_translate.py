import streamlit as st
from io import BytesIO 
import uuid
from function.AzureBlobService import AzureBlobService
from function.AzureDocumentTranslator import AzureDocumentTranslator

# https://learn.microsoft.com/en-us/azure/ai-services/translator/language-support

st.subheader(':material/g_translate: 文档翻译')
lunages = [["zh-Hans", "简体中文"],
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
    ["sv", "Svenska"],]

type = ["pdf", "docx", "pptx", "txt", "xlsx", "doc", "ppt", "xls", "csv", "html", "xml", "mhtml", "odt", "odp", "ods", "rtf", "tsv", "markdown", "md", "mht", "msg"]
MAX_FILE_SIZE = 40 * 1024 * 1024    

selected = st.selectbox("请选择您要翻译文档的输出语言", options=lunages, format_func=lambda x: x[1], index=None, key="language")

disabled = True
if selected is not None:
     disabled = False
else:
    disabled = True

uploaded_file = st.file_uploader("Please Choose a file you want to translate and make sure the file is less than 40 MB", type=type, disabled =disabled)
if uploaded_file is not None:

    file_size = uploaded_file.getbuffer().nbytes  
    if file_size > MAX_FILE_SIZE:  
            st.error('文件太大！请上传40MB以内的文件, 或者切分文件后再上传') 
            st.stop()

    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    pdf_file = BytesIO(bytes_data) 

    with st.spinner(text="文件处理中，请耐心等待，文档越大所需时间越久."):
        pdf_file.seek(0)      
        # Upload the pdf to blob storage
        connection_string = ""
        file_name = "files/"+uploaded_file.name
        file_name = "files/" + str(uuid.uuid4()) + "_" + uploaded_file.name

        with st.expander(f"log info:", expanded=True):
            st.info(str(uploaded_file.name) + " - 开始上传文件.")
            AzureBlobService = AzureBlobService()
            AzureBlobService.upload_file_to_blob_storage(file_name, pdf_file)
            st.info(str(uploaded_file.name) + " - 文件上传成功.")               
            st.info(str(uploaded_file.name) + " - 正在翻译.")
            translator = AzureDocumentTranslator()
            translated_url = translator.start_translation(file_name, to_language=selected[0])
            st.info(str(uploaded_file.name) + " - 文件翻译成功.")
            # st.markdown(  
            #             f'''<div style="padding: 12px; background-color: #e8f4fc; border-radius: 5px;">  
            #             <b>翻译后的文件下载地址为: </b><a href="{translated_url}" target="_blank">点击下载</a>  
            #             </div>''',   
            #             unsafe_allow_html=True)  
            
            st.link_button("点击下载翻译后的文件", 
                translated_url,icon="📥")

    st.success("done!")
