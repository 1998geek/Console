import docx
from PIL import Image, UnidentifiedImageError
import io
import hashlib

# --- 导入用于访问和判断文档元素类型的库 ---
from docx.document import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph


# --- 核心逻辑: 从docx提取数据 (修正版，可以提取表格内图片) ---
def get_chapter_data(doc):
    """
    从docx文档中提取章节标题、章节内容、图片和表格。
    (已修正，可以正确提取表格单元格内的图片)
    """
    chapter_data = {}
    current_heading = "文档开头（无明确章节）"
    chapter_data[current_heading] = {'content': '', 'images': []}
    processed_image_hashes = set()

    for block in doc.element.body:
        # --- 分支一：处理段落 ---
        if isinstance(block, CT_P):
            para = Paragraph(block, doc)
            # 检查是否为标题
            if para.style.name.startswith('Heading'):
                cleaned_text = para.text.strip()
                if cleaned_text:
                    current_heading = cleaned_text
                    if current_heading not in chapter_data:
                        chapter_data[current_heading] = {'content': '', 'images': []}
            # 提取段落文本
            if para.text.strip():
                chapter_data[current_heading]['content'] += para.text + '\n'
            
            # 提取段落中的图片 (与原逻辑相同)
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
                                if image.format and image.format.upper() in ['JPG','JPEG', 'PNG']:
                                    chapter_data[current_heading]['images'].append(image)
                                else:
                                    filename = image_part.partname.split('/')[-1]
                                    img_format = image.format if image.format else 'UNKNOWN'
                                    placeholder = f"UNSUPPORTED_FORMAT_{img_format}:{filename}"
                                    chapter_data[current_heading]['images'].append(placeholder)
                                processed_image_hashes.add(image_hash)
                            except (KeyError, UnidentifiedImageError) as e:
                                filename = '未知图片'
                                if 'image_part' in locals():
                                    filename = image_part.partname.split('/')[-1]
                                error_placeholder = f"ERROR:无法加载图片 {filename} ({e})"
                                chapter_data[current_heading]['images'].append(error_placeholder)

        # --- 分支二：处理表格 ---
        elif isinstance(block, CT_Tbl):
            table = Table(block, doc)
            table_content = "\n--- 表格内容开始 ---\n"
            # 遍历表格的每一个单元格
            for row in table.rows:
                row_texts = []
                for cell in row.cells:
                    cell_text = ""
                    # 【【【核心修改点】】】
                    # 遍历单元格内的所有段落，而不仅仅是获取 .text
                    for para_in_cell in cell.paragraphs:
                        # 1. 累加单元格的文本内容
                        cell_text += para_in_cell.text.strip().replace('\n', ' ') + " "
                        
                        # 2. 对单元格内的段落应用相同的图片提取逻辑
                        if '<w:drawing>' in para_in_cell._p.xml:
                            for run in para_in_cell.runs:
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
                                            if image.format and image.format.upper() in ['JPEG', 'PNG']:
                                                chapter_data[current_heading]['images'].append(image)
                                            else:
                                                filename = image_part.partname.split('/')[-1]
                                                img_format = image.format if image.format else 'UNKNOWN'
                                                placeholder = f"UNSUPPORTED_FORMAT_{img_format}:{filename}"
                                                chapter_data[current_heading]['images'].append(placeholder)
                                            processed_image_hashes.add(image_hash)
                                        except (KeyError, UnidentifiedImageError) as e:
                                            filename = '未知图片'
                                            if 'image_part' in locals():
                                                filename = image_part.partname.split('/')[-1]
                                            error_placeholder = f"ERROR:无法加载图片 {filename} ({e})"
                                            chapter_data[current_heading]['images'].append(error_placeholder)
                    row_texts.append(cell_text.strip())
                table_content += "| " + " | ".join(row_texts) + " |\n"
            table_content += "--- 表格内容结束 ---\n\n"
            chapter_data[current_heading]['content'] += table_content
            
    final_data = {
        title: data for title, data in chapter_data.items() 
        if data['images'] or data['content'].strip()
    }
    final_data_with_images = {
        title: data for title, data in final_data.items() if data['images']
    }
    return final_data_with_images
