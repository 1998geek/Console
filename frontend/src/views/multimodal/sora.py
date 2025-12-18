import streamlit as st
import requests
import time
from src.services.api_client import api_client

def show():
    st.title("🎬 Azure Sora 视频生成器 (模拟)")
    st.markdown("一个使用 Sora 模型生成视频的交互式 Web 应用（当前为模拟任务流）。")

    st.header("📝 视频生成参数")

    with st.form("sora_form"):
        prompt = st.text_area(
            "**提示词 (Prompt)**",
            height=100,
            value="A sweeping aerial shot of a vast mountain range at sunrise, with golden light casting long shadows over the rugged peaks.",
            help="详细描述你想要生成的视频内容。"
        )

        col1, col2 = st.columns(2)
        with col1:
            resolution = st.selectbox(
                "**分辨率 (Resolution)**",
                options=["854x480 (16:9 宽屏)", "480x854 (9:16 竖屏)", "480x480 (1:1 方形)"],
                index=0
            )
            width, height = map(int, resolution.split(' ')[0].split('x'))

        with col2:
            duration = st.slider(
                "**视频时长 (秒)**",
                min_value=1,
                max_value=15,
                value=5,
                help="选择视频的生成时长。"
            )

        submitted = st.form_submit_button("🚀 生成视频")

    if submitted:
        try:
            st.subheader("处理流程")
            with st.status("1. 正在提交视频生成任务...", expanded=True) as status_container:
                res = api_client.post(
                    "/multimodal/sora/generate",
                    data={"prompt": prompt, "width": str(width), "height": str(height), "duration": str(duration)},
                    form_data=True
                )
                if not res or not res.get("task_id"):
                    status_container.update(label="❌ 任务提交失败", state="error")
                    st.error("视频生成任务提交失败。")
                    st.stop()

                task_id = res["task_id"]
                status_container.update(label=f"✅ 任务提交成功！Task ID: {task_id}", state="complete")
                st.info(f"任务已提交，Task ID 为: `{task_id}`")

            st.write("---")
            st.subheader("2. 正在轮询任务状态...")

            status_placeholder = st.empty()
            progress_bar = st.progress(0)

            start_time = time.time()
            max_poll_time = 120

            status = "pending"
            result_url = None
            while status not in ["succeeded", "failed"] and (time.time() - start_time) < max_poll_time:
                elapsed_time = int(time.time() - start_time)
                progress_value = min(elapsed_time / max_poll_time, 0.9)
                progress_bar.progress(progress_value)
                status_placeholder.info(f"⏳ **状态: {status}** (已等待 {elapsed_time} 秒)")

                time.sleep(2)
                status_res = api_client.get(f"/multimodal/sora/status/{task_id}")
                status = status_res.get("status")
                result_url = status_res.get("result")

            st.write("---")
            st.subheader("3. 最终结果")

            if status == "succeeded":
                progress_bar.progress(1.0)
                status_placeholder.success("✅ **状态: succeeded** - 视频生成成功！")
                if result_url:
                    st.video(result_url)
                    output_name = st.text_input("保存文件名", value=f"sora_output_{task_id}.mp4", key=f"sora_name_{task_id}")
                    try:
                        resp = requests.get(result_url, timeout=300)
                        resp.raise_for_status()
                        st.download_button(
                            label="📥 下载视频 (.mp4)",
                            data=resp.content,
                            file_name=output_name,
                            mime="video/mp4"
                        )
                    except Exception:
                        st.link_button("点击下载视频", result_url, icon="📥")
                else:
                    st.warning("⚠️ 任务状态为成功，但未返回视频地址。")
            elif status == "failed":
                progress_bar.empty()
                status_placeholder.error("❌ **状态: failed** - 视频生成失败。")
            else:
                progress_bar.empty()
                status_placeholder.warning(f"⚠️ 任务超时，最后状态为: {status}")
        except Exception as e:
            st.error(f"发生未知错误: {e}")

render = show
