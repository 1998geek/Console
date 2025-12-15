# ==============================================================================
# 标书智能检查系统 - 完整代码 (v5 - 表格提取功能)
#
# 新增功能:
# 1. 能够提取章节内的表格内容，并格式化为文本。
# 2. 改进了核心遍历逻辑，确保段落、表格、图片按文档原始顺序被正确处理。
# ==============================================================================

import streamlit as st
import docx
from PIL import Image, UnidentifiedImageError
import io
import hashlib

# --- 新增必要的导入，用于访问和判断文档元素类型 ---
from docx.document import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph


# --- 核心逻辑: 最终版函数，集合所有优化点 (新增表格提取) ---
def get_chapter_data(doc):
    """
    从docx文档中提取章节标题、章节内容、图片和表格。
    本函数包含以下关键优化：
    1. 统一遍历文档内容块，确保段落和表格按序提取。
    2. 提取表格内容并格式化为文本。
    3. 通过哈希值对图片内容进行全局去重。
    4. 识别WMF等特殊图片格式。
    
    :param doc: python-docx的Document对象
    :return: 一个字典，键是章节标题，值是包含 'content' 和 'images' 的另一个字典。
    """
    chapter_data = {}
    current_heading = "文档开头（无明确章节）"
    chapter_data[current_heading] = {'content': '', 'images': []}
    processed_image_hashes = set()

    # --- 核心改动: 遍历文档的所有顶级块元素(段落和表格) ---
    for block in doc.element.body:
        # 判断块是段落还是表格
        if isinstance(block, CT_P):
            para = Paragraph(block, doc) # 将XML元素包装成Paragraph对象
            
            # --- 以下是原有的段落处理逻辑 ---
            # 1. 判断是否为新的章节标题
            if para.style.name.startswith('Heading'):
                cleaned_text = para.text.strip()
                if cleaned_text:
                    current_heading = cleaned_text
                    if current_heading not in chapter_data:
                        chapter_data[current_heading] = {'content': '', 'images': []}
            
            # 2. 累加当前章节的文本内容
            if para.text.strip():
                chapter_data[current_heading]['content'] += para.text + '\n'

            # 3. 在段落中寻找并处理图片
            if '<w:drawing>' in para._p.xml:
                for run in para.runs:
                    if '<w:drawing>' in run._r.xml:
                        for rId in run.element.xpath(".//@r:embed"):
                            try:
                                image_part = doc.part.related_parts[rId]
                                image_blob = image_part.blob
                                image_hash = hashlib.md5(image_blob).hexdigest()
                                
                                if image_hash in processed_image_hashes:
                                    continue

                                image_stream = io.BytesIO(image_blob)
                                image = Image.open(image_stream)
                                
                                if image.format == 'WMF':
                                    filename = image_part.partname.split('/')[-1]
                                    placeholder = f"UNSUPPORTED_WMF:{filename}"
                                    chapter_data[current_heading]['images'].append(placeholder)
                                else:
                                    chapter_data[current_heading]['images'].append(image)

                                processed_image_hashes.add(image_hash)

                            except (KeyError, UnidentifiedImageError) as e:
                                filename = '未知图片'
                                if 'image_part' in locals():
                                    filename = image_part.partname.split('/')[-1]
                                error_placeholder = f"ERROR:无法加载图片 {filename} ({e})"
                                chapter_data[current_heading]['images'].append(error_placeholder)

        elif isinstance(block, CT_Tbl):
            table = Table(block, doc) # 将XML元素包装成Table对象
            
            # --- 新增的表格处理逻辑 ---
            table_content = "\n--- 表格内容开始 ---\n"
            for row in table.rows:
                # 清理每个单元格的文本，并用'|'连接
                cleaned_cells = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
                table_content += "| " + " | ".join(cleaned_cells) + " |\n"
            table_content += "--- 表格内容结束 ---\n\n"
            
            # 将格式化后的表格内容追加到当前章节
            chapter_data[current_heading]['content'] += table_content
                                    
    # ... 函数末尾的清理逻辑保持不变 ...
    final_data = {
        title: data for title, data in chapter_data.items() 
        if data['images'] or data['content'].strip()
    }
    final_data_with_images = {
        title: data for title, data in final_data.items() if data['images']
    }
    return final_data_with_images

# --- Streamlit 用户界面 (集成最终优化) ---
st.set_page_config(page_title="标书图片审核系统", layout="wide")

st.title("📄 标书智能检查系统 - 图片与内容审核")
st.write("请上传您的 `.docx` 格式标书文件，系统将自动提取包含图片的章节及其对应的文本内容。")
st.info("💡 系统已优化，能够智能识别并提示WMF格式的图片，并自动处理重复的图片引用。")

