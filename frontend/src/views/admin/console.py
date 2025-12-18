import streamlit as st 
import pandas as pd 
from src.services.api_client import api_client 
 
def show(): 
    st.title("🛡️ 管理员控制台") 
    st.write("在这里管理系统用户、查看系统状态。") 
 
    if not st.session_state.get("is_admin", False): 
        st.error("❌ 您没有权限访问此页面。") 
        st.stop() 
 
    tab1, tab2 = st.tabs(["📊 用户管理", "➕ 添加新用户"]) 
 
    with tab1: 
        users = api_client.get("/admin/users") 
        if not users: 
            st.info("暂无用户或无法连接后端。") 
        else: 
            users_df = pd.DataFrame(users) 
            st.header("仪表盘概览", anchor=False) 
            col1, col2, col3 = st.columns(3) 
            with col1: 
                st.metric(label="👤 用户总数", value=len(users_df)) 
            st.divider() 
 
            search_query = st.text_input("🔍 搜索用户", placeholder="按用户名或邮箱搜索...") 
            if search_query: 
                mask = users_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1) 
                filtered_df = users_df[mask] 
            else: 
                filtered_df = users_df 
 
            st.write(f"共显示 **{len(filtered_df)}** 位用户。") 
 
            header_cols = st.columns([3, 4, 2, 2]) 
            header_cols[0].markdown("**用户名**") 
            header_cols[1].markdown("**邮箱**") 
            header_cols[2].markdown("**操作**") 
            header_cols[3].markdown("") 
            st.divider() 
 
            for index, user in filtered_df.iterrows(): 
                username = user["username"] 
                email = user.get("email") or "—" 
                 
                row_cols = st.columns([3, 4, 2, 2], vertical_alignment="center") 
                row_cols[0].text(username) 
                row_cols[1].text(email) 
                 
                with row_cols[2]: 
                    with st.popover("重置密码", use_container_width=False, help=f"为 {username} 设置新密码"): 
                        st.markdown(f"为 **`{username}`** 设置新密码") 
                        with st.form(f"reset_pw_{username}", border=False): 
                            new_password = st.text_input("新密码", type="password", key=f"pw_{username}") 
                            if st.form_submit_button("✓ 确认", use_container_width=True, type="primary"): 
                                if new_password: 
                                    res = api_client.post(f"/admin/users/{username}/reset-password", json={"password": new_password}) 
                                    if res: 
                                        st.toast(f"用户 {username} 的密码已重置。", icon="✅") 
                                    else: 
                                        st.error("密码重置失败！") 
                                else: 
                                    st.warning("密码不能为空。") 
 
                with row_cols[3]: 
                    if username != "admin": 
                        if st.button("删除", key=f"del_btn_{username}", type="secondary", use_container_width=True): 
                            delete_user_dialog(username) 
 
    with tab2: 
        with st.form("add_user_form"): 
            st.subheader("创建新用户账户", anchor=False) 
            col1, col2 = st.columns(2) 
            with col1: 
                new_username = st.text_input("用户名 *", placeholder="例如: user01") 
            with col2: 
                new_password = st.text_input("密码 *", type="password", placeholder="输入安全的密码") 
 
            new_email = st.text_input("邮箱（可选）", placeholder="例如: user@example.com") 
             
            if st.form_submit_button("✓ 添加用户", use_container_width=True, type="primary"): 
                if new_username and new_password: 
                    payload = {"username": new_username, "password": new_password, "email": new_email} 
                    res = api_client.post("/admin/users", json=payload) 
                    if res: 
                        st.success("用户添加成功！请切换到“用户管理”选项卡查看。") 
                    else: 
                        st.error("用户添加失败，可能用户名已存在。") 
                else: 
                    st.warning("请务必填写用户名和密码。") 
 
@st.dialog("确认删除操作") 
def delete_user_dialog(username): 
    st.warning(f"您确定要永久删除用户 **{username}** 吗？此操作无法撤销。") 
    col1, col2 = st.columns(2) 
    if col1.button("确认删除", type="primary", use_container_width=True): 
        res = api_client.delete(f"/admin/users/{username}") 
        if res: 
            st.toast(f"用户 {username} 已被删除。", icon="🗑️") 
            st.rerun() 
        else: 
            st.error("删除失败") 
    if col2.button("取消", use_container_width=True): 
        st.rerun() 
 
render = show 
