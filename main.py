import streamlit as st
import pandas as pd
import os

# Setup page configuration
st.set_page_config(
    page_title="Digital Clone SaaS",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed"  # This collapses the sidebar by default
)

# Add custom CSS to hide the sidebar completely
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

# Initialize session state for login status if not exists
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_creator = None

# Function to handle creator login
def login_creator(username, password):
    # In a real app, you would validate against a secure database
    # For this demo, we'll use a simple CSV file
    try:
        if os.path.exists("data/creators.csv"):
            df = pd.read_csv("data/creators.csv")
            creator = df[df["username"] == username]
            if not creator.empty and creator.iloc[0]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_creator = username
                st.switch_page("pages/dashboard.py")
                return True
        return False
    except Exception as e:
        st.error(f"Login error: {e}")
        return False

# Function to handle creator signup
def signup_creator(username, name, password):
    try:
        # Create creators directory if it doesn't exist
        os.makedirs("data/creators", exist_ok=True)
        
        # Check if creators.csv exists, if not create it
        if not os.path.exists("data/creators.csv"):
            pd.DataFrame(columns=["username", "name", "password"]).to_csv("data/creators.csv", index=False)
        
        # Check if username already exists
        df = pd.read_csv("data/creators.csv")
        if username in df["username"].values:
            st.error("Username already exists. Please choose another one.")
            return False
        
        # Add new creator
        new_creator = pd.DataFrame([[username, name, password]], columns=["username", "name", "password"])
        df = pd.concat([df, new_creator], ignore_index=True)
        df.to_csv("data/creators.csv", index=False)
        
        # Create creator's directory
        os.makedirs(f"data/creators/{username}", exist_ok=True)
        
        # Initialize creator's chat history file
        with open(f"data/creators/{username}/chat_history.txt", "w") as f:
            f.write("")
        
        # Initialize creator's stats file
        pd.DataFrame({
            "total_chats": [0],
            "total_messages": [0],
            "unique_users": [0]
        }).to_csv(f"data/creators/{username}/stats.csv", index=False)
        
        # Log in the new creator
        st.session_state.logged_in = True
        st.session_state.current_creator = username
        st.switch_page("pages/dashboard.py")
        return True
    except Exception as e:
        st.error(f"Signup error: {e}")
        return False

# Main page content
st.title("👤 Digital Clone SaaS")
st.subheader("Create your own AI digital clone and share it with your audience")

# Main layout with two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🚀 What is Digital Clone?")
    st.markdown("""
    Digital Clone allows creators to:
    - Create a personalized AI chatbot clone
    - Share their clone with audience via a simple link
    - Track interactions and analyze popular questions
    - Customize responses and improve over time
    """)
    
    st.markdown("### 👨‍💻 For Creators")
    st.markdown("""
    1. Sign up for an account
    2. Set up your digital clone
    3. Share your unique link: `website.com/{your_username}`
    4. Track analytics on your dashboard
    """)

with col2:
    # Login/Signup tabs
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:  # Login tab
        st.subheader("Creator Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        login_button = st.button("Login")
        
        if login_button:
            if login_username and login_password:
                if login_creator(login_username, login_password):
                    st.success("Login successful!")
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Please enter both username and password.")
    
    with tab2:  # Signup tab
        st.subheader("Creator Sign Up")
        signup_username = st.text_input("Choose a username", key="signup_username")
        signup_name = st.text_input("Your name", key="signup_name")
        signup_password = st.text_input("Create a password", type="password", key="signup_password")
        signup_button = st.button("Sign Up")
        
        if signup_button:
            if signup_username and signup_name and signup_password:
                if signup_creator(signup_username, signup_name, signup_password):
                    st.success("Account created successfully!")
                # Error message is displayed by the signup_creator function if needed
            else:
                st.warning("Please fill in all fields.")

# Footer
st.markdown("---")
st.markdown("© 2023 Digital Clone SaaS. All rights reserved.")