uploaded_file = st.file_uploader("选择一个Word文档...", type=["docx"])

if uploaded_file is not None:
    # 使用session_state来避免重复处理同一个文件
    if 'processed_file' not in st.session_state or st.session_state.processed_file != uploaded_file.name:
        try:
            document = docx.Document(uploaded_file)
            st.success(f"文件 “{uploaded_file.name}” 上传成功！")

            with st.spinner("正在提取图片和章节内容，请稍候..."):
                st.session_state.chapter_data = get_chapter_data(document)
            
            st.session_state.processed_file = uploaded_file.name

        except Exception as e:
            st.error(f"处理文件时发生严重错误：{e}")
            st.error("请确保上传的是一个有效的、未加密或损坏的.docx文件。")
            # 清理session_state以允许重试
            if 'processed_file' in st.session_state: del st.session_state.processed_file
            if 'chapter_data' in st.session_state: del st.session_state.chapter_data

    # 如果session_state中已有处理好的数据，则直接显示
    if 'chapter_data' in st.session_state:
        chapter_data = st.session_state.chapter_data
        
        if not chapter_data:
            st.warning("在此文档中未检测到任何包含图片的章节。")
        else:
            # --- 优化1：计算总数和问题图片总数 ---
            total_images_count = sum(len(data['images']) for data in chapter_data.values())
            total_problem_images = sum(1 for data in chapter_data.values() for img in data['images'] if isinstance(img, str))

            # 构建并显示带有条件格式的成功消息
            success_message = f"任务完成！共在 **{len(chapter_data)}** 个章节中找到了 **{total_images_count}** 张图片及其相关内容。"
            if total_problem_images > 0:
                success_message += f" :red[**其中包含 {total_problem_images} 张问题图片。**]"
            st.success(success_message)
            st.markdown("---")
            
            # --- 优化2：为渲染过程添加状态提示 ---
            status_text = st.empty()
            progress_bar = st.progress(0, text="正在渲染章节...")
            total_chapters = len(chapter_data)

            # 遍历所有找到的章节并显示
            for i, (chapter_title, data) in enumerate(chapter_data.items()):
                images = data['images']
                content = data['content']
                
                # 计算每个章节的问题图片数量
                problem_images_count = sum(1 for img in images if isinstance(img, str))

                # 构建带有问题图片提示的动态标题
                expander_title = f"章节: {chapter_title} (共 {len(images)} 张图片)"
                if problem_images_count > 0:
                    expander_title += f" - :red[**发现 {problem_images_count} 张问题图片！**]"

                # 更新状态文本
                status_text.text(f"正在渲染章节 {i+1}/{total_chapters}: {chapter_title}")

                # 注意：这里使用了您代码中的 expanded=False，默认折叠
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.subheader("章节文本内容")
                        st.text_area(
                            "Content", value=content, height=300, 
                            disabled=True, label_visibility="collapsed"
                        )
                    
                    with col2:
                        st.subheader("章节内图片")
                        for i_img, img_data in enumerate(images):
                            if isinstance(img_data, str) and img_data.startswith("UNSUPPORTED_WMF"):
                                filename = img_data.split(':')[-1]
                                st.warning(f"图片 {i_img+1} ({filename}) 是WMF格式，无法在此预览。")
                                st.info("建议：请在Word中右键单击此图，选择“另存为图片”，保存为PNG或JPG格式后重新插入。")
                            elif isinstance(img_data, str) and img_data.startswith("ERROR"):
                                st.error(f"图片 {i_img+1} 加载失败。错误信息: {img_data}")
                            else:
                                st.image(img_data, caption=f"图片 {i_img+1}", use_container_width=True)
                    
                    st.markdown("---")
                    
                    button_key = f"btn_{chapter_title.replace(' ', '_')}"
                    if st.button(f"结合上下文审核 “{chapter_title}” 章节", key=button_key):
                        valid_images = [img for img in images if not isinstance(img, str)]
                        st.info(f"下一步将调用多模态模型对“{chapter_title}”章节的文本和 {len(valid_images)} 张有效图片进行智能审核。")
                
                # 更新进度条
                progress_bar.progress((i + 1) / total_chapters, text=f"已渲染 {i+1}/{total_chapters} 个章节")

            # 渲染完成后，清空状态组件
            status_text.empty()
            progress_bar.empty()

else:
    # 如果没有文件上传，确保清理session_state
    if 'processed_file' in st.session_state: del st.session_state.processed_file
    if 'chapter_data' in st.session_state: del st.session_state.chapter_data
    st.info("请上传一个文件以开始分析。")