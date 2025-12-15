import streamlit as st
from docx import Document
from docx.shared import Pt
import io
import re

# --- 核心处理函数 ---

def process_docx_format(uploaded_file, font_size, remove_italic):
    """
    处理函数1：修改标题字号和斜体。
    """
    try:
        document = Document(uploaded_file)
        for paragraph in document.paragraphs:
            if paragraph.style and paragraph.style.name.startswith('Heading'):
                for run in paragraph.runs:
                    if font_size:
                        run.font.size = Pt(font_size)
                    if remove_italic:
                        run.font.italic = False
        
        file_stream = io.BytesIO()
        document.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        st.error(f"处理文档时发生错误: {e}")
        st.error("请确保您上传的是一个有效的 .docx 文件。")
        return None

def process_docx_renumber(uploaded_file):
    """
    处理函数2：根据现有标题样式，重新编排所有标题的序号。
    """
    try:
        document = Document(uploaded_file)
        counters = [0] * 9
        numbering_pattern = re.compile(r'^\s*[\d\.]+\s*')

        for p in document.paragraphs:
            if p.style and p.style.name.startswith('Heading'):
                try:
                    level = int(p.style.name.split()[-1])
                    level_index = level - 1
                    counters[level_index] += 1
                    for i in range(level, len(counters)):
                        counters[i] = 0
                    prefix_parts = [str(c) for c in counters[:level]]
                    new_prefix = '.'.join(prefix_parts)
                    clean_text = numbering_pattern.sub('', p.text).strip()
                    new_text = f"{new_prefix} {clean_text}"
                    p.clear()
                    p.add_run(new_text)
                except (ValueError, IndexError):
                    continue
        
        file_stream = io.BytesIO()
        document.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        st.error(f"处理文档时发生错误: {e}")
        st.error("请确保您上传的是一个有效的 .docx 文件。")
        return None

def process_docx_ultimate_fix(uploaded_file):
    """
    处理函数3 (终极版): 上下文感知修复器。
    能够处理由单个层级错误引发的连锁问题，并能识别和忽略错误的“从1开始”的子标题。
    """
    try:
        document = Document(uploaded_file)
        counters = [0] * 9
        
        # 上下文变量
        correction_active = False
        correction_offset = 0
        correction_resets_at_level = 0
        previous_true_level = 0 # 新增：记住上一个标题的正确层级

        # 正则表达式
        numbering_pattern_extract = re.compile(r'^\s*(\d+(\.\d+)*)')
        numbering_pattern_cleanup = re.compile(r'^\s*[\d\.]+\s*')

        for p in document.paragraphs:
            if not (p.style and p.style.name.startswith('Heading')):
                continue

            try:
                style_level = int(p.style.name.split()[-1])
            except (ValueError, IndexError):
                continue

            if correction_active and style_level <= correction_resets_at_level:
                correction_active = False
                correction_offset = 0
                correction_resets_at_level = 0

            text_level = None
            match = numbering_pattern_extract.match(p.text)
            if match:
                text_level = match.group(1).count('.') + 1

            # --- 新增逻辑：识别并忽略“流氓”的“1.”开头的子标题 ---
            # 如果文本层级是1，但它不是文档的第一个标题，那么这个层级是不可信的
            if text_level == 1 and previous_true_level > 0:
                text_level = None # 将其视为没有序号的标题，强制回退到使用样式判断

            # --- 核心逻辑：判断并应用修正 ---
            true_level = None
            if text_level is not None and text_level != style_level:
                true_level = text_level
                correction_active = True
                correction_offset = true_level - style_level
                correction_resets_at_level = style_level
            else:
                true_level = style_level + correction_offset
            
            true_level = max(1, min(9, true_level))
            
            # --- 标准的重排序号和应用样式逻辑 ---
            level_index = true_level - 1
            counters[level_index] += 1
            for i in range(true_level, len(counters)):
                counters[i] = 0
                
            new_prefix = '.'.join(str(c) for c in counters[:true_level])
            clean_text = numbering_pattern_cleanup.sub('', p.text).strip()
            new_text = f"{new_prefix} {clean_text}"
            
            p.clear()
            p.add_run(new_text)
            p.style = f'Heading {true_level}'
            
            # 更新上一个标题的真实层级，为下一次循环做准备
            previous_true_level = true_level

        file_stream = io.BytesIO()
        document.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        st.error(f"处理文档时发生错误: {e}")
        st.error("请确保您上传的是一个有效的 .docx 文件。")
        return None

