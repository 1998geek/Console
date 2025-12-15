from dotenv import load_dotenv
load_dotenv()

from sub_pages.init_sidebar import init_sidebar
import streamlit as st
st.set_page_config(page_title="AI Assistant", page_icon=":material/home:", layout="wide", initial_sidebar_state="auto", menu_items=None)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("Welcome Let's build Copilot!")
    st.write("Please log in to continue (username `*****`, password `*****`).")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log in", type="primary", use_container_width=True):
        # if username == "admin" and password == "admin123456":
        st.session_state.logged_in = True
        st.session_state.is_admin = True
        st.success("Logged in successfully!")
        st.rerun()
        #     st.rerun()
        # else:
        #     st.error("Incorrect username or password")

def logout():
    st.write("Are you sure you want to log out?")
    st.write("You will be redirected to the login page.")
    if st.button("Log out", type="primary"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

init_sidebar(login, logout)