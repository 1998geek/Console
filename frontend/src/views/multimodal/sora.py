import streamlit as st
import time
from src.services.api_client import api_client

def show():
    st.title("🎬 Sora 视频生成 (模拟)")
    prompt = st.text_area("输入视频描述", value="一只在太空漫步的柯基犬", height=120)
    btn = st.button("生成视频", type="primary")
    if btn:
        with st.spinner("正在提交任务..."):
            res = api_client.post("/multimodal/sora/generate", data={"prompt": prompt}, form_data=True)
        if not res or not res.get("task_id"):
            st.error("任务提交失败")
            return
        task_id = res["task_id"]
        status_box = st.empty()
        while True:
            with status_box.container():
                st.info("正在生成中...")
            time.sleep(2)
            status_res = api_client.get(f"/multimodal/sora/status/{task_id}")
            if not status_res or not status_res.get("status"):
                st.error("查询状态失败")
                break
            if status_res["status"] == "processing" or status_res["status"] == "pending":
                continue
            if status_res["status"] == "completed":
                video_url = status_res.get("result")
                st.success("生成完成")
                if video_url:
                    st.video(video_url)
                break
            if status_res["status"] == "failed":
                st.error("生成失败")
                break

render = show
