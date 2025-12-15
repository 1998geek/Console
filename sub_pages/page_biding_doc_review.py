import streamlit as st
import time
import random
import docx
from function.local.docx_images_info import get_chapter_data
from function.ImageReviewHandler import get_ai_client, perform_llm_check

@st.cache_resource
def initialize_ai_client():
    """
    这是一个带缓存的函数，专门用于在 Streamlit 应用中初始化 AI 客户端。
    它会调用真正的客户端创建逻辑，并处理可能出现的错误。
    """
    try:
        # 调用 ai_handler.py 中的函数来创建客户端实例
        client = get_ai_client()
        return client
    except (ValueError, RuntimeError) as e:
        # 如果创建失败（比如密钥没配置），就在界面上显示错误并停止应用
        st.error(str(e))
        st.stop()


# --- 用于显示最终审核摘要的函数 ---
def display_final_summary(all_results):
    """
    在所有章节审核完毕后，显示一个总结性的报告。
    (This function has been corrected to count individual image statuses for accuracy.)
    """
    st.markdown("---")
    st.header("🏁 智能审核最终摘要")

    if not all_results:
        st.warning("没有可供总结的审核结果。")
        return

    # Initialize counts for individual images
    total_images_count = 0
    success_images_count = 0
    warning_images_count = 0
    error_images_count = 0

    # This dictionary will still hold the overall status and a combined summary for each chapter for the detailed list.
    chapter_summary_results = {}

    for chapter_title, image_results in all_results.items():
        if not isinstance(image_results, list) or not image_results:
            continue # Skip empty or invalid results for a chapter

        # Count individual image statuses
        for res in image_results:
            if isinstance(res, dict):
                total_images_count += 1
                status = res.get('status')
                if status == 'error':
                    error_images_count += 1
                elif status == 'warning':
                    warning_images_count += 1
                elif status == 'success':
                    success_images_count += 1

        # Determine the overall status for the chapter to display in the detailed list
        statuses = {res.get('status') for res in image_results if isinstance(res, dict)}
        
        final_status = 'success'
        if 'error' in statuses:
            final_status = 'error'
        elif 'warning' in statuses:
            final_status = 'warning'

        # Combine summaries for problematic chapters to display later
        problem_summaries = [
            f"图片{i+1}: {res.get('summary', '无详细信息')}"
            for i, res in enumerate(image_results)
            if isinstance(res, dict) and res.get('status') in ['warning', 'error']
        ]
        
        chapter_summary_results[chapter_title] = {
            'status': final_status,
            'summary': "".join([f"\n- {s}" for s in problem_summaries]) if problem_summaries else "所有图片均审核通过。"
        }
    
    total_chapters = len(all_results)
    st.write(f"对 **{total_chapters}** 个章节中的 **{total_images_count}** 张图片审核已全部完成。")

    col1, col2, col3 = st.columns(3)
    # Update metrics to show image counts
    col1.metric("✅ 图片通过", f"{success_images_count} 张")
    col2.metric("⚠️ 图片警告", f"{warning_images_count} 张")
    col3.metric("❌ 图片问题", f"{error_images_count} 张")

    # The detailed list of problematic chapters remains the same
    if warning_images_count > 0 or error_images_count > 0:
        st.subheader("详细问题列表:")
        for chapter_title, result in chapter_summary_results.items():
            status = result.get('status')
            if status == 'warning':
                st.warning(f"**{chapter_title}:** {result['summary']}")
            elif status == 'error':
                st.error(f"**{chapter_title}:** {result['summary']}")

# --- 渲染单个章节内容的通用函数 ---
def render_chapter(chapter_title, chapter_data, check_result=None):
    """
    渲染单个章节的UI，包括内容、图片和可选的审核结果。
    """
    images = chapter_data['images']
    content = chapter_data['content']
    problem_images_count = sum(1 for img in images if isinstance(img, str))
    expander_title = f"章节: {chapter_title} (共 {len(images)} 张图片)"
    if problem_images_count > 0:
        expander_title += f" - :red[**发现 {problem_images_count} 张问题图片！**]"

    with st.expander(expander_title, expanded=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("章节文本内容")
            st.text_area(
                "Content", value=content, height=400, 
                disabled=True, label_visibility="collapsed", key=f"content_{chapter_title}_{random.random()}"
            )
        with col2:
            st.subheader("章节内图片")
            for i_img, img_data in enumerate(images):
                if isinstance(img_data, str) and "UNSUPPORTED_FORMAT" in img_data:
                    parts = img_data.split(':')
                    filename = parts[-1]
                    # Extract format from placeholder like "UNSUPPORTED_FORMAT_WMF"
                    img_format = parts[0].split('_')[-1] if len(parts) > 1 and '_' in parts[0] else "未知"
                    st.warning(f"图片 {i_img+1} ({filename}) 是 **{img_format}** 格式，无法在此预览。")
                    st.info("建议：请在Word中将此图另存为PNG或JPG格式后重新插入。")
                elif isinstance(img_data, str) and "ERROR" in img_data:
                    st.error(f"图片 {i_img+1} 加载失败: {img_data}")
                else:
                    st.image(img_data, caption=f"图片 {i_img+1}", width='stretch')
    
    if check_result and isinstance(check_result, list):

        # 使用 for 循环遍历列表中的每一个审核结果
        for index, result_item in enumerate(check_result):
            # 为每张图片的结果添加一个子标题，使其更清晰
            st.markdown(f"**图片 {index + 1} 的审核结果:**")
            # 确保列表中的元素是有效的字典格式
            if isinstance(result_item, dict) and 'status' in result_item:
                status = result_item['status']
                summary = result_item.get('summary', '（无摘要信息）') # 使用.get()更安全

                # 在循环内部，应用您原来的逻辑
                if status == 'success':
                    st.success(summary)
                elif status == 'warning':
                    st.warning(summary)
                elif status == 'error':
                    st.error(summary)
                else: # 包含 'info' 等其他情况
                    st.info(summary)
            else:
                # 如果列表中的某一项格式不正确，也明确提示
                st.error(f"图片 {index + 1} 的返回结果格式不正确: {result_item}")
        # 所有结果显示完毕后，画一条分割线
        st.markdown("---")

def reset_page_state():
    """
    重置与标书审核页面相关的会话状态。
    """
    keys_to_delete = [
        'processed_file', 
        'chapter_data', 
        'check_results', 
        'initial_render_complete'
    ]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]

