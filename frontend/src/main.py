import os
import base64
import importlib
import streamlit as st

st.set_page_config(page_title="ComLan", page_icon=":material/home:", layout="wide", initial_sidebar_state="auto", menu_items=None)


def _load_bg_base64() -> str | None:
    try:
        candidates = [
            "/Users/wangyang/Documents/GitHub/Company/AI_Console/frontend/images/background.jpg",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "images", "background.jpg")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "images", "background.jpg")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "background.jpg")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Console", "images", "background.jpg")),
        ]
        for bg_path in candidates:
            if os.path.exists(bg_path):
                with open(bg_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except Exception:
        pass
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


from src.services import auth_service

def render_login_page():
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
                    # TODO: Fetch user role/permissions from backend if needed
                    st.session_state.is_admin = False 
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
    st.write("Are you sure you want to log out?")
    st.write("You will be redirected to the login page.")
    if st.button("Log out", type="primary"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()


def _run_view(module_path: str, placeholder_text: str = "TODO: 调用 api_client"):
    try:
        mod = importlib.import_module(module_path)
        fn = getattr(mod, "render", None)
        if callable(fn):
            return fn()
    except Exception as e:
        st.error(f"加载页面失败: {e}")
    st.info(placeholder_text)


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


def show_free_chat():
    st.info("TODO: 调用 api_client")


def show_chat_bi():
    st.info("TODO: 调用 api_client")


def show_case_study():
    st.info("TODO: 调用 api_client")


def show_background_study():
    st.info("TODO: 调用 api_client")


def show_customer_support():
    st.info("TODO: 调用 api_client")


def show_heading_numbering_base():
    st.info("TODO: 调用 api_client")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if st.session_state.logged_in:
    logout_page = st.Page(logout, title="Log out", icon=":material/logout:", url_path="logout")

    admin_page = st.Page(show_admin_console, title="管理员控制台", icon=":material/admin_panel_settings:", url_path="admin-console") if st.session_state.get("is_admin", False) else None

    page_translate = st.Page(show_cloud_trans, title="文档翻译 - 云端资源集成", icon=":material/g_translate:", url_path="cloud-trans")
    page_translate_local = st.Page(show_local_trans, title="文档翻译 - 本地模型算力", icon=":material/letter_switch:", url_path="local-trans")
    page_heading_numbering = st.Page(show_numbering, title="word文档整理 - 上传文件", icon=":material/frame_inspect:", url_path="word-clean")
    page_heading_numbering_base = st.Page(show_heading_numbering_base, title="word文档整理 - 基础 - 上传文件", icon=":material/frame_inspect:", url_path="word-clean-base")

    page_contract_review = st.Page(show_contract_review, title="合同智能初审", icon=":material/description:", url_path="contract-review")
    page_biding_review = st.Page(show_biding_review, title="标书智能审查", icon=":material/policy:", url_path="biding-review")
    page_docx_diff = st.Page(show_docx_diff, title="Word 文档比对", icon=":material/compare_arrows:", url_path="docx-diff")

    page_dify_chatflow = st.Page(show_dify, title="Dify - 智能体集成", icon=":material/chat_bubble:", url_path="dify-chatflow")
    page_xinference = st.Page(show_xinference, title="XInference - 本地模型平台集成", icon=":material/rocket_launch:", url_path="xinference")
    page_free_chat_multimodal = st.Page(show_multimodal_chat, title="多模型问答 - 多模态", icon=":material/chat_bubble:", url_path="free-chat-multimodal")

    page_sora = st.Page(show_sora, title="Sora 视频生成", icon=":material/hangout_video:", url_path="sora")
    page_img_recognize = st.Page(show_img_recognize, title="员工违规操作识别", icon=":material/frame_inspect:", url_path="img-recognize")

    page_prompt_config = st.Page(show_prompt_config, title="Prompt 配置", icon=":material/settings:", url_path="prompt-config")
    page_settings_newsletter = st.Page(show_newsletter, title="AI简报设置", icon=":material/article:", url_path="newsletter")

    page_free_chat = st.Page(show_free_chat, title="多模型问答", icon=":material/chat:", url_path="free-chat")
    page_chat_bi = st.Page(show_chat_bi, title="智能问数", icon=":material/monitoring:", url_path="chat-bi")
    page_case_study = st.Page(show_case_study, title="案例查询", icon=":material/history_edu:", url_path="case-study")
    page_background_study = st.Page(show_background_study, title="客户背景调研", icon=":material/book_ribbon:", url_path="background-study")
    page_customer_support = st.Page(show_customer_support, title="售后问题助手", icon=":material/support_agent:", url_path="customer-support")

    nav = {
        "Doc Translation": [page_translate, page_translate_local],
        "Tools": [page_docx_diff, page_biding_review, page_contract_review, page_img_recognize, page_heading_numbering, page_heading_numbering_base],
        "Intelligent Query": [page_dify_chatflow, page_xinference, page_free_chat, page_free_chat_multimodal, page_sora, page_chat_bi, page_customer_support],
        "Case Study": [page_case_study, page_background_study],
        "Settings": [page_prompt_config, page_settings_newsletter],
        "Account": [admin_page, logout_page] if admin_page else [logout_page],
    }
    pg = st.navigation(nav)
else:
    login_page = st.Page(render_login_page, title="Log in", icon=":material/login:", url_path="login")
    pg = st.navigation([login_page])

pg.run()
