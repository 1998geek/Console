import os
import base64
import importlib
import streamlit as st
from src.services import auth_service

# 设置页面配置
st.set_page_config(page_title="ComLan", page_icon=":material/home:", layout="wide", initial_sidebar_state="auto", menu_items=None)

def _load_bg_base64() -> str | None:
    """加载背景图片并转换为 base64 字符串"""
    try:
        # 尝试多个可能的路径加载背景图
        candidates = [
            "/app/frontend/images/background.jpg", # Docker 容器路径
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "images", "background.jpg")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "images", "background.jpg")),
        ]
        for bg_path in candidates:
            if os.path.exists(bg_path):
                with open(bg_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return None

def _inject_login_css():
    """注入登录页面的 CSS 样式"""
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
            header, div[data-testid="stHeader"], section[data-testid="stSidebar"] {{ display: none !important; }}
            .st-emotion-cache-18ni7ap, .st-emotion-cache-1d391kg {{ background: none !important; }}
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
        """,
        unsafe_allow_html=True,
    )

def render_login_page():
    """渲染登录页面"""
    _inject_login_css()
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        with st.container():
            st.markdown("<div class='form-card'>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style='text-align: center; margin-bottom: 2rem;'>
                    <h1 style='color: #0072C6; margin-bottom: 0.5rem;'>⚙️ 昆仑联通AI增效计划</h1>
                    <p style='color: #fff;'>您的智能对话分析专家</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            username = st.text_input("用户名", key="login_username")
            password = st.text_input("密码", type="password", key="login_password")
            if st.button("登录", key="btn_login"):
                result = auth_service.login(username, password)
                if result["success"]:
                    st.session_state.logged_in = True
                    # 这里可以根据后端返回补充角色判断
                    # st.session_state.is_admin = result.get("is_admin", False) 
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error(f"登录失败: {result['message']}")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='text-align: center; padding: 20px; color: #fff; font-size: 14px; margin-top: 20px;'>
                Copyright © 2025 北京昆仑联通 版权所有 All Rights Reserved
            </div>
            """,
            unsafe_allow_html=True,
        )

def logout():
    """退出登录"""
    st.write("您确定要退出登录吗？")
    if st.button("退出登录", type="primary"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        if "token" in st.session_state:
            del st.session_state.token
        st.rerun()

def _run_view(module_path: str, placeholder_text: str = "TODO: 调用 api_client"):
    """动态加载并运行视图模块"""
    try:
        mod = importlib.import_module(module_path)
        fn = getattr(mod, "render", None)
        if callable(fn):
            return fn()
    except ImportError:
         st.error(f"找不到模块: {module_path}")
    except Exception as e:
        st.error(f"加载页面失败: {e}")
    st.info(placeholder_text)

# --- 视图函数定义 ---

def show_cloud_trans():
    _run_view("src.views.doc_tools.cloud_trans")

def show_local_trans():
    _run_view("src.views.doc_tools.local_trans")

def show_numbering():
    _run_view("src.views.doc_tools.numbering")

def show_contract_review():
    _run_view("src.views.contract.contract_review")

def show_biding_review():
    _run_view("src.views.contract.bidding_review")

def show_docx_diff():
    _run_view("src.views.contract.diff")

def show_dify():
    _run_view("src.views.agent.dify")

def show_xinference():
    _run_view("src.views.agent.xinference")

def show_multimodal_chat():
    _run_view("src.views.agent.multimodal_chat")

def show_sora():
    _run_view("src.views.multimodal.sora")

def show_img_recognize():
    _run_view("src.views.multimodal.img_recognize")

def show_prompt_config():
    _run_view("src.views.automation.prompt_config")

def show_newsletter():
    _run_view("src.views.automation.newsletter")

def show_admin_console():
    _run_view("src.views.admin.console")


# --- 主程序逻辑 ---

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if st.session_state.logged_in:
    # 定义所有页面对象
    
    # 1. Word 工具
    page_translate = st.Page(show_cloud_trans, title="文档翻译 - 云端资源集", icon=":material/g_translate:", url_path="cloud-trans")
    page_translate_local = st.Page(show_local_trans, title="文档翻译 - 本地模型算力", icon=":material/letter_switch:", url_path="local-trans")
    page_heading_numbering = st.Page(show_numbering, title="word文档整理 - 上传文件", icon=":material/frame_inspect:", url_path="word-clean")

    # 2. 智能合同
    page_docx_diff = st.Page(show_docx_diff, title="Word 文档智能比对 (分词增强)", icon=":material/compare_arrows:", url_path="docx-diff")
    page_biding_review = st.Page(show_biding_review, title="标书智能审查", icon=":material/policy:", url_path="biding-review")
    page_contract_review = st.Page(show_contract_review, title="合同智能初审", icon=":material/description:", url_path="contract-review")

    # 3. 智能体集成
    page_dify_chatflow = st.Page(show_dify, title="Dify - 智能体集成", icon=":material/chat_bubble:", url_path="dify-chatflow")
    page_xinference = st.Page(show_xinference, title="XInference - 本地模型平台集成", icon=":material/rocket_launch:", url_path="xinference")
    page_free_chat_multimodal = st.Page(show_multimodal_chat, title="多模型问答 - 多模态", icon=":material/chat_bubble:", url_path="free-chat-multimodal")

    # 4. 多模态
    page_sora = st.Page(show_sora, title="Sora 视频生成", icon=":material/hangout_video:", url_path="sora")
    page_img_recognize = st.Page(show_img_recognize, title="图片识别", icon=":material/frame_inspect:", url_path="img-recognize")

    # 5. 自动化
    page_settings_newsletter = st.Page(show_newsletter, title="AI简报设置", icon=":material/article:", url_path="newsletter")
    page_prompt_config = st.Page(show_prompt_config, title="Prompt 配置", icon=":material/settings:", url_path="prompt-config")

    # 6. 系统设置
    logout_page = st.Page(logout, title="退出登录", icon=":material/logout:", url_path="logout")
    admin_page = st.Page(show_admin_console, title="账户管理", icon=":material/admin_panel_settings:", url_path="admin-console") if st.session_state.get("is_admin", False) else None

    # 构建导航字典
    nav = {
        "Word 工具": [page_translate, page_translate_local, page_heading_numbering],
        "智能合同": [page_docx_diff, page_biding_review, page_contract_review],
        "智能体集成": [page_dify_chatflow, page_xinference, page_free_chat_multimodal],
        "多模态": [page_sora, page_img_recognize],
        "自动化": [page_settings_newsletter, page_prompt_config],
        "系统设置": [admin_page, logout_page] if admin_page else [logout_page],
    }
    
    pg = st.navigation(nav)
else:
    login_page = st.Page(render_login_page, title="登录", icon=":material/login:", url_path="login")
    pg = st.navigation([login_page])

pg.run()