# --- UI渲染主函数 ---
def render_ui():
    """
    根据 session_state 中的数据渲染整个用户界面。
    """

    st.title("📄 标书智能检查系统 - 图片审核")
    st.write("请上传您的 `.docx` 格式标书文件，系统将自动提取包含图片的章节及其对应的文本内容。")
    st.info("💡 系统目前仅支持预览 JPG (JPEG) 和 PNG 格式的图片，其他格式（如 WMF, EMF, BMP 等）将被标记但无法显示。")
    st.write("上传 `.docx` 格式标书，系统将提取含图片的章节，并可启动AI模拟审核检查图文一致性、图片质量等问题。")

    uploaded_file = st.file_uploader("选择一个Word文档...", type=["docx"])

    # 当用户删除文件时，重置页面状态
    if uploaded_file is None and 'processed_file' in st.session_state:
        reset_page_state()

    # 1. 处理文件上传
    if uploaded_file is not None:
        if 'processed_file' not in st.session_state or st.session_state.processed_file != uploaded_file.name:
            try:
                with st.spinner("正在解析文档..."):
                    document = docx.Document(uploaded_file)
                    st.session_state.chapter_data = get_chapter_data(document)
                st.success(f"文件 “{uploaded_file.name}” 解析成功！")
                st.session_state.processed_file = uploaded_file.name
                st.session_state.check_results = {} 
                if 'initial_render_complete' in st.session_state:
                    del st.session_state['initial_render_complete']
            except Exception as e:
                st.error(f"处理文件时发生严重错误：{e}")
                reset_page_state()
    
    # 2. 如果没有数据，显示提示信息
    if 'chapter_data' not in st.session_state:
        st.info("请上传一个文件以开始分析。")
        return

    # 3. 如果有数据，显示主要内容
    chapter_data = st.session_state.chapter_data
    
    total_images_count = sum(len(data['images']) for data in chapter_data.values())
    total_problem_images = sum(1 for data in chapter_data.values() for img in data['images'] if isinstance(img, str))
    summary_message = f"提取完成！共在 **{len(chapter_data)}** 个章节中找到了 **{total_images_count}** 张图片。"
    if total_problem_images > 0:
        summary_message += f" :red[**其中包含 {total_problem_images} 张问题图片。**]"
    st.success(summary_message)

    st.markdown("---")

    # 4. 显示审核按钮并处理点击事件
    if st.button("🚀 开始智能审核全部章节", use_container_width=True, type="primary"):
        st.header("审查进度")
        st.session_state.check_results = {}
        
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        st.subheader("已审核章节详情:")
        for i, (chapter_title, data) in enumerate(chapter_data.items()):
            status_text.info(f"🔍 正在检查章节 {i+1}/{len(chapter_data)}: **{chapter_title}**")
            
            result = perform_llm_check(initialize_ai_client(), data['content'], data['images'])
            st.session_state.check_results[chapter_title] = result
            
            render_chapter(chapter_title, data, check_result=result)
            progress_bar.progress((i + 1) / len(chapter_data))

        status_text.empty()
        progress_bar.empty()
        st.success("✅ 所有章节均已审核完毕！请查看下方最终摘要。")
    
    # 5. 显示章节列表和已有的审核结果
    else:
        st.header("📄 章节内容概览")
        if 'initial_render_complete' not in st.session_state:
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            for i, (title, data) in enumerate(chapter_data.items()):
                status_text.info(f"🎨 正在渲染章节 {i+1}/{len(chapter_data)}: **{title}**")
                render_chapter(title, data)
                progress_bar.progress((i + 1) / len(chapter_data))

            status_text.empty()
            progress_bar.empty()
            st.session_state.initial_render_complete = True
        # else:
        #     for title, data in chapter_data.items():
        #         result = st.session_state.get('check_results', {}).get(title)
        #         render_chapter(title, data, check_result=result)
    
    # 6. 如果有审核结果，显示最终摘要
    if st.session_state.get('check_results'):
        display_final_summary(st.session_state.check_results)

st.set_page_config(page_title="标书图片审核系统", layout="wide")
render_ui()