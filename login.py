import streamlit as st
import os
import hashlib
from function.db_manager import DatabaseManager

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def render_login_page():    
        
    # 读取并编码背景图片
    background_path = os.path.join(os.path.dirname(__file__), 'images', 'background.jpg')
    if os.path.exists(background_path):
        import base64
        with open(background_path, "rb") as f:
            background_image = base64.b64encode(f.read()).decode()
    else:
        background_image = None

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # Inject custom CSS styles
        background_style = f"""
        background: url("data:image/jpg;base64,{background_image}") no-repeat center center fixed;
        """ if background_image else "background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);"
        
        st.markdown(f"""
        <style>
            /* 修改 Streamlit 的默认样式 */
            .stApp {{
                {background_style}
                background-size: cover !important;
                min-height: 100vh !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            /* 隐藏所有顶部元素 */
            header, div[data-testid="stHeader"], section[data-testid="stSidebar"] {{
                display: none !important;
            }}
            
            /* 移除所有背景 */
            .st-emotion-cache-18ni7ap, .st-emotion-cache-1d391kg {{
                background: none !important;
            }}
            
            /* 确保内容从顶部开始 */
            .main .block-container {{
                padding-top: 2rem !important;
                padding-bottom: 2rem !important;
                max-width: 100% !important;
            }}

            /* 其他样式保持不变 */
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
            
            /* Tab styles */
            [data-baseweb="tab-list"] {{
                gap: 10px;
            }}
            
            [data-baseweb="tab"] {{
                padding: 12px 30px;
                border-radius: 30px;
                background: #f0f0f0;
                transition: all 0.3s;
                color: #666;
            }}

            [data-baseweb="tab"]:hover {{
                background: #e0e0e0;
            }}
            
            [data-baseweb="tab"][aria-selected="true"] {{
                background: #0072C6;
                color: white;
            }}
        </style>
        """, unsafe_allow_html=True)

        # Create a responsive layout
        col1, col2, col3 = st.columns([1, 4, 1])
        
        with col2:
            # Add card container
            with st.container():
                st.markdown("<div class='form-card'>", unsafe_allow_html=True)
                
                # Add title and icon
                st.markdown("""
                    <div style='text-align: center; margin-bottom: 2rem;'>
                        <h1 style='color: #0072C6; margin-bottom: 0.5rem;'>⚙️ 昆仑联通AI增效计划</h1>
                        <p style='color: #fff;'>您的智能对话分析专家</p>
                    </div>
                """, unsafe_allow_html=True)
                
                db_manager = DatabaseManager()
                
                username = st.text_input("用户名")
                password = st.text_input("密码", type="password")
                
                if st.button("登录"):
                    # 检查是否是管理员登录
                    if username == "admin" and password == "admin123456":
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.rerun()
                    else:
                        # 验证普通用户
                        hashed_password = hash_password(password)
                        if db_manager.verify_user(username, hashed_password):
                            st.session_state.logged_in = True
                            st.session_state.is_admin = False
                            st.rerun()
                        else:
                            st.error("用户名或密码错误")
    
            st.markdown("</div>", unsafe_allow_html=True)  # End card container
            
            # 添加版权声明
            st.markdown("""
                <div style='text-align: center; padding: 20px; color: #fff; font-size: 14px; margin-top: 20px;'>
                    Copyright © 2025 北京昆仑联通 版权所有 All Rights Reserved
                </div>
            """, unsafe_allow_html=True)
