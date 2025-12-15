import streamlit as st
import hashlib
import pandas as pd
from function.db_manager import DatabaseManager

class AdminPage:
    """
    A class to encapsulate the admin page functionality, providing user management
    and system overview capabilities.
    """

    def __init__(self):
        """Initializes the database manager."""
        self.db_manager = DatabaseManager()
        # Initialize session state for the delete confirmation dialog
        if 'user_to_delete' not in st.session_state:
            st.session_state.user_to_delete = None

    def hash_password(self, password: str) -> str:
        """Hashes a password using SHA256 for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _render_dashboard_metrics(self, users_df: pd.DataFrame):
        """
        Renders the top-level dashboard metrics.
        
        Args:
            users_df: A DataFrame containing all user data.
        """
        st.header("仪表盘概览", anchor=False)
        total_users = len(users_df)

        # Use columns for a clean metric layout
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="👤 用户总数", value=total_users)
        # These columns are placeholders for future metrics
        with col2:
            pass
        with col3:
            pass
        st.divider()

    def _render_user_management_tab(self):
        """
        Renders the main user management tab, including the user list,
        search, and actions like password reset and deletion.
        """
        all_users = self.db_manager.get_all_users()
        if not all_users:
            st.info("系统中暂无用户。")
            return

        users_df = pd.DataFrame(all_users)
        
        # --- Dashboard and Search ---
        self._render_dashboard_metrics(users_df)
        
        search_query = st.text_input("🔍 搜索用户", placeholder="按用户名或邮箱搜索...")
        
        if search_query:
            mask = users_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            filtered_df = users_df[mask]
        else:
            filtered_df = users_df

        if filtered_df.empty:
            st.warning("未找到匹配的用户。")
            return
            
        st.write(f"共显示 **{len(filtered_df)}** 位用户。")

        # --- Custom User Table with Actions ---
        # Define headers for our custom table
        header_cols = st.columns([3, 4, 2, 2])
        header_cols[0].markdown("**用户名**")
        header_cols[1].markdown("**邮箱**")
        header_cols[2].markdown("**操作**")
        header_cols[3].markdown("") # Leave the last column header empty for alignment
        st.divider()

        # Display each user row
        for index, user in filtered_df.iterrows():
            username = user["username"]
            email = user.get("email") if pd.notna(user.get("email")) else "—"
            
            row_cols = st.columns([3, 4, 2, 2], vertical_alignment="center")
            
            row_cols[0].text(username)
            row_cols[1].text(email)
            
            # --- Reset Password Action (using Popover) ---
            with row_cols[2]:
                with st.popover("重置密码", use_container_width=False, help=f"为 {username} 设置新密码"):
                    st.markdown(f"为 **`{username}`** 设置新密码")
                    with st.form(f"reset_pw_{username}", border=False):
                        new_password = st.text_input("新密码", type="password", key=f"pw_{username}")
                        if st.form_submit_button("✓ 确认", use_container_width=True, type="primary"):
                            if new_password:
                                hashed_password = self.hash_password(new_password)
                                if self.db_manager.update_user_password(username, hashed_password):
                                    st.toast(f"用户 {username} 的密码已重置。", icon="✅")
                                else:
                                    st.error("密码重置失败！")
                            else:
                                st.warning("密码不能为空。")

            # --- Delete User Action (with Confirmation Dialog) ---
            with row_cols[3]:
                if username != "admin": # Prevent the admin user from being deleted
                    if st.button("删除", key=f"del_btn_{username}", type="secondary", use_container_width=True):
                        # Set the user to be deleted in session state to trigger the dialog
                        st.session_state.user_to_delete = username
                        st.rerun() # Rerun to open the dialog immediately

        # This part will render the dialog if a user has been selected for deletion
        if st.session_state.user_to_delete:
            self._render_delete_dialog()

    def _render_delete_dialog(self):
        """Renders a confirmation dialog for deleting a user."""
        username = st.session_state.user_to_delete

        @st.dialog("确认删除操作")
        def confirm_delete():
            st.warning(f"您确定要永久删除用户 **{username}** 吗？此操作无法撤销。")
            
            btn_cols = st.columns(2)
            # Confirm button
            if btn_cols[0].button("确认删除", type="primary", use_container_width=True):
                if self.db_manager.delete_user(username):
                    st.toast(f"用户 {username} 已被删除。", icon="🗑️")
                    st.session_state.user_to_delete = None # Reset state
                    st.rerun()
                else:
                    st.error("删除失败！")
            # Cancel button
            if btn_cols[1].button("取消", use_container_width=True):
                st.session_state.user_to_delete = None # Reset state
                st.rerun()
        
        # This function call opens the dialog
        confirm_delete()

    def _render_add_user_tab(self):
        """Renders the form for adding a new user."""
        with st.form("add_user_form"):
            st.subheader("创建新用户账户", anchor=False)
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("用户名 *", placeholder="例如: user01")
            with col2:
                new_password = st.text_input("密码 *", type="password", placeholder="输入安全的密码")

            new_email = st.text_input("邮箱（可选）", placeholder="例如: user@example.com")
            
            st.caption("带 * 号为必填项。")

            if st.form_submit_button("✓ 添加用户", use_container_width=True, type="primary"):
                if new_username and new_password:
                    hashed_password = self.hash_password(new_password)
                    if self.db_manager.add_user(new_username, hashed_password, new_email):
                        st.success("用户添加成功！请切换到“用户管理”选项卡查看。")
                    else:
                        st.error("用户添加失败，可能用户名已存在。")
                else:
                    st.warning("请务必填写用户名和密码。")

    def render(self):
        """Renders the entire admin page with its tabs."""
        st.title("🛡️ 管理员控制台")
        st.write("在这里管理系统用户、查看系统状态。")

        tab1, tab2 = st.tabs(["📊 用户管理", "➕ 添加新用户"])

        with tab1:
            self._render_user_management_tab()

        with tab2:
            self._render_add_user_tab()


def render():
    """
    Entry point function to render the page.
    It performs an authorization check before rendering the content.
    """
    # This check ensures only admins can see the page.
    # It assumes 'is_admin' is set in the session_state during login.
    if not st.session_state.get("is_admin", False):
        st.error("❌ 您没有权限访问此页面。")
        st.stop()

    page = AdminPage()
    page.render()


# Main function for standalone testing
if __name__ == "__main__":
    # To test this page directly, we can simulate an admin login
    st.session_state["is_admin"] = True
    st.session_state["username"] = "admin"
    
    render()
