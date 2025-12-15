import streamlit as st

st.subheader(':material/support_agent: 客户支持助手，请输入您的问题。')

# 嵌入 Dify 前端页面
dify_url = "http://192.168.88.101/chat/kfAW2hnbVLIaLZxo"

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