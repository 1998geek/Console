from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from sub_pages.init_sidebar import init_sidebar
from login import render_login_page

st.set_page_config(page_title="ComLan", page_icon=":material/home:", layout="wide", initial_sidebar_state="auto", menu_items=None)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def logout():
    st.write("Are you sure you want to log out?")
    st.write("You will be redirected to the login page.")
    if st.button("Log out", type="primary"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

init_sidebar(render_login_page, logout)