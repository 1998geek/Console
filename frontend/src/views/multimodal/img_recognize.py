import streamlit as st 
import base64 
from src.services.api_client import api_client 
 
def show(): 
    st.subheader(':material/frame_inspect: 图片识别') 
     
    category = [ 
        ["着装识别", 0], 
        ["票据识别", 1], 
        ["条形码识别", 2], 
    ] 
     
    prompts = [ 
        "⽬标区域 ：⾐服上的⽂字,⽂字内容 ：⾐服上的⽂字可能包括品牌名称 输出格式 ：请以⽂本形式输出 是否在衣服上检测到了⽂字？如果有，请输出⽂字内容。请注意，可能会有多个⽂字内容。请将所有检测到的⽂字内容以结构化⽂本形式输出结果。",  
        "请使⽤OCR技术识别并提取图⽚中票据上的所有关键信息，包括起点站、终点站、通⾏时间、⾦额以及其他标识，并以结构化⽂本形式输出结果。", 
        "请使⽤OCR技术识别并提取图⽚中的条形码内容（字母开头的编码 如A001808250593）及其下⽅的⽂字信息（如验证码、产品型号、产品代码），并以结构化⽂本形式输出结果。" 
    ] 
 
    selected = st.selectbox( 
        "please select the category you want to recognize", 
        options=category, 
        format_func=lambda x: x[0], 
        index=None, 
        key="selectbox_category" 
    ) 
 
    disabled = True if selected is None else False 
     
    type = ["jpg", "jpeg", "png", "webp"] 
    MAX_FILE_SIZE = 40 * 1024 * 1024    
     
    uploaded_file = st.file_uploader( 
        "Please Choose a file you want to recognize and make sure the file is less than 40 MB", 
        type=type, 
        disabled=disabled 
    ) 
 
    if uploaded_file is not None: 
        file_size = uploaded_file.size 
        if file_size > MAX_FILE_SIZE:  
            st.error('文件太大！请上传40MB以内的文件, 或者切分文件后再上传') 
            st.stop() 
 
        mime_type = uploaded_file.type 
 
        with st.spinner(text="文件处理中，请耐心等待，照片越大所需时间越久."): 
            with st.expander(f"log info:", expanded=True):       
                st.info(str(uploaded_file.name) + " - 正在识别.")    
                st.info(f"检测到的文件MIME类型: {mime_type}") 
 
                prompt_text = prompts[selected[1]] 
                model_type = "qwen-vl-max-latest" if selected[1] == 0 else "qwen-vl-ocr-latest" 
                 
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), mime_type)} 
                data = { 
                    "prompt": prompt_text, 
                    "model": model_type 
                } 
                 
                res = api_client.upload_file_get_json("/multimodal/vision/analyze", files=files, data=data) 
 
                if res and res.get("description"): 
                    st.info(str(uploaded_file.name) + " - 识别完成.") 
                    st.info(res["description"]) 
                else: 
                    st.error("识别失败或后端未返回结果") 
 
        st.success("done!") 
 
render = show
