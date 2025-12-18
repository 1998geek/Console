import streamlit as st
from src.services.api_client import api_client

def show():
    st.title("📄 标书智能检查系统 - 图片审核")
    st.write("请上传您的 `.docx` 格式标书文件，系统将自动提取包含图片的章节及其对应的文本内容。")
    st.info("💡 系统目前仅支持预览 JPG (JPEG) 和 PNG 格式的图片，其他格式（如 WMF, EMF, BMP 等）将被标记但无法显示。")
    st.write("上传 `.docx` 格式标书，系统将提取含图片的章节，并可启动AI模拟审核检查图文一致性、图片质量等问题。")
    uploaded_file = st.file_uploader("选择一个Word文档...", type=["docx"])
    if st.button("🚀 开始智能审核全部章节", type="primary", use_container_width=True):
        if not uploaded_file:
            st.warning("请上传一个文件以开始分析。")
            return
        with st.spinner("正在解析文档并进行智能审核..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            res = api_client.upload_file_get_json("/contract/review/bidding", files=files)
        if res and res.get("analysis"):
            st.success("✅ 所有章节均已审核完毕！")
            st.markdown("---")
            st.header("🏁 智能审核最终摘要")
            st.markdown(res["analysis"])
            base = uploaded_file.name.rsplit(".", 1)[0]
            output_name = st.text_input("保存文件名", value=f"{base}_标书合规审查报告.md", key=f"bidding_review_name_{uploaded_file.name}")
            st.download_button(
                label="📥 下载审核报告",
                data=res["analysis"].encode("utf-8"),
                file_name=output_name,
                mime="text/markdown"
            )
        else:
            st.error("解析失败或后端接口未适配 '标书图片审核' 逻辑。")

render = show
