import streamlit as st

# 保留子标题
st.subheader(':material/book_ribbon: 客户调用助手请输入您要调用的客户名称。')

# 嵌入 Dify 前端页面，优化 iframe 样式
dify_url = "http://172.200.234.13/chat/vzicKhGMKHV5cPLG"

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
