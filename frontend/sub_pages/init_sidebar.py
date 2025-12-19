
import streamlit as st

def init_sidebar(login_func, logout_func):
    """
    管理侧边栏导航和页面路由
    """
    if st.session_state.get('logged_in', False):
        
        # --- 1. 定义功能页面 ---
        
        # [A] 登出页 (URL路径默认为 /logout)
        logout_page = st.Page(logout_func, title="退出登录", icon=":material/logout:")

        # [B] 文档翻译页
        page_translate = st.Page("sub_pages/page_translate.py", title="文档翻译 (新版)", icon=":material/g_translate:")

        # [C] 管理员页面 (仅管理员可见)
        admin_pages = []
        if st.session_state.get('is_admin', False):
            # 修复点：添加 url_path="admin"，避免与 logout 冲突
            page_admin = st.Page(logout_func, title="管理员控制台", icon=":material/admin_panel_settings:", url_path="admin") 
            admin_pages.append(page_admin)

        # --- 2. 构建导航结构 ---
        nav_structure = {
            "Doc Translation": [page_translate],
            "Account": [logout_page]
        }
        
        # 如果有管理员菜单
        if admin_pages:
            nav_structure["Admin"] = admin_pages

        pg = st.navigation(nav_structure)
        
    else:
        # --- 3. 未登录状态 ---
        login_page = st.Page(login_func, title="用户登录", icon=":material/login:")
        pg = st.navigation([login_page])

    pg.run()
