import streamlit as st
import os
import base64
from api_client import login_request, get_current_user_info

def render_login_page():    
    # --- 1. 资源加载 ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    background_path = os.path.join(current_dir, 'static', 'images', 'background.jpg')
    
    if os.path.exists(background_path):
        with open(background_path, "rb") as f:
            background_image = base64.b64encode(f.read()).decode()
    else:
        background_image = None

    # --- 2. Session 状态初始化 ---
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # --- 3. 注入 CSS 样式 ---
        background_style = f"""
        background: url("data:image/jpg;base64,{background_image}") no-repeat center center fixed;
        """ if background_image else "background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);"
        
        st.markdown(f"""
        <style>
            .stApp {{
                {background_style}
                background-size: cover !important;
                min-height: 100vh !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            header, div[data-testid="stHeader"], section[data-testid="stSidebar"] {{
                display: none !important;
            }}
            .st-emotion-cache-18ni7ap, .st-emotion-cache-1d391kg {{
                background: none !important;
            }}
            .main .block-container {{
                padding-top: 2rem !important;
                padding-bottom: 2rem !important;
                max-width: 100% !important;
            }}
            .stButton>button {{
                border-radius: 10px;
                background: #0072C6;
                color: white;
                width: 100%;
                padding: 0.8rem;
                font-weight: bold;
            }}
            .stButton>button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 114, 198, 0.4);
            }}
        </style>
        """, unsafe_allow_html=True)

        # --- 4. 页面布局 ---
        col1, col2, col3 = st.columns([1, 4, 1])
        
        with col2:
            with st.container():
                st.markdown("<div class='form-card'>", unsafe_allow_html=True)
                
                st.markdown("""
                    <div style='text-align: center; margin-bottom: 2rem;'>
                        <h1 style='color: #0072C6; margin-bottom: 0.5rem;'>⚙️ 昆仑联通AI增效计划</h1>
                        <p style='color: #fff;'>您的智能对话分析专家</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # === 修改点：添加默认 value ===
                username = st.text_input("用户名", value="admin")
                password = st.text_input("密码", type="password", value="admin123456")
                
                if st.button("登录"):
                    # 1. 后门逻辑 (保留用于测试 UI)
                    if username == "admin" and password == "admin123456":
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.token = "fake-admin-token-for-testing"
                        st.rerun()

                    # 2. 真实 API 逻辑
                    token_data = login_request(username, password)
                    
                    if token_data and "access_token" in token_data:
                        st.session_state.logged_in = True
                        st.session_state.token = token_data["access_token"]
                        st.rerun()
                    else:
                        st.error("用户名或密码错误")
    
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("""
                <div style='text-align: center; padding: 20px; color: #fff; font-size: 14px; margin-top: 20px;'>
                    Copyright © 2025 北京昆仑联通 版权所有 All Rights Reserved
                </div>
            """, unsafe_allow_html=True)
