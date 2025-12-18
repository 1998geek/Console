import streamlit as st 
import re 
from src.services.api_client import api_client 
 
def show(): 
    st.subheader(":material/rocket_launch: Xorbits Inference Chat") 
 
    AVAILABLE_MODELS = ["qwen3", "qwen2.5-vl-instruct"] 
     
    with st.sidebar: 
        st.header("模型配置") 
        selected_model = st.selectbox( 
            "选择一个模型进行对话:", 
            options=AVAILABLE_MODELS, 
            index=0 
        ) 
        st.info(f"当前选择的模型: **{selected_model}**") 
 
        show_thinking_process = False 
        if "qwen3" in selected_model: 
            show_thinking_process = st.toggle( 
                "显示思考过程 (Show Thinking)", 
                value=False, 
                help="开启后，Qwen3模型将展示其`<think>`...`</think>`的思考步骤。" 
            ) 
 
        if 'qwen2.5-vl' in selected_model: 
            st.warning("提示: 您选择的是一个多模态模型 (VL)，但此界面仅支持文本对话。") 
 
        if st.button("清除聊天记录", type="primary"): 
            st.session_state.xinference_messages = [] 
            st.rerun() 
 
    if "xinference_messages" not in st.session_state: 
        st.session_state.xinference_messages = [] 
 
    for message in st.session_state.xinference_messages: 
        with st.chat_message(message["role"]): 
            st.markdown(message["content"]) 
 
    if prompt := st.chat_input("请输入您的问题..."): 
        st.session_state.xinference_messages.append({"role": "user", "content": prompt}) 
        with st.chat_message("user"): 
            st.markdown(prompt) 
 
        with st.chat_message("assistant"): 
            message_placeholder = st.empty() 
            raw_full_response = "" 
             
            payload = { 
                "model": selected_model, 
                "messages": st.session_state.xinference_messages, 
                "show_thinking": show_thinking_process 
            } 
 
            try: 
                stream = api_client.stream_post("/agent/xinference/chat", json=payload) 
                 
                for chunk in stream: 
                    if chunk: 
                        raw_full_response += chunk 
                        display_text = raw_full_response 
                        if not show_thinking_process: 
                            display_text = re.sub(r"<think>.*?</think>", "", raw_full_response, flags=re.DOTALL).strip() 
                         
                        message_placeholder.markdown(display_text + "▌") 
 
                final_display = raw_full_response 
                if not show_thinking_process: 
                    final_display = re.sub(r"<think>.*?</think>", "", raw_full_response, flags=re.DOTALL).strip() 
                 
                message_placeholder.markdown(final_display) 
                st.session_state.xinference_messages.append({"role": "assistant", "content": final_display}) 
 
            except Exception as e: 
                st.error(f"调用模型时出错: {e}") 
 
render = show
