import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import json
st.set_page_config(initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)
# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("pythonProject4/test.json")
    firebase_admin.initialize_app(cred)

# Streamlit app
st.title("Image Comparison App with Firebase Authentication")

# User authentication
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


def login(email, password):
    try:
        user = auth.get_user_by_email(email)
        st.session_state["logged_in"] = True
        st.session_state["user"] = user
        st.success("Logged in successfully!")
    except firebase_admin.auth.AuthError as e:
        st.error(f"Failed to log in: {str(e)}")
    except:
        st.error("Invalid credentials")


def logout():
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.success("Logged out successfully!")


if not st.session_state["logged_in"]:
    st.header("Log In")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Log In"):
        login(email, password)
        st.switch_page("pages/aws_main.py")

else:
    st.header("Welcome to the App")
    st.write("You are logged in as:", st.session_state["user"].email)
    if st.button("Log Out"):
        logout()
    if st.button("Return to App"):
        st.switch_page("pages/aws_main.py")