# --- Streamlit 页面定义 ---

def page_format_titles():
    """页面1: 标题格式修改器"""
    st.header("✍️ 标题格式修改器")
    st.markdown("此工具可以批量修改 Word (.docx) 文档中所有标题的**字号**和**斜体**样式。")
    uploaded_file = st.file_uploader("上传 .docx 文档", type=['docx'], key="format_uploader")
    if uploaded_file:
        st.success(f"文件上传成功: **{uploaded_file.name}**")
        st.divider()
        font_size_to_set = st.number_input("设置标题字号:", min_value=1, max_value=100, value=16, step=1)
        remove_italic = st.checkbox("取消所有标题的斜体样式", value=True)
        if st.button("🚀 开始处理格式", type="primary", key="format_button"):
            with st.spinner("正在处理..."):
                processed_stream = process_docx_format(uploaded_file, font_size_to_set, remove_italic)
                if processed_stream:
                    st.success("🎉 格式处理完成！")
                    st.download_button(label="📥 点击下载", data=processed_stream, file_name=f"格式修改后_{uploaded_file.name}", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

def page_renumber_headings():
    """页面2: 标题序号重排器 (基础版)"""
    st.header("🔢 标题序号重排器 (基础版)")
    st.markdown("此工具**根据标题现有的样式** (标题1, 标题2...) 重新生成 `1.`, `1.1`, `1.1.1` 格式的序号。**它假定您文档的标题样式层级是基本正确的。**")
    uploaded_file = st.file_uploader("上传 .docx 文档", type=['docx'], key="renumber_uploader")
    if uploaded_file:
        st.success(f"文件上传成功: **{uploaded_file.name}**")
        st.divider()
        if st.button("🚀 开始重排序号", type="primary", key="renumber_button"):
            with st.spinner("正在分析并重排标题序号..."):
                processed_stream = process_docx_renumber(uploaded_file)
                if processed_stream:
                    st.success("🎉 序号重排完成！")
                    st.download_button(label="📥 点击下载", data=processed_stream, file_name=f"序号重排后_{uploaded_file.name}", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

def page_ultimate_fixer():
    """页面3: 标题层级与序号终极修复器"""
    st.header("🏆 标题层级与序号终极修复器")
    st.markdown("""
    这是解决复杂文档混乱的**最强工具**。它能处理由单个标题层级错误引发的**连锁问题**。
    - **智能诊断**: 发现 `2.5.1` 这样的文本被错误地设为“标题1”时，会将其修正为“标题3”。
    - **连锁修正**: 在下一个更高层级标题出现前，所有后续的子标题都会被自动应用这个偏差（例如，原来的“标题2”会被智能地修正为“标题4”）。
    - **忽略伪造序号**: **(新功能)** 如果一个子标题错误地以 `1.` 开头，程序会智能地忽略它，并将其正确地归入父标题下（例如，`2.5` 下面的 `1.` 会被修正为 `2.5.1`）。
    """)
    uploaded_file = st.file_uploader("上传 .docx 文档", type=['docx'], key="ultimate_fix_uploader")
    if uploaded_file:
        st.success(f"文件上传成功: **{uploaded_file.name}**")
        st.divider()
        if st.button("🚀 开始终极修复", type="primary", key="ultimate_fix_button"):
            with st.spinner("正在进行上下文感知扫描，修正连锁错误..."):
                processed_stream = process_docx_ultimate_fix(uploaded_file)
                if processed_stream:
                    st.success("🎉 文档层级与序号已完美修复！")
                    st.download_button(label="📥 点击下载修复后的文档", data=processed_stream, file_name=f"终极修复后_{uploaded_file.name}", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# --- 主应用布局 ---

st.set_page_config(page_title="Word 文档处理器", page_icon="📄", layout="wide")

st.sidebar.title("📄 多功能 Word 处理器")
st.sidebar.markdown("请在下方选择您需要的功能：")

page_options = {
    "标题格式修改": page_format_titles,
    "标题序号重排 (基础)": page_renumber_headings,
    "层级与序号终极修复": page_ultimate_fixer,
}
selected_page = st.sidebar.radio("功能选择", options=list(page_options.keys()))

st.sidebar.divider()
st.sidebar.info("由 Gemini 强力驱动 | 专为高效办公设计")

page_options[selected_page]()
