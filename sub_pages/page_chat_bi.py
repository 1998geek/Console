import streamlit as st

st.subheader(':material/monitoring: 智能问数助手，请输入您的问题。')


# 嵌入 Dify 前端页面
dify_url = "http://172.200.234.13/chat/uXArlDP7jccKB5KX"

# 添加自定义样式
st.markdown("""
    <style>
        iframe {
            width: calc(100% - var(--sidebar-width, 0px)); /* 动态宽度 */
            height: 570px; /* 全屏高度 */
            border: none;
        }   
""", unsafe_allow_html=True)
# 渲染 iframe
st.markdown(f"""
    <div class="iframe-container">
        <iframe
            src="{dify_url}"
            scrolling="no"
            frameborder="0"
        ></iframe>
    </div>
""", unsafe_allow_html=True)