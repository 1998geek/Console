
import streamlit as st

def init_sidebar(login, logout):
    # https://fonts.google.com/icons?icon=
    if st.session_state.logged_in:
        
        logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

        # 只为管理员用户添加管理员页面
        if st.session_state.get('is_admin', False):
            def admin_page():
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("page_admin", "sub_pages/page_admin.py")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    module.render()
                except Exception as e:
                    st.error(f"加载管理员页面时出错: {str(e)}")

            page_admin = st.Page(admin_page, title="管理员控制台", icon=":material/admin_panel_settings:")

        # page_create_index = st.Page("sub_pages/page_create_index.py", title="Create Index", icon="✏️")
        # page_delete_index = st.Page("sub_pages/page_delete_index.py", title="Delete Index", icon="🎈")
        # page_upload_data = st.Page("sub_pages/page_upload_data.py", title="Upload Data", icon="📚")
        # page_vector_search = st.Page("sub_pages/page_vector_search.py", title="Vector Search", icon="🎉")
        # page_chat = st.Page("sub_pages/page_chat.py", title="Chat Search", icon="💬")
        # page_free_chat = st.Page("sub_pages/page_free_chat.py", title="Free Chat", icon="🍁")
        # page_deepseek = st.Page("sub_pages/page_deepseek-r1.py", title="Deepseek-R1", icon="🐋")
        # page_whisper = st.Page("sub_pages/page_whisper.py", title="Transcription", icon="🔍")
        
        page_translate = st.Page("sub_pages/page_translate.py", title="文档翻译 - 云端资源集成", icon=":material/g_translate:")
        page_translate_local = st.Page("sub_pages/page_translate_local.py", title="文档翻译 - 本地模型算力", icon=":material/letter_switch:")
        page_heading_numbering = st.Page("sub_pages/page_heading_numbering.py", title="word文档整理 - 上传文件", icon=":material/frame_inspect:")
        page_heading_numbering_base = st.Page("sub_pages/page_heading_numbering_base.py", title="word文档整理 - 基础 - 上传文件", icon=":material/frame_inspect:")

        page_contract_review = st.Page("sub_pages/page_contract_review.py", title="合同智能初审", icon=":material/description:")
        page_biding_review = st.Page("sub_pages/page_biding_doc_review.py", title="标书智能审查", icon=":material/policy:")
        page_docx_diff = st.Page("sub_pages/page_docx_diff.py", title="Word 文档比对", icon=":material/compare_arrows:")
        page_dify_chatflow = st.Page("sub_pages/page_dify_chatflow.py", title="Dify - 智能体集成", icon=":material/chat_bubble:")
        page_xinference = st.Page("sub_pages/page_xinference.py", title="XInference - 本地模型平台集成", icon=":material/rocket_launch:")
        page_sora = st.Page("sub_pages/page_az_sora.py", title="Sora 视频生成", icon=":material/hangout_video:")
        page_img_recognize = st.Page("sub_pages/page_img_recognize.py", title="员工违规操作识别", icon=":material/frame_inspect:")

        page_free_chat = st.Page("sub_pages/page_free_chat.py", title="多模型问答", icon=":material/chat:")
        page_free_chat_multimodal  = st.Page("sub_pages/page_free_chat_multimodal .py", title="多模型问答 - 多模态", icon=":material/chat_bubble:")

        page_chat_bi = st.Page("sub_pages/page_chat_bi.py", title="智能问数", icon=":material/monitoring:")
        page_case_study = st.Page("sub_pages/page_case_study.py", title="案例查询", icon=":material/history_edu:")
        page_background_study = st.Page("sub_pages/page_background_study.py", title="客户背景调研", icon=":material/book_ribbon:")
        page_customer_support = st.Page("sub_pages/page_customer_support.py", title="售后问题助手", icon=":material/support_agent:")

        page_prompt_config = st.Page("sub_pages/settings_pages/page_prompt_config.py", title="Prompt 配置", icon=":material/settings:")
        page_settings_newsletter = st.Page("sub_pages/settings_pages/page_settings_newsletter.py", title="AI简报设置", icon=":material/article:")

        pg = st.navigation(
            {
                # "Tools": [page_create_index, page_delete_index, page_upload_data, page_vector_search],
                # "Search": [page_chat, page_free_chat, page_deepseek],
                # "Transcription": [page_whisper],
                "Doc Translation": [page_translate, page_translate_local],
                "Tools": [page_docx_diff, page_biding_review, page_contract_review, page_img_recognize, page_heading_numbering, page_heading_numbering_base],
                "Intelligent Query": [page_dify_chatflow, page_xinference, page_free_chat,page_free_chat_multimodal, page_sora, page_chat_bi, page_customer_support],
                "Case Study": [page_case_study, page_background_study],
                "Settings": [page_prompt_config, page_settings_newsletter],
                "Account": [page_admin, logout_page] if st.session_state.get('is_admin', False) else [logout_page],
            }
        )
    else:
        login_page = st.Page(login, title="Log in", icon=":material/login:")
        pg = st.navigation([login_page])

    pg.run()