import streamlit as st
from docx import Document
import io
import re

def correct_heading_hierarchy(doc_obj):
    """
    Corrects heading hierarchy by analyzing each chapter (sections between H1s),
    finding missing levels, and compacting the hierarchy.
    """
    
    # 1. Find chapter boundaries (start index of each H1)
    h1_indices = [i for i, p in enumerate(doc_obj.paragraphs) if p.style and p.style.name == 'Heading 1']
    
    chapter_boundaries = []
    # Add start of doc if it doesn't start with H1 or has no H1s
    if not h1_indices or h1_indices[0] > 0:
        chapter_boundaries.append(0)
    
    chapter_boundaries.extend(h1_indices)
    # Add end of doc
    chapter_boundaries.append(len(doc_obj.paragraphs))

    # 2. Process each chapter defined by the boundaries
    for i in range(len(chapter_boundaries) - 1):
        start_index = chapter_boundaries[i]
        end_index = chapter_boundaries[i+1]
        chapter_paragraphs = doc_obj.paragraphs[start_index:end_index]

        # Pass 1: Analyze the chapter to build a remap rule
        present_levels = set()
        for p in chapter_paragraphs:
            if p.style and p.style.name.startswith('Heading'):
                try:
                    level = int(p.style.name.split(' ')[-1])
                    present_levels.add(level)
                except (ValueError, IndexError):
                    continue
        
        if not present_levels:
            continue

        sorted_present_levels = sorted(list(present_levels))
        
        # Create the compaction map. E.g., [1, 3, 5] -> {1:1, 3:2, 5:3}
        level_remap = {old_level: new_level for new_level, old_level in enumerate(sorted_present_levels, start=1)}

        # Pass 2: Apply the remapping to the chapter's headings
        for p in chapter_paragraphs:
            if p.style and p.style.name.startswith('Heading'):
                try:
                    declared_level = int(p.style.name.split(' ')[-1])
                    if declared_level in level_remap:
                        effective_level = level_remap[declared_level]
                        
                        if effective_level != declared_level:
                            try:
                                p.style = f'Heading {effective_level}'
                            except KeyError:
                                st.warning(f"文档缺少“Heading {effective_level}”样式，无法修正跳级。将按原样式处理。")
                except (ValueError, IndexError):
                    continue

def apply_heading_numbering(doc_obj):
    """
    Applies hierarchical numbering to headings in a docx document.
    Assumes the heading hierarchy is already correct.
    """
    counters = [0] * 9
    # This regex finds and removes existing numbering to avoid duplication
    numbering_pattern = re.compile(r'^\s*\d+(\.\d+)*[.\s\u3000]*')

    for p in doc_obj.paragraphs:
        if not (p.style and p.style.name.startswith('Heading')):
            continue

        try:
            level = int(p.style.name.split(' ')[-1])

            # Strip existing numbering from the paragraph to prevent duplication
            # We check the full paragraph text for a pattern match
            if numbering_pattern.match(p.text):
                # If matched, we iterate through the runs to remove the numbering
                # This is complex because numbering may span multiple runs
                # A simpler approach for now is to clear and rewrite the paragraph text
                # This might lose some formatting in complex cases, but is more reliable for numbering
                text_without_numbering = numbering_pattern.sub('', p.text).lstrip()
                # Clear existing runs
                for run in p.runs:
                    run.clear()
                # Add back the text in a new run
                p.add_run(text_without_numbering)

            # Update counters for the current level
            counters[level - 1] += 1
            # Reset counters for all deeper levels
            for i in range(level, 9):
                counters[i] = 0
            
            # Generate the new numbering string
            numbering_str = ".".join(map(str, counters[:level]))
            
            # Prepend the new numbering to the first run
            if p.runs:
                p.runs[0].text = f"{numbering_str} {p.runs[0].text}"
            else:
                p.add_run(f"{numbering_str} ")

        except (ValueError, IndexError):
            continue

# --- Streamlit App ---

st.set_page_config(layout="centered")
st.title("📄 Word 标题层级与编号修正器")

st.markdown("""
这个工具首先修正您 Word 文档中的标题层级，然后为它们生成正确的编号。

**核心功能:**
1.  **智能层级压缩**: 工具会分析每个章节，如果存在跳级（例如，只有1、3、5级），它会自动将它们压缩为连续的级别（1、2、3级）。
2.  **自动生成编号**: 在层级修正后，为所有标题添加或更新为正确的层级编号 (例如: `1`, `1.1`, `1.1.1`)。
3.  **保留格式**: 在操作时，会尽量保留您原有的标题文字格式（如加粗、颜色等）。

请上传您的 `.docx` 文件开始。
""")

uploaded_file = st.file_uploader(
    "上传您的 .docx 文档",
    type=['docx'],
    label_visibility="collapsed"
)

if uploaded_file:
    st.success(f"文件上传成功: **{uploaded_file.name}**")

    if st.button("🚀 开始处理并生成下载文件", type="primary", use_container_width=True):
        with st.spinner("正在分析和处理文档，请稍候..."):
            try:
                document = Document(uploaded_file)
                
                # Step 1: Correct the heading hierarchy
                correct_heading_hierarchy(document)
                
                # Step 2: Apply numbering to the corrected hierarchy
                apply_heading_numbering(document)
                
                # Save the processed document to a memory stream
                file_stream = io.BytesIO()
                document.save(file_stream)
                file_stream.seek(0)
                
                st.success("🎉 文档处理完成！")

                new_file_name = f"编号修正_{uploaded_file.name}"
                
                st.download_button(
                    label="📥 点击下载修改后的文档",
                    data=file_stream,
                    file_name=new_file_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"处理文档时发生意外错误: {e}")
                st.error("请确保文件未损坏且为有效的 .docx 格式。")