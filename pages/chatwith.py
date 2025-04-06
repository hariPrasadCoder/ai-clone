import streamlit as st
import random
import time
import pandas as pd
import os
from urllib.parse import parse_qs

# Setup page configuration
st.set_page_config(
    page_title="Chat Interface",
    page_icon="💬",
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

# Function to navigate to dashboard page
def go_to_dashboard(username):
    st.session_state["current_creator"] = username
    st.switch_page("pages/creator_dashboard.py")

# Helper functions
def get_user_data(username):
    try:
        df = pd.read_csv("data/creators.csv")
        user_data = df[df["username"] == username]
        if not user_data.empty:
            return user_data.iloc[0]
        return None
    except Exception as e:
        st.error(f"Error reading user data: {e}")
        return None

def save_chat_history(username, messages):
    try:
        # Create directory if it doesn't exist
        os.makedirs("data/creators", exist_ok=True)
        os.makedirs(f"data/creators/{username}", exist_ok=True)
        
        # Save messages to a file
        with open(f"data/creators/{username}/chat_history.txt", "a") as f:
            for message in messages:
                if message["role"] == "user":
                    f.write(f"User: {message['content']}\n")
                else:
                    f.write(f"Assistant: {message['content']}\n")
            f.write("\n---\n\n")
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

def response_generator(user_name):
    response = random.choice(
        [
            f"Hello! I'm {user_name}'s AI assistant. How can I help you today?",
            f"Hi there! I'm {user_name}'s digital clone. Is there anything I can help you with?",
            f"Hey, I'm {user_name}'s AI. What can I do for you?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

# Get creator from URL query parameter
creator_username = st.query_params.get("creator", None)

# Initialize chat interface
if creator_username:
    # Store in session state for consistency
    st.session_state["current_chatbot"] = creator_username
elif "current_chatbot" in st.session_state:
    # Use existing session state if available
    creator_username = st.session_state["current_chatbot"]

# Main chat interface
if creator_username:
    user_data = get_user_data(creator_username)
    
    if user_data is not None:
        user_name = user_data["name"]
        
        # Chat Interface
        col1, col2 = st.columns([5, 1])
        with col1:
            st.title(f"Chat with {user_name}")
        with col2:
            if st.button("Home"):
                st.switch_page("main.py")
        
        # Show creator info in header instead of sidebar
        st.write(f"Creator: **{user_name}**")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": f"Hi! I'm {user_name}'s digital clone. How can I help you today?"}
            ]
        
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Accept user input
        if prompt := st.chat_input(f"Message {user_name}..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
        
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                response = st.write_stream(response_generator(user_name))
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Save chat history
            save_chat_history(creator_username, [{"role": "user", "content": prompt}, 
                                      {"role": "assistant", "content": response}])
    else:
        st.error(f"Creator '{creator_username}' not found.")
        if st.button("Back to Home"):
            st.switch_page("main.py")
else:
    # Creator selection UI
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("Chat with AI Clones")
    with col2:
        if st.button("Home"):
            st.switch_page("main.py")
    
    st.write("Choose a creator to chat with:")
    
    try:
        creators_df = pd.read_csv("data/creators.csv")
        
        # Display available creators
        for _, creator in creators_df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"### {creator['name']}")
            with col2:
                if st.button("Chat", key=f"chat_{creator['username']}"):
                    st.query_params["creator"] = creator['username']
                    st.rerun()
    except Exception as e:
        st.error(f"Error loading creators: {e}")
    
    # Add a form to directly enter a username
    with st.form("username_form"):
        input_username = st.text_input("Or enter username directly")
        submit_button = st.form_submit_button("Go to chat")
        
        if submit_button and input_username:
            st.query_params["creator"] = input_username
            st.rerun()
    
    if st.button("Back to Home"):
        st.switch_page("main.py") 