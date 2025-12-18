import streamlit as st
from src.services.api_client import api_client

def show():
    st.title(":material/description: AI 合同智能初审助手")
    st.markdown(
        "上传您的合同文件（.docx / pdf），选择需要审核的要点，AI 将为您提供一份初步的审核报告。"
        "注意：docx 请使用Microsoft Office 官方文件，其他软件导出的兼容格式可能会导致翻译错误。"
        "审核只针对合同文本内容，不包括图片"
    )
    uploaded_file = st.file_uploader(
        "上传合同文件",
        type=["docx", "pdf"],
        help="请上传 .docx .pdf 格式的合同文件。"
    )
    review_options = ["合同要点识别", "风险识别", "核心条款摘要", "要素完整性检查", "提出修改建议"]
    selected_points = st.multiselect(
        "选择您关注的审核要点 (可多选)",
        options=review_options,
        default=review_options[:2]
    )
    if st.button("🚀 开始审核", type="primary"):
        if not uploaded_file:
            st.warning("请先上传一个合同文件。")
            return
        if not selected_points:
            st.warning("请至少选择一个审核要点。")
            return
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        data = {"review_points": selected_points}
        with st.spinner("AI 正在深度分析合同，请稍候..."):
            res = api_client.upload_file_get_json("/contract/review/file", files=files, data=data)
        if res and res.get("analysis"):
            st.subheader("AI 审核报告")
            st.markdown(res["analysis"])
            st.markdown("---")
            st.caption("**免责声明**: 本报告由AI生成，仅供初步参考，不能替代专业法律顾问的正式意见。")
            base = uploaded_file.name.rsplit(".", 1)[0]
            output_name = st.text_input("保存文件名", value=f"{base}_合同初审报告.md", key=f"contract_review_name_{uploaded_file.name}")
            st.download_button(
                label="📥 下载审核报告",
                data=res["analysis"].encode("utf-8"),
                file_name=output_name,
                mime="text/markdown"
            )
        else:
            st.error("审核失败，请检查后端服务日志。")

render = show
