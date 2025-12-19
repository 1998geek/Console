import streamlit as st
from src.services.api_client import api_client
from src.utils.ui import TaskProgress # [引入新工具]

def show():
    st.title(":material/image_search: 智能图片识别")

    if "img_rec_results" not in st.session_state:
        st.session_state.img_rec_results = []

    with st.container():
        st.markdown("💡 **说明**：上传图片，AI 将分析图片内容、提取文字或生成详细描述。")
        file = st.file_uploader("上传图片", type=["png", "jpg", "jpeg", "webp"])
        if file:
            st.image(file, caption="已上传图片预览", width=300)
        mode = st.radio("识别模式", ["通用场景描述", "OCR 文字提取", "物体检测"], horizontal=True)
        run = st.button("🚀 开始识别", type="primary", disabled=not file, use_container_width=True)

    if run and file:
        st.session_state.img_rec_results = [] 
        progress = TaskProgress(title="启动视觉模型...") # [使用新工具]
        
        try:
            progress.update(20, "正在预处理图片...")
            content = file.getvalue()
            files_payload = {"file": (file.name, content, file.type)}
            data_payload = {"mode": mode}
            
            progress.update(50, "⚡️ 正在进行 AI 视觉分析 (请稍候)...")
            res = api_client.post("/multimodal/image/analyze", files=files_payload, data=data_payload)
            
            progress.update(80, "分析完成，正在整理报告...")
            
            success = False
            result_text = ""
            if res and res.get("success", False): 
                result_text = res.get("data", {}).get("description", "识别成功，但未返回内容。")
                success = True
            elif res and "description" in res:
                result_text = res["description"]
                success = True
            
            if success:
                st.session_state.img_rec_results.append({
                    "original_name": file.name,
                    "result_text": result_text,
                    "mode": mode
                })
                progress.finish("✅ 识别完成！")
            else:
                progress.fail("❌ 识别失败")
                st.error("后端返回错误或格式无法解析。")
                
        except Exception as e:
            progress.fail("❌ 系统错误")
            st.error(f"Error: {e}")

    if st.session_state.img_rec_results:
        st.divider()
        st.subheader("识别结果")
        for i, res in enumerate(st.session_state.img_rec_results):
            with st.container(border=True):
                st.markdown(f"**🖼️ 来源**: `{res['original_name']}` | **模式**: `{res['mode']}`")
                st.markdown("### 分析报告")
                st.markdown(res['result_text'])
                st.divider()
                
                # [关键] 底部对齐
                c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
                with c1:
                    default_txt_name = f"result_{res['original_name']}.md"
                    new_name = st.text_input("结果文件名:", value=default_txt_name, key=f"rename_img_{i}")
                with c2:
                    st.download_button(
                        label="⬇️ 下载结果",
                        data=res['result_text'],
                        file_name=new_name,
                        mime="text/markdown",
                        type="primary",
                        use_container_width=True,
                        key=f"dl_img_{i}"
                    )

render = show