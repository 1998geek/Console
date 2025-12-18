import streamlit as st

def render():
    st.title(":material/settings: Prompt 配置")
    st.markdown("配置审查模板与批量规则。")
    col1, col2 = st.columns(2)
    with col1:
        prompt = st.text_area("单次审查 Prompt", height=200, value="")
        save1 = st.button("保存单次配置", type="primary")
    with col2:
        batch_prompt = st.text_area("批量审查 Prompt", height=200, value="")
        save2 = st.button("保存批量配置", type="primary")
    if save1 or save2:
        st.info("TODO: 调用 api_client")
        st.success("配置已保存")
