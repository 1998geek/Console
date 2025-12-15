# --- 安装说明 ---
# 1. 打开终端或命令行
# 2. 运行以下命令来安装所有必要的库:
#    pip install streamlit mammoth lxml jieba

import streamlit as st
import mammoth
from lxml import html
from lxml.html.diff import htmldiff
import jieba
import io

# --- 核心功能函数 ---

def segment_chinese_in_tree(tree_root):
    """
    递归遍历 lxml 树，使用 jieba 对所有中文文本节点进行分词。
    这是实现字词级比对的关键。
    """
    # 遍历树中的所有元素节点
    for element in tree_root.iter('*'):
        # 处理元素自身的文本 (el.text)
        if element.text and element.text.strip():
            # 使用 jieba.cut 分词，并用空格连接
            element.text = ' '.join(jieba.cut(element.text, cut_all=False))
        # 处理元素尾部的文本 (el.tail)，即紧跟在元素后面的文本
        if element.tail and element.tail.strip():
            element.tail = ' '.join(jieba.cut(element.tail, cut_all=False))
    return tree_root

# --- Streamlit 应用界面 ---

# 1. 设置页面标题和介绍
# st.set_page_config(page_title="Word 文档智能比对", layout="wide")
st.title(":material/compare_arrows: Word 文档智能比对 (分词增强)")
st.markdown("""
上传两个 `.docx` 文件，本工具将通过**中文分词技术**，实现**字词级别**的精准比对，
并以“修订模式”高亮显示两个文档之间的差异。注意：请使用Microsoft Office 官方文件，其他软件导出的兼容格式可能会导致翻译错误。

- <span style="background-color: #e6ffe6;">绿色背景</span> 代表新增的内容。
- <span style="background-color: #ffe6e6; text-decoration: line-through;">红色删除线</span> 代表删除的内容。
""", unsafe_allow_html=True)


# 2. 创建并排的列来放置文件上传器
col1, col2 = st.columns(2)

with col1:
    st.header("文档 A (原始版本)")
    uploaded_file1 = st.file_uploader("上传第一个 .docx 文件", type=['docx'], key="file1")

with col2:
    st.header("文档 B (修订版本)")
    uploaded_file2 = st.file_uploader("上传第二个 .docx 文件", type=['docx'], key="file2")

# 3. 创建比对按钮
if st.button("🚀 开始比对"):
    # 检查两个文件是否都已上传
    if uploaded_file1 is not None and uploaded_file2 is not None:
        with st.spinner('正在转换、分词和比对文档，请稍候...'):
            try:
                # --- 步骤 1: 将 .docx 文件转换为 HTML ---
                html1_raw = mammoth.convert_to_html(uploaded_file1).value
                html2_raw = mammoth.convert_to_html(uploaded_file2).value

                # --- 步骤 2: 解析 HTML 并进行中文分词 ---
                # 解析为 lxml 树结构
                tree1 = html.fromstring(html1_raw)
                tree2 = html.fromstring(html2_raw)

                # 对两棵树进行分词处理
                segmented_tree1 = segment_chinese_in_tree(tree1)
                segmented_tree2 = segment_chinese_in_tree(tree2)

                # --- 步骤 3: 使用 lxml.html.diff 比对分词后的内容 ---
                diff_html = htmldiff(segmented_tree1, segmented_tree2)

                # --- 步骤 4: 添加自定义 CSS 样式并渲染最终的 HTML ---
                styled_diff_html = f"""
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                        line-height: 1.6;
                    }}
                    ins {{
                        background-color: #e6ffe6 !important;
                        text-decoration: none !important;
                    }}
                    del {{
                        background-color: #ffe6e6 !important;
                        text-decoration: line-through !important;
                        color: #555 !important;
                    }}
                </style>
                {diff_html}
                """

                st.header("比对结果 (修订模式视图)")
                st.components.v1.html(styled_diff_html, height=800, scrolling=True)

            except Exception as e:
                st.error(f"处理过程中发生错误: {e}")
                st.exception(e) # 打印更详细的错误堆栈信息
                st.error("请确保上传的是有效的 .docx 文件。")

    else:
        st.error("❌ 请确保两个文件都已成功上传！")
