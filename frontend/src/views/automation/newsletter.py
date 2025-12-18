import streamlit as st

def render():
    st.title(":material/article: AI简报设置")
    title = st.text_input("简报标题", "AI Weekly Recap")
    header = st.text_area("头部内容 Markdown", height=160)
    twitter = st.text_area("Twitter 摘要 Markdown", height=160)
    reddit = st.text_area("Reddit 摘要 Markdown", height=160)
    generate = st.button("生成 HTML", type="primary")
    if generate:
        st.info("TODO: 调用 api_client")
        st.success("已生成 HTML 预览")
