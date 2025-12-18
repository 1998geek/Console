import streamlit as st

def render():
    st.title(":material/description: 合同智能初审")
    st.markdown("上传合同文件，进行结构化条款检查与风险提示。")
    file = st.file_uploader("上传合同文件", type=["pdf", "docx"])
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("合同类型", ["采购合同", "销售合同", "服务合同", "框架协议"], index=0)
    with col2:
        st.selectbox("审查侧重点", ["价格与付款", "交付与验收", "违约与赔偿", "保密与知识产权"], index=0)
    run = st.button("开始初审", type="primary")
    if run:
        if file:
            st.info("TODO: 调用 api_client")
            st.success("初审任务已提交")
        else:
            st.warning("请上传文件")
