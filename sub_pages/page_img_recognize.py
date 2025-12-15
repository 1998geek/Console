import streamlit as st
from io import BytesIO 
import uuid
from app_config.keys_config import ALIYUN_AI_ENDPOINT, ALIYUN_AI_TOKEN
from openai import OpenAI
import base64

st.subheader(':material/frame_inspect: 图片识别')
category = [["着装识别", 0],
    ["票据识别", 1],
    ["条形码识别", 2],]

prompts = ["⽬标区域 ：⾐服上的⽂字,⽂字内容 ：⾐服上的⽂字可能包括品牌名称 输出格式 ：请以⽂本形式输出 是否在衣服上检测到了⽂字？如果有，请输出⽂字内容。请注意，可能会有多个⽂字内容。请将所有检测到的⽂字内容以结构化⽂本形式输出结果。",  
           "请使⽤OCR技术识别并提取图⽚中票据上的所有关键信息，包括起点站、终点站、通⾏时间、⾦额以及其他标识，并以结构化⽂本形式输出结果。",
           "请使⽤OCR技术识别并提取图⽚中的条形码内容（字母开头的编码 如A001808250593）及其下⽅的⽂字信息（如验证码、产品型号、产品代码），并以结构化⽂本形式输出结果。"]

type = ["jpg", "jpeg", "png","webp"]
MAX_FILE_SIZE = 40 * 1024 * 1024    

selected = st.selectbox("please select the category you want to recognize",
                        options=category, format_func=lambda x: x[0], index=None, key="selectbox_category")

disabled = True
if selected is not None:
     disabled = False
else:
    disabled = True

uploaded_file = st.file_uploader("Please Choose a file you want to recognize and make sure the file is less than 40 MB",
                                  type=type, disabled =disabled)
if uploaded_file is not None:

    file_size = uploaded_file.getbuffer().nbytes  
    if file_size > MAX_FILE_SIZE:  
            st.error('文件太大！请上传40MB以内的文件, 或者切分文件后再上传') 
            st.stop()

    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    # img_file = BytesIO(bytes_data) 
     # 将字节数据进行Base64编码
    base64_encoded_data = base64.b64encode(bytes_data)
    base64_image_string = base64_encoded_data.decode('utf-8')
    mime_type = uploaded_file.type

    with st.spinner(text="文件处理中，请耐心等待，照片越大所需时间越久."):
  
        with st.expander(f"log info:", expanded=True):       
            st.info(str(uploaded_file.name) + " - 正在识别.")    
            st.info(f"检测到的文件MIME类型: {mime_type}")

            # 根据MIME类型构建符合要求的Data URI
            data_uri = None
            if mime_type == "image/png":
                data_uri = f"data:image/png;base64,{base64_image_string}"
            elif mime_type == "image/jpeg": # .jpg 和 .jpeg 通常都是 image/jpeg
                data_uri = f"data:image/jpeg;base64,{base64_image_string}"
            elif mime_type == "image/webp":
                data_uri = f"data:image/webp;base64,{base64_image_string}"
            else:
                # 如果上传的文件类型不在预期内，但您在st.file_uploader中限制了类型，
                # 理论上不会走到这里。但为了健壮性，可以添加处理。
                st.error(f"不支持的文件类型: {mime_type}。请确保上传的是支持的图片格式 (PNG, JPEG, WEBP)。")
                st.stop()

            content = [
                {
                    "type": "image_url",
                    "image_url": {"url": data_uri},
                    # 输入图像的最小像素阈值，小于该值图像会按原比例放大，直到总像素大于min_pixels
                    "min_pixels": 28 * 28 * 4,
                    # 输入图像的最大像素阈值，超过该值图像会按原比例缩小，直到总像素低于max_pixels
                    "max_pixels": 28 * 28 * 8192
                },
                {"type": "text", "text": prompts[selected[1]]},
            ]

            client = OpenAI(
                api_key=ALIYUN_AI_TOKEN,
                base_url=ALIYUN_AI_ENDPOINT,
            )

            if selected[1] == 0:
                model = "qwen-vl-max-latest"
            else:
                model = "qwen-vl-ocr-latest"

            completion = client.chat.completions.create(
                # model="qwen-vl-ocr-latest", # 可按需替换模型
                model = model,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ])

            st.info(str(uploaded_file.name) + " - 识别完成.")
            st.info(completion.choices[0].message.content)

    st.success("done!")