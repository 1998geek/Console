import streamlit as st
import time
from src.services.api_client import api_client
from src.utils.ui import TaskProgress # [引入新工具]

def show():
    st.title(":material/movie: Sora 视频生成")

    if "sora_results" not in st.session_state:
        st.session_state.sora_results = []

    with st.container():
        st.info("💡 **提示**：输入一段文字描述，AI 将为您生成高清视频。")
        col1, col2 = st.columns([3, 1])
        with col1:
            prompt = st.text_area("视频描述 (Prompt)", height=100, placeholder="例如：一只在大雪中奔跑的金色寻回犬，电影质感，4k分辨率...")
        with col2:
            style = st.selectbox("视频风格", ["写实 (Realistic)", "动画 (Animation)", "赛博朋克 (Cyberpunk)", "素描 (Sketch)"])
            duration = st.select_slider("时长 (秒)", options=[5, 10, 15, 60], value=5)
        
        run = st.button("🎬 开始生成视频", type="primary", use_container_width=True)

    if run and prompt:
        st.session_state.sora_results = []
        progress = TaskProgress(title="准备生成环境...") # [使用新工具]
        
        try:
            progress.update(10, "正在构建场景描述...")
            data_payload = {"prompt": prompt, "style": style, "duration": duration}
            
            # 长耗时阶段
            progress.update(50, "⚡️ 已发送指令，AI 正在渲染每一帧 (请耐心等待)...")
            res_content, _ = api_client.upload_and_download("/multimodal/sora/generate", data=data_payload, timeout=300)
            
            progress.update(90, "视频生成完毕，正在接收数据流...")
            
            if res_content:
                default_name = f"sora_video_{int(time.time())}.mp4"
                st.session_state.sora_results.append({
                    "prompt": prompt,
                    "default_name": default_name,
                    "data": res_content,
                    "mime": "video/mp4"
                })
                progress.finish("✨ 视频生成成功！")
            else:
                progress.fail("❌ 生成失败")
                st.error("❌ 后端未返回数据。")
                
        except Exception as e:
            progress.fail("❌ 发生错误")
            st.error(f"Error: {e}")

    if st.session_state.sora_results:
        st.divider()
        st.subheader("生成结果")
        for i, res in enumerate(st.session_state.sora_results):
            with st.container(border=True):
                st.video(res['data'])
                # [关键] 底部对齐
                c1, c2 = st.columns([3, 1], vertical_alignment="bottom") 
                with c1:
                    st.caption(f"**提示词**: {res['prompt']}")
                    new_name = st.text_input("重命名视频文件:", value=res['default_name'], key=f"rename_sora_{i}")
                with c2:
                    st.download_button(
                        label="⬇️ 下载视频",
                        data=res['data'],
                        file_name=new_name,
                        mime=res['mime'],
                        type="primary",
                        use_container_width=True,
                        key=f"dl_sora_{i}"
                    )

render = show