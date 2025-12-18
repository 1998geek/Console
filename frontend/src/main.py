
import os
import base64
import importlib
import streamlit as st
from src.services import auth_service

# -----------------------------------------------------------------------------
# 1. 页面配置与基础样式
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ComLan AI Console", 
    page_icon=":material/token:", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

def _load_bg_base64() -> str | None:
    # 尝试加载背景图
    candidates = [
        # Relative to src/main.py -> ../images/background.jpg
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "images", "background.jpg")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "images", "background.jpg")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "background.jpg")),
    ]
    for bg_path in candidates:
        if os.path.exists(bg_path):
            with open(bg_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

def _inject_login_css():
    bg = _load_bg_base64()
    style = f'background: url("data:image/jpg;base64,{bg}") no-repeat center center fixed;' if bg else "background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);"
    st.markdown(
        f"""
        <style>
            .stApp {{
                {style}
                background-size: cover !important;
                min-height: 100vh !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            /* 隐藏登录页的侧边栏和顶部 */
            header, div[data-testid="stHeader"], section[data-testid="stSidebar"] {{ display: none !important; }}
            .st-emotion-cache-18ni7ap, .st-emotion-cache-1d391kg {{ background: none !important; }}
            .main .block-container {{
                padding-top: 2rem !important;
                padding-bottom: 2rem !important;
                max-width: 100% !important;
            }}
            /* 登录按钮样式 */
            .stButton>button {{
                border-radius: 10px;
                background: #0072C6;
                color: white;
                width: 100%;
                padding: 0.8rem;
                font-weight: bold;
                border: none;
            }}
            .stButton>button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 114, 198, 0.4);
            }}

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
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# 2. 动态加载视图函数
# -----------------------------------------------------------------------------
def _run_view(module_path: str):
    try:
        mod = importlib.import_module(module_path)
        if hasattr(mod, "render"):
            mod.render()
        elif hasattr(mod, "show"):
            mod.show()
        else:
            st.error(f"模块 {module_path} 中未找到 render 或 show 函数")
    except ImportError:
        st.error(f"找不到模块: {module_path}")
    except Exception as e:
        st.error(f"加载页面出错: {e}")

# --- 视图包装函数 (仅保留核心功能) ---

# 文档工具
def show_cloud_trans(): _run_view("src.views.doc_tools.cloud_trans")
def show_local_trans(): _run_view("src.views.doc_tools.local_trans")
def show_numbering():   _run_view("src.views.doc_tools.numbering")

# 合同助手
def show_contract_review(): _run_view("src.views.contract.contract_review")
def show_biding_review():   _run_view("src.views.contract.bidding_review")
def show_docx_diff():       _run_view("src.views.contract.diff")

# 智能体集成
def show_dify():            _run_view("src.views.agent.dify")
def show_xinference():      _run_view("src.views.agent.xinference")
def show_multimodal_chat(): _run_view("src.views.agent.multimodal_chat")

# 多模态应用
def show_sora():            _run_view("src.views.multimodal.sora")
def show_img_recognize():   _run_view("src.views.multimodal.img_recognize")

# 自动化配置
def show_prompt_config():   _run_view("src.views.automation.prompt_config")
def show_newsletter():      _run_view("src.views.automation.newsletter")

# 系统管理
def show_admin_console():   _run_view("src.views.admin.console")

# -----------------------------------------------------------------------------
# 3. 登录与注销逻辑
# -----------------------------------------------------------------------------
def render_login_page():
    _inject_login_css()
    if "login_username" not in st.session_state:
        st.session_state.login_username = "admin"
    if "login_password" not in st.session_state:
        st.session_state.login_password = "admin123456"
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        with st.container():
            st.markdown(
                """
                <div style='text-align: center; margin-bottom: 2rem; padding-top: 5vh;'>
                    <h1 style='color: #0072C6; font-size: 2.5rem;'>⚙️ 昆仑联通AI增效计划</h1>
                    <p style='color: #fff; font-size: 1.1rem;'>您的智能对话分析专家</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            username = st.text_input("用户名", key="login_username")
            password = st.text_input("密码", type="password", key="login_password")

            if st.button("登录"):
                result = auth_service.login(username, password)
                if result["success"]:
                    st.session_state.logged_in = True
                    st.session_state.token = result.get("token")
                    st.session_state.is_admin = (username == "admin")
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error(f"登录失败: {result.get('message', '未知错误')}")

        st.markdown(
            """
            <div style='text-align: center; padding: 20px; color: #fff; font-size: 14px; margin-top: 20px;'>
                Copyright © 2025 北京昆仑联通 版权所有 All Rights Reserved
            </div>
            """,
            unsafe_allow_html=True
        )

def logout():
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.is_admin = False
    st.rerun()

# -----------------------------------------------------------------------------
# 4. 导航与路由配置
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if st.session_state.logged_in:
    
    # === 定义页面对象 ===
    
    # 1. 文档工具 (Doc Tools)
    pg_cloud_trans = st.Page(show_cloud_trans, title="云端文档翻译", icon=":material/cloud_sync:", url_path="cloud-trans")
    pg_local_trans = st.Page(show_local_trans, title="本地模型翻译", icon=":material/translate:", url_path="local-trans")
    pg_numbering   = st.Page(show_numbering,   title="文档自动编号", icon=":material/format_list_numbered:", url_path="doc-numbering")

    # 2. 合同助手 (Contract Assistant)
    pg_contract = st.Page(show_contract_review, title="合同智能初审", icon=":material/gavel:", url_path="contract-review")
    pg_biding   = st.Page(show_biding_review,   title="标书合规审查", icon=":material/fact_check:", url_path="biding-review")
    pg_diff     = st.Page(show_docx_diff,       title="文档智能比对", icon=":material/difference:", url_path="doc-diff")

    # 3. 智能体集成 (Agent Integration)
    pg_dify       = st.Page(show_dify,            title="Dify 智能体",       icon=":material/smart_toy:", url_path="dify-chat")
    pg_xinference = st.Page(show_xinference,      title="本地模型对话",       icon=":material/dns:", url_path="local-chat")
    pg_multimodal = st.Page(show_multimodal_chat, title="多模态对话助手",     icon=":material/perm_media:", url_path="vision-chat")

    # 4. 多模态应用 (Multimodal Apps)
    pg_vision = st.Page(show_img_recognize, title="图片智能分析", icon=":material/image_search:", url_path="image-analysis")
    pg_sora   = st.Page(show_sora,          title="Sora 视频生成", icon=":material/movie:", url_path="video-gen")

    # 5. 自动化配置 (Automation)
    pg_prompt = st.Page(show_prompt_config, title="Prompt 规则配置", icon=":material/tune:", url_path="prompt-settings")
    pg_news   = st.Page(show_newsletter,    title="AI 简报设置",     icon=":material/newspaper:", url_path="newsletter-settings")

    # 6. 系统管理 (Account)
    pg_admin  = st.Page(show_admin_console, title="管理员控制台", icon=":material/admin_panel_settings:", url_path="admin-console")
    pg_logout = st.Page(logout,             title="退出登录",     icon=":material/logout:", url_path="logout")

    # === 构建导航结构 ===
    nav_structure = {
        "📂 文档工具 (Doc Tools)": [pg_cloud_trans, pg_local_trans, pg_numbering],
        "⚖️ 合同助手 (Contract)":  [pg_contract, pg_biding, pg_diff],
        "🤖 智能体 (Agents)":      [pg_dify, pg_xinference, pg_multimodal],
        "👁️ 多模态 (Vision/Video)": [pg_vision, pg_sora],
        "⚙️ 自动化 (Config)":       [pg_prompt, pg_news],
        "👤 账户 (Account)":        [pg_admin, pg_logout] if st.session_state.is_admin else [pg_logout]
    }

    pg = st.navigation(nav_structure)
    pg.run()

else:
    # 未登录状态：显示登录页
    pg = st.navigation([st.Page(render_login_page, title="登录", url_path="login")])
    pg.run()
