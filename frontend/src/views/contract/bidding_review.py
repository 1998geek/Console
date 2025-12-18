import streamlit as st

def render():
    st.title(":material/policy: 标书智能审查")
    st.markdown("上传标书文档，进行要点抽取与合规性检查。")
    file = st.file_uploader("上传标书文件", type=["pdf", "docx"])
    with st.expander("审查选项"):
        st.checkbox("检查资质证书匹配")
        st.checkbox("检查财务审计年度一致性")
        st.checkbox("检查成功案例合同名称")
        st.checkbox("检查项目经理简历与技能")
        st.checkbox("检查授权书或承诺函盖章")
    run = st.button("开始审查", type="primary")
    if run:
        if file:
            st.info("TODO: 调用 api_client")
            st.success("审查任务已提交")
        else:
            st.warning("请上传文件")
