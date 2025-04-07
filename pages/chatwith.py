import streamlit as st
import random
import time
import pandas as pd
import os
from urllib.parse import parse_qs
import boto3
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, SystemMessage
import json
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()
pinecone_api = os.getenv("PINECONE_API")

session = boto3.Session(profile_name="personal", region_name="us-east-1")
bedrock = boto3.client("bedrock-runtime")
pc = Pinecone(api_key=pinecone_api)
index_name = "document-store"
pinecone_index = pc.Index(index_name)

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

def llama2_model():
    llm = Bedrock(
        model_id="meta.llama3-70b-instruct-v1:0",
        model_kwargs={'max_gen_len': 512}
    )
    return llm

# def call_langchain_with_chat_memory(chat_history, user_input):
#     # Initialize LLM and memory
#     llm = llama2_model()
#     memory = ConversationBufferMemory(return_messages=True)
    
#     # Load previous chat history
#     for message in chat_history:
#         if message["role"] == "user":
#             memory.chat_memory.add_user_message(message["content"])
#         elif message["role"] == "assistant":
#             memory.chat_memory.add_ai_message(message["content"])
    
#     # Create conversation chain
#     conversation = ConversationChain(
#         llm=llm,
#         memory=memory,
#         verbose=False
#     )
    
#     # Generate response
#     response = conversation.predict(input=user_input)
    
#     # Stream response word by word
#     for word in response.split():
#         yield word + " "
#         time.sleep(0.05)

def call_langchain_with_chat_memory(chat_history, user_input, username):
    # 1. Generate embedding for user input
    response = bedrock.invoke_model(
        body=json.dumps({"inputText": user_input}),
        modelId="amazon.titan-embed-text-v2:0",
        contentType="application/json"
    )
    input_embedding = json.loads(response['body'].read()).get("embedding")
    
    # 2. Query Pinecone with username filter
    results = pinecone_index.query(
        vector=input_embedding,
        top_k=3,
        include_metadata=True,
        filter={
            "user_id": {"$eq": username},
            "$and": [{"source": {"$exists": True}}]
        }
    )
    
    # 3. Build context from matches
    context = "\n".join([match.metadata["text"] for match in results.matches])
    
    # 4. Initialize LLM with context-aware prompt
    llm = llama2_model()
    memory = ConversationBufferMemory(return_messages=True)
    
    # Load history with context
    memory.chat_memory.add_message(SystemMessage(content=f"Relevant context: {context}"))
    for message in chat_history:
        if message["role"] == "user":
            memory.chat_memory.add_user_message(message["content"])
        else:
            memory.chat_memory.add_ai_message(message["content"])
    
    # 5. Create conversation chain
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )
    
    # 6. Generate and stream response
    response = conversation.predict(input=user_input)
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
                response = st.write_stream(call_langchain_with_chat_memory(st.session_state.messages, prompt, creator_username))
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Save chat history
            save_chat_history(creator_username, [{"role": "user", "content": prompt}, 
                                      {"role": "assistant", "content": response}])
    else:
        st.error(f"Creator '{creator_username}' not found.")
        if st.button("Back to Home"):
            st.switch_page("main.py")