import streamlit as st

def render():
    st.title(":material/admin_panel_settings: 管理员控制台")
    tab1, tab2 = st.tabs(["用户管理", "审计日志"])
    with tab1:
        st.text_input("搜索用户")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("角色", ["admin", "user"], index=1)
        with col2:
            st.toggle("启用状态", value=True)
        st.button("保存变更", type="primary")
        st.info("TODO: 调用 api_client")
    with tab2:
        st.dataframe({"时间": [], "操作": [], "用户": []})
        st.info("TODO: 调用 api_client")
