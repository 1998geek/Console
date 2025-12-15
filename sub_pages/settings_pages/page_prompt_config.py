import streamlit as st
import sys
import os

# This is needed for streamlit to find the modules in app_config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_config.prompt_config import load_prompt, save_prompt
from app_config.settings import get_setting, update_setting

def render_prompt_config_page():
    st.title("⚙️ 标书审核配置")

    st.markdown("""
    在这里，您可以查看和修改用于标书图片智能审核的各项配置。
    - **Prompt**: 定义了AI在执行审核任务时的角色、规则和输出格式。
    - **通用设置**: 配置通用的参数，例如批量处理的图片数量阈值。
    - **保存**: 修改完成后，点击相应板块下的“保存”按钮即可生效。
    """)

    tab1, tab2, tab3 = st.tabs(["单项审核Prompt", "批量审核Prompt", "通用设置"])

    with tab1:
        st.subheader("单项审核 (Single Item Review)")
        # Use a session_state key to avoid reloading prompt on every interaction
        if 'prompt_single' not in st.session_state:
            st.session_state.prompt_single = load_prompt(is_batch=False)

        edited_prompt_single = st.text_area(
            "Prompt for Single Item Review",
            value=st.session_state.prompt_single,
            height=400,
            key="text_area_single"
        )

        if st.button("💾 保存单项审核Prompt", use_container_width=True, key="save_single"):
            if edited_prompt_single:
                save_prompt(edited_prompt_single, is_batch=False)
                st.session_state.prompt_single = edited_prompt_single # Update session state
                st.success("✅ 单项审核Prompt已成功保存！")
                st.toast("🎉 Prompt 已保存", icon="✅")
            else:
                st.error("❌ Prompt内容不能为空！")

    with tab2:
        st.subheader("批量审核 (Batch Review)")
        if 'prompt_batch' not in st.session_state:
            st.session_state.prompt_batch = load_prompt(is_batch=True)

        edited_prompt_batch = st.text_area(
            "Prompt for Batch Review",
            value=st.session_state.prompt_batch,
            height=400,
            key="text_area_batch"
        )
        if st.button("💾 保存批量审核Prompt", use_container_width=True, key="save_batch"):
            if edited_prompt_batch:
                save_prompt(edited_prompt_batch, is_batch=True)
                st.session_state.prompt_batch = edited_prompt_batch # Update session state
                st.success("✅ 批量审核Prompt已成功保存！")
                st.toast("🎉 Prompt 已保存", icon="✅")
            else:
                st.error("❌ Prompt内容不能为空！")

    with tab3:
        st.subheader("通用设置 (General Settings)")
        
        if 'image_batch_threshold' not in st.session_state:
            st.session_state.image_batch_threshold = get_setting("IMAGE_BATCH_THRESHOLD")

        new_threshold = st.number_input(
            "图片批量处理阈值 (IMAGE_BATCH_THRESHOLD)",
            min_value=1,
            max_value=20,
            value=st.session_state.image_batch_threshold,
            step=1,
            help="当单个章节中的图片数量超过此阈值时，将触发批量审核模式。建议值为3-5。"
        )
        
        if st.button("💾 保存通用设置", use_container_width=True, key="save_settings"):
            update_setting("IMAGE_BATCH_THRESHOLD", new_threshold)
            st.session_state.image_batch_threshold = new_threshold # Update session state
            st.success(f"✅ 通用设置已成功保存！图片批量处理阈值已更新为 {new_threshold}。")
            st.toast("⚙️ 设置已保存", icon="✅")


# Main function call
st.set_page_config(page_title="Prompt配置", layout="wide")
render_prompt_config_page()