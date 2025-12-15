import streamlit as st
from function.dify_client import DifyClient # Import the UI-agnostic client
import requests # Still needed for specific exception types if we catch them explicitly
from app_config.keys_config import DIFY_API_BASE_URL_DEFAULT, DIFY_API_KEY_DEFAULT

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# --- Initialize Dify Client ---
api_base_url = DIFY_API_BASE_URL_DEFAULT # Replace with st.secrets in production
api_key = DIFY_API_KEY_DEFAULT           # Replace with st.secrets in production

@st.cache_resource # Good practice to cache resource-like objects
def get_dify_client():
    return DifyClient(api_base_url=api_base_url, api_key=api_key, user_id="streamlit_app_user")

dify_client_instance = get_dify_client()

# Initialize session state variables
if "messages_dify_workflow" not in st.session_state:
    st.session_state.messages_dify_workflow = []
if "dify_conversation_id" not in st.session_state:
    st.session_state.dify_conversation_id = None 
if "user_input_processed" not in st.session_state:
    st.session_state.user_input_processed = True

# --- Top controls: Conversation ID and Clear Chat History ---
col1, col2 = st.columns([3, 1], vertical_alignment="bottom")

with col1:
    conv_id_display = st.session_state.get("dify_conversation_id", "None")
    st.caption(f"Conversation ID (from Dify): **{conv_id_display}**")

with col2:
    if st.button("Clear Chat History", type="primary"):
        st.session_state.messages_dify_workflow = []
        st.session_state.dify_conversation_id = None 
        st.session_state.user_input_processed = True 
        st.rerun()
st.markdown("---") 

# Display chat messages_dify_workflow from history
for message in st.session_state.messages_dify_workflow:
    # avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    # with st.chat_message(message["role"], avatar=avatar):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Main chat input
if prompt := st.chat_input("What would you like to ask Dify?"):
    st.session_state.messages_dify_workflow.append({"role": "user", "content": prompt})
    st.session_state.user_input_processed = False 
    st.rerun() 

# Logic for handling bot response
if not st.session_state.user_input_processed and \
   st.session_state.messages_dify_workflow and \
   st.session_state.messages_dify_workflow[-1]["role"] == "user":
    
    last_user_prompt = st.session_state.messages_dify_workflow[-1]["content"]
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_bot_response = ""
        current_conv_id = st.session_state.get("dify_conversation_id")
        previous_conv_id_in_session = current_conv_id # To check if it changes

        try:
            for item in dify_client_instance.chat_stream(last_user_prompt, current_conv_id):
                if isinstance(item, str): # This is a content chunk
                    full_bot_response += item
                    message_placeholder.markdown(full_bot_response + "▌")
                elif isinstance(item, dict):
                    item_type = item.get("type")
                    if item_type == "metadata":
                        new_conv_id = item.get("conversation_id")
                        if new_conv_id:
                            st.session_state.dify_conversation_id = new_conv_id
                            # print(f"APP: Dify Conversation ID updated to: {new_conv_id}")
                    elif item_type == "error":
                        error_source = item.get("source", "unknown")
                        error_msg = item.get("message", "An error occurred.")
                        st.error(f"Error from Dify ({error_source}): {error_msg}")
                        # print(f"APP: Displayed Dify stream error: {item.get('details')}")
                        # Potentially add to chat history as an error message
                        full_bot_response += f"\n\n*Error: {error_msg}*" 
                        break # Stop processing further for this response on stream error
            
            message_placeholder.markdown(full_bot_response) # Display final message

        except requests.exceptions.HTTPError as e:
            err_msg = f"HTTP Error: {e.response.status_code} - {e.response.reason}. "
            try:
                details = e.response.json() # Dify often returns JSON errors
                err_msg += details.get("message", "")
                if "code" in details: err_msg += f" (Code: {details.get('code')})"
            except ValueError: # Not JSON
                err_msg += e.response.text[:200] # First 200 chars
            st.error(err_msg)
            full_bot_response += f"\n\n*Error: Connection or server error.*" # Append to chat
            message_placeholder.markdown(full_bot_response)
        except requests.exceptions.RequestException as e:
            st.error(f"API Request Error: Could not connect to Dify API. {e}")
            full_bot_response += f"\n\n*Error: Could not connect.*" # Append to chat
            message_placeholder.markdown(full_bot_response)
        except Exception as e: # Catch any other unexpected errors from the client
            st.error(f"An unexpected error occurred: {e}")
            full_bot_response += f"\n\n*Error: An unexpected error occurred processing your request.*"
            message_placeholder.markdown(full_bot_response)

    if full_bot_response or not st.session_state.user_input_processed : # Add even if it's just an error message collected
        # Ensure we only add if the last message is indeed the user prompt we just processed
        if st.session_state.messages_dify_workflow and \
           st.session_state.messages_dify_workflow[-1]["role"] == "user" and \
           st.session_state.messages_dify_workflow[-1]["content"] == last_user_prompt:
            st.session_state.messages_dify_workflow.append({"role": "assistant", "content": full_bot_response if full_bot_response else "No response or error processing."})
    
    st.session_state.user_input_processed = True 

    # Rerun if conversation ID changed to update the display at the top
    if st.session_state.dify_conversation_id != previous_conv_id_in_session:
        st.rerun()