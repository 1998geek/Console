import streamlit as st
from app_config.settings import get_setting, update_setting
from function.NewsCollector import RSSProcessor, NewsCollector
from function.EmailSender import EmailSender

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

    with st.expander("Configure Settings", expanded=False):
        with st.form("settings_form"):
            new_settings = {}
            for key, label in settings_keys.items():
                is_password = "PASSWORD" in key
                current_value = get_setting(key) or ""
                # if is_password:
                #     current_value = "" # Don't display password
                
                new_settings[key] = st.text_input(label, value=current_value, type="password" if is_password else "default")

            if st.form_submit_button("Save Settings"):
                with st.spinner("Saving..."):
                    for key, value in new_settings.items():
                        if "PASSWORD" in key and not value:
                            continue
                        update_setting(key, value)
                    st.success("Settings saved!")

    st.header("Newsletter Actions")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Newsletter Preview"):
            with st.spinner("Generating..."):
                try:
                    subject, newsletter_html = NewsCollector().collect_news_job(send_email=False)
                    st.session_state.newsletter_subject = subject
                    st.session_state.newsletter_html = newsletter_html
                    st.success("Preview generated.")
                except Exception as e:
                    st.error(f"Error generating preview: {e}")
    
    with col2:
        if 'newsletter_html' in st.session_state:
            if st.button("Send Newsletter"):
                with st.spinner("Sending..."):
                    try:
                        success = NewsCollector().send_email(
                            title=st.session_state.newsletter_subject,
                            html_content=st.session_state.newsletter_html
                        )
                        if success:
                            st.success("Newsletter sent!")
                            del st.session_state.newsletter_subject
                            del st.session_state.newsletter_html
                        else:
                            st.error("Failed to send newsletter.")
                    except Exception as e:
                        st.error(f"Error sending email: {e}")

    if 'newsletter_html' in st.session_state:
        st.subheader("Preview")
        st.markdown(st.session_state.newsletter_html, unsafe_allow_html=True)

show()