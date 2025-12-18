import streamlit as st 
from src.services.api_client import api_client 
 
def show(): 
    st.title("Newsletter Settings") 
 
    settings_keys = { 
        "RSS_URL": "RSS Feed URL", 
        "SENDER_USERNAME": "Sender Email Username", 
        "SENDER_PASSWORD": "Sender Email Password", 
        "SMTP_HOST": "SMTP Host", 
        "SMTP_PORT": "SMTP Port", 
        "TO_ADDRS": "Recipient Emails (comma-separated)", 
        "FROM_ALIAS": "Sender Display Name" 
    } 
 
    # 1. 设置表单 
    with st.expander("Configure Settings", expanded=False): 
        with st.form("settings_form"): 
            new_settings = {} 
            # 这里我们简化逻辑，不预加载所有值以保护隐私，或者后续从后端 load 
            for key, label in settings_keys.items(): 
                is_password = "PASSWORD" in key 
                # 实际项目应调用 api_client.get("/automation/config/{key}") 获取当前值 
                current_value = "" 
                new_settings[key] = st.text_input(label, value=current_value, type="password" if is_password else "default") 
 
            if st.form_submit_button("Save Settings"): 
                with st.spinner("Saving..."): 
                    # 批量保存逻辑 
                    for key, value in new_settings.items(): 
                        if "PASSWORD" in key and not value: 
                            continue # 不覆盖空密码 
                        if value: 
                            api_client.post("/automation/config", json={"key": key, "value": value}) 
                    st.success("Settings saved!") 
 
    st.header("Newsletter Actions") 
 
    # 2. 动作按钮 
    col1, col2 = st.columns(2) 
    with col1: 
        if st.button("Generate Newsletter Preview"): 
            with st.spinner("Generating..."): 
                # 调用后端生成预览 
                res = api_client.post("/automation/newsletter/preview") 
                if res and res.get("html"): 
                    st.session_state.newsletter_subject = res.get("subject", "No Subject") 
                    st.session_state.newsletter_html = res.get("html") 
                    st.success("Preview generated.") 
                else: 
                    st.error("Error generating preview.") 
     
    with col2: 
        if 'newsletter_html' in st.session_state: 
            if st.button("Send Newsletter"): 
                with st.spinner("Sending..."): 
                    # 调用后端发送 
                    res = api_client.post("/automation/newsletter/send", json={ 
                        "subject": st.session_state.newsletter_subject, 
                        "html": st.session_state.newsletter_html 
                    }) 
                    if res and res.get("success"): 
                        st.success("Newsletter sent!") 
                        del st.session_state.newsletter_subject 
                        del st.session_state.newsletter_html 
                    else: 
                        st.error("Failed to send newsletter.") 
 
    # 3. 预览区域 
    if 'newsletter_html' in st.session_state: 
        st.subheader("Preview") 
        st.markdown(st.session_state.newsletter_html, unsafe_allow_html=True) 
 
render = show
