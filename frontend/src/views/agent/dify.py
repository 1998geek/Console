import streamlit as st 
from src.services.api_client import api_client 
 
def show(): 
    if "messages_dify_workflow" not in st.session_state: 
        st.session_state.messages_dify_workflow = [] 
    if "dify_conversation_id" not in st.session_state: 
        st.session_state.dify_conversation_id = None 
     
    col1, col2 = st.columns([3, 1], vertical_alignment="bottom") 
 
    with col1: 
        conv_id_display = st.session_state.get("dify_conversation_id", "None") 
        st.caption(f"Conversation ID (from Dify): **{conv_id_display}**") 
 
    with col2: 
        if st.button("Clear Chat History", type="primary"): 
            st.session_state.messages_dify_workflow = [] 
            st.session_state.dify_conversation_id = None 
            st.rerun() 
    st.markdown("---") 
 
    for message in st.session_state.messages_dify_workflow: 
        with st.chat_message(message["role"]): 
            st.markdown(message["content"]) 
 
    if prompt := st.chat_input("What would you like to ask Dify?"): 
        st.session_state.messages_dify_workflow.append({"role": "user", "content": prompt}) 
        with st.chat_message("user"): 
            st.markdown(prompt) 
 
        with st.chat_message("assistant"): 
            message_placeholder = st.empty() 
            message_placeholder.markdown("Thinking...") 
             
            payload = { 
                "query": prompt, 
                "conversation_id": st.session_state.dify_conversation_id 
            } 
             
            res = api_client.post("/agent/dify/chat", json=payload) 
             
            if res: 
                answer = res.get("answer", "") 
                new_conv_id = res.get("conversation_id") 
                 
                if new_conv_id: 
                    st.session_state.dify_conversation_id = new_conv_id 
                 
                message_placeholder.markdown(answer) 
                st.session_state.messages_dify_workflow.append({"role": "assistant", "content": answer}) 
                 
                if new_conv_id and new_conv_id != conv_id_display: 
                    st.rerun() 
            else: 
                message_placeholder.error("Error connecting to Dify Agent.") 
 
render = show
