import streamlit as st
from src.services.api_client import api_client

def show():
    st.title(":material/admin_panel_settings: 管理员控制台")
    if st.session_state.get("user_info", {}).get("is_admin") is not True:
        st.info("提示：当前未检测到管理员信息，将依赖后端权限校验。")
    with st.spinner("加载用户数据..."):
        try:
            data = api_client.get("/admin/users")
        except Exception as e:
            msg = str(e)
            if "403" in msg or "权限不足" in msg:
                st.error("需要管理员权限")
                return
            st.error(f"加载失败: {msg}")
            return
    total = len(data) if isinstance(data, list) else 0
    st.metric("总用户数", total)
    if total > 0:
        cols_to_show = ["id", "username", "email", "created_at", "is_admin"]
        rows = [{k: row.get(k) for k in cols_to_show} for row in data]
        st.dataframe(rows, use_container_width=True)

render = show
