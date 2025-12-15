import streamlit as st
import requests
import time

from app_config.keys_config import AZURE_OPENAI_TOKEN, AZURE_OPENAI_ENDPOINT

st.title("🎬 Azure Sora 视频生成器")
st.markdown("一个使用 Azure OpenAI Sora 模型生成视频的交互式 Web 应用。")

# 从 st.secrets 或环境变量中获取默认值，如果找不到则为空
endpoint = AZURE_OPENAI_ENDPOINT
subscription_key = AZURE_OPENAI_TOKEN
deployment = "sora"
api_version = "preview"

# --- 主界面：用户输入 ---
st.header("📝 视频生成参数")

with st.form("sora_form"):
    prompt = st.text_area(
        "**提示词 (Prompt)**", 
        height=100,
        # value="Looking at the Mona Lisa painting. Van Gogh stands in front of the painting.",
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
        # 解析分辨率
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

# --- 任务处理逻辑 ---
if submitted:
    try:
        # --- 1. 提交生成任务 ---
        path = f'openai/v1/video/generations/jobs'
        params = f'?api-version={api_version}'
        constructed_url = endpoint.strip('/') + '/' + path + params

        headers = {
            'Api-Key': subscription_key,
            'Content-Type': 'application/json',
        }

        body = {
            "prompt": prompt,
            "n_variants": "1",
            "n_seconds": str(duration),
            "height": str(height),
            "width": str(width),
            "model": deployment,
        }

        st.subheader("处理流程")
        with st.status("1. 正在提交视频生成任务...", expanded=True) as status_container:
            job_response = requests.post(constructed_url, headers=headers, json=body)
            
            if not job_response.ok:
                status_container.update(label="❌ 任务提交失败", state="error")
                st.error("视频生成任务提交失败。")
                st.json(job_response.json())
                st.stop()
            
            job_info = job_response.json()
            job_id = job_info.get("id")
            status = job_info.get("status")
            
            status_container.update(label=f"✅ 任务提交成功！Job ID: {job_id}", state="complete")
            st.info(f"任务已提交，Job ID 为: `{job_id}`")

        # --- 2. 轮询任务状态 ---
        status_url = f"{endpoint.strip('/')}/openai/v1/video/generations/jobs/{job_id}?api-version={api_version}"
        
        st.write("---")
        st.subheader("2. 正在轮询任务状态...")
        
        # 创建一个空占位符用于显示实时状态
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        start_time = time.time()
        max_poll_time = 300 # 最长等待5分钟

        while status not in ["succeeded", "failed"] and (time.time() - start_time) < max_poll_time:
            # 更新进度条和状态文本
            elapsed_time = int(time.time() - start_time)
            progress_value = min(elapsed_time / max_poll_time, 0.9)
            progress_bar.progress(progress_value)
            status_placeholder.info(f"⏳ **状态: {status}** (已等待 {elapsed_time} 秒)")
            
            time.sleep(5)  # 等待5秒再查询
            
            job_response = requests.get(status_url, headers=headers).json()
            status = job_response.get("status")

        # --- 3. 处理最终结果 ---
        st.write("---")
        st.subheader("3. 最终结果")

        if status == "succeeded":
            progress_bar.progress(1.0)
            status_placeholder.success("✅ **状态: succeeded** - 视频生成成功！")
            
            generations = job_response.get("generations", [])
            if generations:
                generation_id = generations[0].get("id")
                
                with st.spinner("正在下载视频..."):
                    video_url = f'{endpoint.strip("/")}/openai/v1/video/generations/{generation_id}/content/video{params}'
                    video_response = requests.get(video_url, headers=headers)

                    if video_response.ok:
                        video_bytes = video_response.content
                        st.video(video_bytes)
                        
                        st.download_button(
                            label="📥 下载视频 (.mp4)",
                            data=video_bytes,
                            file_name=f"sora_output_{job_id}.mp4",
                            mime="video/mp4"
                        )
                    else:
                        st.error("视频下载失败。")
                        st.json(video_response.json())
            else:
                st.warning("⚠️ 任务状态为成功，但未返回任何视频生成结果。")

        elif status == "failed":
            progress_bar.empty()
            status_placeholder.error("❌ **状态: failed** - 视频生成失败。")
            st.json(job_response)
        else:
            progress_bar.empty()
            status_placeholder.warning(f"⚠️ 任务超时，最后状态为: {status}")

    except requests.exceptions.RequestException as e:
        st.error(f"网络请求失败，请检查 Endpoint 地址和网络连接: {e}")
    except Exception as e:
        st.error(f"发生未知错误: {e}")