import streamlit as st
import os
import sys

# 1. 路径修复：确保 Python 能找到同级目录下的模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 2. 加载环境变量 (本地调试用，Docker 环境会自动加载)
from dotenv import load_dotenv
load_dotenv() 

from sub_pages.init_sidebar import init_sidebar
from login import render_login_page

# 3. 页面基础配置 (必须是第一个 st 命令)
st.set_page_config(
    page_title="ComLan AI Portal (Refactored)", 
    page_icon=":material/home:", 
    layout="wide", 
    initial_sidebar_state="auto", 
    menu_items=None
)

# 4. 全局 Session 初始化
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None

# 5. 定义登出逻辑
def logout():
    st.write("### 退出登录")
    st.write("您确定要退出当前账号吗？")
    if st.button("确认退出", type="primary"):
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.is_admin = False
        st.rerun()

# 6. 启动导航控制
# init_sidebar 会接管页面的渲染：
# - 未登录 -> 渲染 login_page
# - 已登录 -> 渲染 Sidebar 导航栏
init_sidebar(render_login_page, logout)