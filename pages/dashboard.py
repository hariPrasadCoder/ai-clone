import streamlit as st
import pandas as pd
import os
import uuid
from collections import Counter
import datetime
import json
import matplotlib.pyplot as plt
import numpy as np

# Setup page configuration
st.set_page_config(
    page_title="Creator Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"  # This collapses the sidebar by default
)

# Add custom CSS to hide the sidebar completely and apply custom styling
st.markdown(
    """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
        
        /* Theme Variables */
        :root {
            --primary-color: #9c27b0;
            --primary-color-light: #bb86fc;
            --secondary-color: #ffc107;
            --secondary-color-light: #ffe082;
            --text-color: #f8f9fa;
            --bg-color: #121212;
            --card-bg-color: #1e1e1e;
            --hover-color: #6a0dad;
        }
        
        /* Modern styling */
        .stApp {
            background-color: var(--bg-color);
            color: var(--text-color);
        }
        
        /* Header styling */
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-color-light) !important;
            font-weight: 600 !important;
        }
        
        /* Button styling */
        .stButton button {
            background-color: var(--primary-color) !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton button:hover {
            background-color: var(--hover-color) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        }
        
        /* Card styling for metrics */
        [data-testid="stMetric"] {
            background-color: var(--card-bg-color);
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            border-left: 4px solid var(--primary-color);
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--primary-color-light) !important;
        }
        
        [data-testid="stMetricValue"] {
            color: var(--text-color) !important;
            font-weight: bold !important;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: var(--card-bg-color);
            border-radius: 6px 6px 0px 0px;
            border: none;
            color: var(--text-color);
            padding: 10px 16px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--primary-color) !important;
            color: white !important;
        }
        
        /* Form styling */
        [data-testid="stForm"] {
            background-color: var(--card-bg-color);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Input styling */
        .stTextInput input, .stTextArea textarea, .stSelectbox, [data-baseweb="select"] {
            background-color: #2d2d2d !important;
            color: var(--text-color) !important;
            border: 1px solid #444 !important;
            border-radius: 6px !important;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 1px var(--primary-color) !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: var(--card-bg-color);
            border-radius: 8px;
            border: none !important;
            color: var(--primary-color-light) !important;
        }
        
        .streamlit-expanderContent {
            background-color: var(--card-bg-color);
            border-radius: 0 0 8px 8px;
            border: none !important;
        }
        
        /* Code block styling */
        .stCodeBlock {
            background-color: #292929 !important;
            border-radius: 8px;
            border: 1px solid #444;
        }
        
        /* Link styling */
        a {
            color: var(--secondary-color) !important;
            text-decoration: none !important;
        }
        
        a:hover {
            color: var(--secondary-color-light) !important;
            text-decoration: underline !important;
        }
        
        /* Theme toggle button - will be functional with additional JS */
        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Add theme toggle button (non-functional in pure Streamlit, but shows the UI element)
st.markdown(
    """
    <div class="theme-toggle">
        <button style="background-color: #9c27b0; color: white; border: none; border-radius: 50%; width: 40px; height: 40px; cursor: pointer;">
            <span style="font-size: 18px;">🌙</span>
        </button>
    </div>
    """,
    unsafe_allow_html=True
)

# Authentication check
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access your dashboard.")
    
    # Define the redirect function outside of the button callback
    def go_to_login():
        st.session_state.redirect_to_login = True
    
    # Create button with simple callback
    st.button("Go to Login", on_click=go_to_login)
    
    # Check if redirect flag is set and perform the page switch
    if st.session_state.get("redirect_to_login", False):
        st.switch_page("main.py")
    
    st.stop()

# Get creator info
username = st.session_state.current_creator

# Helper functions
def get_creator_data():
    try:
        df = pd.read_csv("data/creators.csv")
        creator = df[df["username"] == username]
        if not creator.empty:
            return creator.iloc[0]
        return None
    except Exception as e:
        st.error(f"Error loading creator data: {e}")
        return None

def update_creator_profile(updated_data):
    try:
        df = pd.read_csv("data/creators.csv")
        # Find the creator's row
        creator_idx = df.index[df["username"] == username].tolist()[0]
        
        # Update fields (except username which is the identifier)
        for key, value in updated_data.items():
            if key != "username":
                df.at[creator_idx, key] = value
        
        # Save back to file
        df.to_csv("data/creators.csv", index=False)
        
        # Update profile data if exists
        profile_path = f"data/creators/{username}/profile.json"
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                profile_data = json.load(f)
            
            # Update profile data
            for key, value in updated_data.items():
                profile_data[key] = value
            
            with open(profile_path, "w") as f:
                json.dump(profile_data, f, indent=4)
        else:
            # Create profile data if it doesn't exist
            os.makedirs(os.path.dirname(profile_path), exist_ok=True)
            with open(profile_path, "w") as f:
                json.dump(updated_data, f, indent=4)
                
        return True
    except Exception as e:
        st.error(f"Error updating profile: {e}")
        return False

def get_creator_profile():
    try:
        profile_path = f"data/creators/{username}/profile.json"
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                return json.load(f)
        else:
            # Create default profile
            creator_data = get_creator_data()
            profile = {
                "username": creator_data["username"],
                "name": creator_data["name"],
                "bio": "This is your digital clone's bio. Edit it to tell users about yourself.",
                "expertise": "Add your areas of expertise here",
                "contact_email": "",
                "website": "",
                "social_links": {
                    "twitter": "",
                    "linkedin": "",
                    "instagram": ""
                },
                "join_date": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(profile_path), exist_ok=True)
            
            # Save default profile
            with open(profile_path, "w") as f:
                json.dump(profile, f, indent=4)
                
            return profile
    except Exception as e:
        st.error(f"Error loading profile: {e}")
        return None

def get_stats():
    try:
        stats_path = f"data/creators/{username}/stats.csv"
        if os.path.exists(stats_path):
            return pd.read_csv(stats_path)
        else:
            # Initialize stats if doesn't exist
            stats = pd.DataFrame({
                "total_chats": [0],
                "total_messages": [0],
                "unique_users": [0]
            })
            stats.to_csv(stats_path, index=False)
            return stats
    except Exception as e:
        st.error(f"Error loading stats: {e}")
        return pd.DataFrame({
            "total_chats": [0],
            "total_messages": [0],
            "unique_users": [0]
        })

def get_usage_history():
    """Generate or retrieve usage history data."""
    try:
        usage_path = f"data/creators/{username}/usage_history.csv"
        if os.path.exists(usage_path):
            return pd.read_csv(usage_path)
        else:
            # Create some dummy data for now (in a real app, this would be real data)
            today = datetime.datetime.now()
            dates = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)]
            
            # Generate some random usage data
            np.random.seed(42)  # For reproducibility
            chats = np.random.randint(0, 5, size=30)
            messages = chats * np.random.randint(2, 8, size=30)
            unique_users = np.random.randint(0, 3, size=30)
            
            # Create dataframe
            usage_df = pd.DataFrame({
                "date": dates,
                "chats": chats,
                "messages": messages,
                "unique_users": unique_users
            })
            
            # Save to file
            os.makedirs(os.path.dirname(usage_path), exist_ok=True)
            usage_df.to_csv(usage_path, index=False)
            
            return usage_df
    except Exception as e:
        st.error(f"Error loading usage history: {e}")
        return pd.DataFrame({
            "date": [],
            "chats": [],
            "messages": [],
            "unique_users": []
        })

def get_most_asked_questions():
    try:
        history_path = f"data/creators/{username}/chat_history.txt"
        if not os.path.exists(history_path):
            return []
        
        with open(history_path, "r") as f:
            content = f.read()
        
        # Extract user questions
        questions = []
        for line in content.split("\n"):
            if line.startswith("User:"):
                questions.append(line[5:].strip())
        
        # Count questions and get top 10
        question_counts = Counter(questions)
        return question_counts.most_common(10)
    except Exception as e:
        st.error(f"Error analyzing questions: {e}")
        return []

def get_saved_faqs():
    """Get creator's saved FAQs."""
    try:
        faqs_path = f"data/creators/{username}/faqs.json"
        if os.path.exists(faqs_path):
            with open(faqs_path, "r") as f:
                return json.load(f)
        else:
            # Initialize with empty FAQs
            default_faqs = []
            os.makedirs(os.path.dirname(faqs_path), exist_ok=True)
            with open(faqs_path, "w") as f:
                json.dump(default_faqs, f, indent=4)
            return default_faqs
    except Exception as e:
        st.error(f"Error loading FAQs: {e}")
        return []

def save_faq(question, answer):
    """Save a new FAQ or update an existing one."""
    try:
        faqs_path = f"data/creators/{username}/faqs.json"
        if os.path.exists(faqs_path):
            with open(faqs_path, "r") as f:
                faqs = json.load(f)
        else:
            faqs = []
            os.makedirs(os.path.dirname(faqs_path), exist_ok=True)
        
        # Check if question already exists
        for faq in faqs:
            if faq["question"] == question:
                faq["answer"] = answer
                break
        else:
            # Question doesn't exist, add it
            faqs.append({
                "id": str(uuid.uuid4()),
                "question": question,
                "answer": answer,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Save to file
        with open(faqs_path, "w") as f:
            json.dump(faqs, f, indent=4)
        
        return True
    except Exception as e:
        st.error(f"Error saving FAQ: {e}")
        return False

def delete_faq(faq_id):
    """Delete a FAQ by ID."""
    try:
        faqs_path = f"data/creators/{username}/faqs.json"
        if os.path.exists(faqs_path):
            with open(faqs_path, "r") as f:
                faqs = json.load(f)
            
            # Filter out the FAQ with the given ID
            faqs = [faq for faq in faqs if faq["id"] != faq_id]
            
            # Save back to file
            with open(faqs_path, "w") as f:
                json.dump(faqs, f, indent=4)
            
            return True
    except Exception as e:
        st.error(f"Error deleting FAQ: {e}")
        return False

def generate_clone_link():
    # Get the current server URL, defaulting to localhost if not available
    server_url = "http://localhost:8501"
    if "server" in st.query_params:
        server_url = st.query_params["server"]
    return f"{server_url}/chatwith?creator={username}"

def update_bot_settings(settings):
    try:
        settings_path = f"data/creators/{username}/bot_settings.csv"
        settings_df = pd.DataFrame([settings])
        settings_df.to_csv(settings_path, index=False)
        st.success("Bot settings updated successfully!")
    except Exception as e:
        st.error(f"Error updating bot settings: {e}")

def get_bot_settings():
    try:
        settings_path = f"data/creators/{username}/bot_settings.csv"
        if os.path.exists(settings_path):
            return pd.read_csv(settings_path).iloc[0].to_dict()
        else:
            # Default settings
            default_settings = {
                "bot_name": f"{get_creator_data()['name']}'s Clone",
                "greeting_message": f"Hi! I'm {get_creator_data()['name']}'s digital clone. How can I help you today?",
                "theme_color": "#1E88E5",
                "avatar": "default"
            }
            # Save default settings
            pd.DataFrame([default_settings]).to_csv(settings_path, index=False)
            return default_settings
    except Exception as e:
        st.error(f"Error loading bot settings: {e}")
        return {
            "bot_name": "My Digital Clone",
            "greeting_message": "Hi! How can I help you today?",
            "theme_color": "#1E88E5",
            "avatar": "default"
        }

# Get creator's data
creator_data = get_creator_data()
if creator_data is None:
    st.error("Creator data not found. Please try logging in again.")
    st.button("Back to Login", on_click=lambda: st.switch_page("main.py"))
    st.stop()

# Page layout
col_main, col_logout = st.columns([5, 1])
with col_main:
    st.title(f"Dashboard: {creator_data['name']}")
with col_logout:
    if st.button("Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.current_creator = None
        st.switch_page("main.py")

# Create a modern dashboard header with cards
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2 style="margin: 0; color: var(--primary-color-light);">Welcome back, {}</h2>
        <div style="background-color: var(--card-bg-color); padding: 8px 16px; border-radius: 20px; display: inline-block;">
            <span style="color: var(--secondary-color);">●</span> Online
        </div>
    </div>
""".format(creator_data['name']), unsafe_allow_html=True)

# Top bar with key metrics
stats = get_stats()
st.markdown("<h3 style='color: var(--text-color); margin-bottom: 20px;'>Key Metrics</h3>", unsafe_allow_html=True)

# Custom styled metric cards
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
        <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-top: 4px solid var(--primary-color);">
            <h4 style="color: var(--text-color); margin: 0;">Total Chats</h4>
            <p style="font-size: 32px; font-weight: bold; color: var(--primary-color-light); margin: 10px 0;">{stats["total_chats"][0]}</p>
            <p style="color: var(--text-color); opacity: 0.7; margin: 0;">All-time conversations</p>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-top: 4px solid var(--secondary-color);">
            <h4 style="color: var(--text-color); margin: 0;">Total Messages</h4>
            <p style="font-size: 32px; font-weight: bold; color: var(--secondary-color); margin: 10px 0;">{stats["total_messages"][0]}</p>
            <p style="color: var(--text-color); opacity: 0.7; margin: 0;">Messages exchanged</p>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-top: 4px solid var(--primary-color-light);">
            <h4 style="color: var(--text-color); margin: 0;">Unique Users</h4>
            <p style="font-size: 32px; font-weight: bold; color: white; margin: 10px 0;">{stats["unique_users"][0]}</p>
            <p style="color: var(--text-color); opacity: 0.7; margin: 0;">Distinct visitors</p>
        </div>
    """, unsafe_allow_html=True)

# Clone link - Redesigned as a special card
st.markdown("""
    <div style="background: linear-gradient(135deg, var(--primary-color), var(--hover-color)); border-radius: 15px; padding: 25px; margin: 20px 0; box-shadow: 0 8px 15px rgba(0,0,0,0.3);">
        <h3 style="color: white; margin-top: 0;">Your Digital Clone Link</h3>
        <p style="color: rgba(255,255,255,0.8); margin-bottom: 15px;">Share this unique link with your audience so they can chat with your digital clone.</p>
    </div>
""", unsafe_allow_html=True)

clone_link = generate_clone_link()
st.code(clone_link, language=None)

# Display QR code placeholder (in a real app, you'd generate a real QR code)
col1, col2 = st.columns([3, 1])
with col1:
    st.info("Share this link on your social media or website to connect with your audience through your digital clone.")
with col2:
    st.markdown("""
        <div style="background-color: white; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; border-radius: 10px; margin: 0 auto;">
            <span style="color: black; font-size: 10px; text-align: center;">QR Code Placeholder</span>
        </div>
    """, unsafe_allow_html=True)

# Main dashboard tabs - Updated to include new sections
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Profile", "Edit Profile", "Analytics", "Usage Summary", "Bot Settings", "FAQ Builder"
])

with tab1:  # Profile Summary tab
    st.markdown("<h2 style='text-align: center; color: var(--primary-color-light); margin-bottom: 30px;'>Profile Summary</h2>", unsafe_allow_html=True)
    
    profile = get_creator_profile()
    if profile:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Avatar with custom styling
            st.markdown("""
                <div style="background-color: var(--card-bg-color); border-radius: 50%; width: 150px; height: 150px; overflow: hidden; margin: 0 auto; border: 4px solid var(--primary-color); box-shadow: 0 8px 16px rgba(0,0,0,0.3);">
                    <img src="https://via.placeholder.com/150" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <h3 style="text-align: center; margin-top: 15px; color: var(--text-color);">{}</h3>
            """.format(profile["name"]), unsafe_allow_html=True)
        
        with col2:
            # Profile info card
            st.markdown("""
                <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); height: 100%;">
                    <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <span style="background-color: var(--primary-color); color: white; border-radius: 20px; padding: 5px 10px; font-size: 14px; margin-right: 10px;">@{}</span>
                        <span style="background-color: #2d2d2d; color: var(--text-color); border-radius: 20px; padding: 5px 10px; font-size: 14px;">Joined: {}</span>
                    </div>
                    
                    <h4 style="color: var(--primary-color-light); border-bottom: 1px solid #444; padding-bottom: 8px; margin-bottom: 15px;">Bio</h4>
                    <p style="color: var(--text-color); margin-bottom: 20px;">{}</p>
                    
                    <h4 style="color: var(--primary-color-light); border-bottom: 1px solid #444; padding-bottom: 8px; margin-bottom: 15px;">Expertise</h4>
                    <p style="color: var(--text-color); margin-bottom: 20px;">{}</p>
                </div>
            """.format(
                profile['username'],
                profile.get('join_date', 'N/A'),
                profile.get("bio", "No bio yet."),
                profile.get("expertise", "No expertise listed.")
            ), unsafe_allow_html=True)
            
            # Contact & Links
            if any([profile.get("contact_email"), profile.get("website"), 
                   any(profile.get("social_links", {}).values())]):
                st.markdown("""
                    <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-top: 20px;">
                        <h4 style="color: var(--primary-color-light); margin-top: 0; border-bottom: 1px solid #444; padding-bottom: 8px; margin-bottom: 15px;">Contact & Links</h4>
                        <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                """, unsafe_allow_html=True)
                
                links_html = ""
                
                if profile.get("contact_email"):
                    links_html += f"""
                        <a href="mailto:{profile['contact_email']}" style="background-color: #2d2d2d; color: var(--text-color); text-decoration: none; border-radius: 20px; padding: 8px 15px; display: inline-flex; align-items: center;">
                            <span style="margin-right: 8px;">✉️</span> Email
                        </a>
                    """
                
                if profile.get("website"):
                    links_html += f"""
                        <a href="{profile['website']}" target="_blank" style="background-color: #2d2d2d; color: var(--text-color); text-decoration: none; border-radius: 20px; padding: 8px 15px; display: inline-flex; align-items: center;">
                            <span style="margin-right: 8px;">🌐</span> Website
                        </a>
                    """
                
                for platform, link in profile.get("social_links", {}).items():
                    if link:
                        icon = "📱"
                        if platform.lower() == "twitter":
                            icon = "🐦"
                        elif platform.lower() == "linkedin":
                            icon = "💼"
                        elif platform.lower() == "instagram":
                            icon = "📸"
                        elif platform.lower() == "github":
                            icon = "💻"
                            
                        links_html += f"""
                            <a href="{link}" target="_blank" style="background-color: #2d2d2d; color: var(--text-color); text-decoration: none; border-radius: 20px; padding: 8px 15px; display: inline-flex; align-items: center;">
                                <span style="margin-right: 8px;">{icon}</span> {platform.capitalize()}
                            </a>
                        """
                
                st.markdown(links_html + "</div></div>", unsafe_allow_html=True)

with tab2:  # Edit Profile tab
    st.markdown("<h2 style='text-align: center; color: var(--primary-color-light); margin-bottom: 30px;'>Edit Profile</h2>", unsafe_allow_html=True)
    
    profile = get_creator_profile()
    if profile:
        # Custom form styling
        st.markdown("""
            <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 25px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-bottom: 20px;">
                <h3 style="color: var(--primary-color-light); margin-top: 0; margin-bottom: 20px;">Personal Information</h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("edit_profile_form"):
            st.markdown("<h4 style='color: var(--text-color);'>Basic Details</h4>", unsafe_allow_html=True)
            name = st.text_input("Name", value=profile.get("name", ""))
            bio = st.text_area("Bio", value=profile.get("bio", ""), height=100,
                              help="Describe yourself and your digital clone's purpose")
            expertise = st.text_area("Areas of Expertise", value=profile.get("expertise", ""), height=100,
                                    help="List your specialties and knowledge areas")
            
            st.markdown("<h4 style='color: var(--text-color); margin-top: 20px;'>Contact Information</h4>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                contact_email = st.text_input("Contact Email", value=profile.get("contact_email", ""))
            with col2:
                website = st.text_input("Website", value=profile.get("website", ""))
            
            # Social links with custom styling
            st.markdown("<h4 style='color: var(--text-color); margin-top: 20px;'>Social Links</h4>", unsafe_allow_html=True)
            social_links = profile.get("social_links", {})
            
            col1, col2 = st.columns(2)
            with col1:
                twitter = st.text_input("Twitter", value=social_links.get("twitter", ""), 
                                      help="Your Twitter profile URL")
                instagram = st.text_input("Instagram", value=social_links.get("instagram", ""),
                                        help="Your Instagram profile URL")
            with col2:
                linkedin = st.text_input("LinkedIn", value=social_links.get("linkedin", ""),
                                       help="Your LinkedIn profile URL")
                github = st.text_input("GitHub", value=social_links.get("github", ""),
                                     help="Your GitHub profile URL")
            
            st.markdown("<div style='text-align: center; margin-top: 30px;'>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Save Profile")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submitted:
                updated_profile = {
                    "username": profile["username"],
                    "name": name,
                    "bio": bio,
                    "expertise": expertise,
                    "contact_email": contact_email,
                    "website": website,
                    "social_links": {
                        "twitter": twitter,
                        "linkedin": linkedin,
                        "instagram": instagram,
                        "github": github
                    },
                    "join_date": profile.get("join_date", datetime.datetime.now().strftime("%Y-%m-%d"))
                }
                
                if update_creator_profile(updated_profile):
                    st.success("Profile updated successfully!")
                    # Also update the creator's name in creators.csv
                    update_data = {"name": name}
                    update_creator_profile(update_data)

with tab3:  # Analytics tab
    st.markdown("<h2 style='text-align: center; color: var(--primary-color-light); margin-bottom: 30px;'>Analytics Dashboard</h2>", unsafe_allow_html=True)
    
    # User engagement metrics intro
    st.markdown("""
        <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-bottom: 30px;">
            <h3 style="color: var(--primary-color-light); margin-top: 0;">User Engagement</h3>
            <p style="color: var(--text-color); margin-bottom: 0;">Track how users are interacting with your digital clone over time.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Usage stats
    usage_data = get_usage_history()
    if not usage_data.empty:
        # Convert date to datetime for plotting
        usage_data["date"] = pd.to_datetime(usage_data["date"])
        
        # Customize matplotlib style for dark theme
        plt.style.use('dark_background')
        
        # Create tabs for different metrics
        metric_tab1, metric_tab2, metric_tab3 = st.tabs(["Chats", "Messages", "Unique Users"])
        
        with metric_tab1:
            # Custom card with chart
            st.markdown("""
                <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                    <h3 style="color: var(--primary-color-light); margin-top: 0; margin-bottom: 20px;">Daily Chats</h3>
                </div>
            """, unsafe_allow_html=True)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            # Use gradient color for line
            ax.plot(usage_data["date"], usage_data["chats"], marker='o', linestyle='-', color='#9c27b0')
            
            # Fill area under the line with gradient
            ax.fill_between(usage_data["date"], usage_data["chats"], alpha=0.3, color='#9c27b0')
            
            # Customize grid and background
            ax.set_facecolor('#1e1e1e')
            fig.patch.set_facecolor('#1e1e1e')
            ax.grid(True, linestyle='--', alpha=0.3, color='#555555')
            
            # Add title and labels with custom styling
            ax.set_title("Daily Conversation Activity", color='white', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel("Date", color='white', fontsize=12, labelpad=10)
            ax.set_ylabel("Number of Chats", color='white', fontsize=12, labelpad=10)
            
            # Style the tick labels
            ax.tick_params(colors='white', which='both')
            
            # Rotate date labels for better readability
            fig.autofmt_xdate()
            
            # Add some padding
            plt.tight_layout(pad=3)
            
            st.pyplot(fig)
            
            # Add insights card
            total_chats = usage_data["chats"].sum()
            avg_chats = usage_data["chats"].mean()
            max_chats = usage_data["chats"].max()
            max_date = usage_data.loc[usage_data["chats"].idxmax(), "date"].strftime("%Y-%m-%d")
            
            st.markdown(f"""
                <div style="display: flex; gap: 20px; margin-top: 20px;">
                    <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 15px; flex: 1; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-left: 4px solid var(--primary-color);">
                        <p style="color: var(--text-color); margin: 0; font-size: 14px;">Total Chats</p>
                        <h3 style="color: var(--primary-color-light); margin: 5px 0;">{total_chats}</h3>
                    </div>
                    <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 15px; flex: 1; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-left: 4px solid var(--primary-color);">
                        <p style="color: var(--text-color); margin: 0; font-size: 14px;">Average Daily</p>
                        <h3 style="color: var(--primary-color-light); margin: 5px 0;">{avg_chats:.1f}</h3>
                    </div>
                    <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 15px; flex: 1; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-left: 4px solid var(--primary-color);">
                        <p style="color: var(--text-color); margin: 0; font-size: 14px;">Peak Day</p>
                        <h3 style="color: var(--primary-color-light); margin: 5px 0;">{max_chats} ({max_date})</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with metric_tab2:
            # Messages chart with similar styling
            st.markdown("""
                <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                    <h3 style="color: var(--secondary-color); margin-top: 0; margin-bottom: 20px;">Daily Messages</h3>
                </div>
            """, unsafe_allow_html=True)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(usage_data["date"], usage_data["messages"], marker='o', linestyle='-', color='#ffc107')
            ax.fill_between(usage_data["date"], usage_data["messages"], alpha=0.3, color='#ffc107')
            
            ax.set_facecolor('#1e1e1e')
            fig.patch.set_facecolor('#1e1e1e')
            ax.grid(True, linestyle='--', alpha=0.3, color='#555555')
            
            ax.set_title("Daily Message Activity", color='white', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel("Date", color='white', fontsize=12, labelpad=10)
            ax.set_ylabel("Number of Messages", color='white', fontsize=12, labelpad=10)
            
            ax.tick_params(colors='white', which='both')
            fig.autofmt_xdate()
            plt.tight_layout(pad=3)
            
            st.pyplot(fig)
            
            # Add insights for messages
            total_msgs = usage_data["messages"].sum()
            avg_msgs = usage_data["messages"].mean()
            avg_msgs_per_chat = total_msgs / usage_data["chats"].sum() if usage_data["chats"].sum() > 0 else 0
            
            st.markdown(f"""
                <div style="display: flex; gap: 20px; margin-top: 20px;">
                    <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 15px; flex: 1; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-left: 4px solid var(--secondary-color);">
                        <p style="color: var(--text-color); margin: 0; font-size: 14px;">Total Messages</p>
                        <h3 style="color: var(--secondary-color); margin: 5px 0;">{total_msgs}</h3>
                    </div>
                    <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 15px; flex: 1; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-left: 4px solid var(--secondary-color);">
                        <p style="color: var(--text-color); margin: 0; font-size: 14px;">Average Daily</p>
                        <h3 style="color: var(--secondary-color); margin: 5px 0;">{avg_msgs:.1f}</h3>
                    </div>
                    <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 15px; flex: 1; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-left: 4px solid var(--secondary-color);">
                        <p style="color: var(--text-color); margin: 0; font-size: 14px;">Avg Messages/Chat</p>
                        <h3 style="color: var(--secondary-color); margin: 5px 0;">{avg_msgs_per_chat:.1f}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with metric_tab3:
            # Unique users visualization
            st.markdown("""
                <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                    <h3 style="color: var(--primary-color-light); margin-top: 0; margin-bottom: 20px;">Daily Unique Users</h3>
                </div>
            """, unsafe_allow_html=True)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Create bar chart for unique users
            bars = ax.bar(usage_data["date"], usage_data["unique_users"], color='#bb86fc', alpha=0.8, width=0.8)
            
            # Add a trend line
            ax.plot(usage_data["date"], usage_data["unique_users"].rolling(window=7).mean(), 
                   color='white', linestyle='--', linewidth=2, label='7-day Average')
            
            ax.set_facecolor('#1e1e1e')
            fig.patch.set_facecolor('#1e1e1e')
            ax.grid(True, linestyle='--', alpha=0.3, color='#555555', axis='y')
            
            ax.set_title("Daily Unique Users", color='white', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel("Date", color='white', fontsize=12, labelpad=10)
            ax.set_ylabel("Number of Unique Users", color='white', fontsize=12, labelpad=10)
            
            ax.tick_params(colors='white', which='both')
            ax.legend(facecolor='#2d2d2d', edgecolor='#2d2d2d', labelcolor='white')
            
            fig.autofmt_xdate()
            plt.tight_layout(pad=3)
            
            st.pyplot(fig)
            
            # User growth analysis
            total_users = usage_data["unique_users"].sum()
            retention_rate = 0.68  # Placeholder for actual retention calculation
            
            st.markdown(f"""
                <div style="display: flex; gap: 20px; margin-top: 20px;">
                    <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 15px; flex: 1; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-left: 4px solid #bb86fc;">
                        <p style="color: var(--text-color); margin: 0; font-size: 14px;">Total Unique Users</p>
                        <h3 style="color: #bb86fc; margin: 5px 0;">{total_users}</h3>
                    </div>
                    <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 15px; flex: 1; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-left: 4px solid #bb86fc;">
                        <p style="color: var(--text-color); margin: 0; font-size: 14px;">New Users (Last 7 Days)</p>
                        <h3 style="color: #bb86fc; margin: 5px 0;">{usage_data.tail(7)["unique_users"].sum()}</h3>
                    </div>
                    <div style="background-color: var(--card-bg-color); border-radius: 10px; padding: 15px; flex: 1; box-shadow: 0 4px 8px rgba(0,0,0,0.2); border-left: 4px solid #bb86fc;">
                        <p style="color: var(--text-color); margin: 0; font-size: 14px;">Estimated Retention</p>
                        <h3 style="color: #bb86fc; margin: 5px 0;">{retention_rate:.0%}</h3>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    # Most asked questions
    st.markdown("""
        <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-top: 40px; margin-bottom: 30px;">
            <h3 style="color: var(--primary-color-light); margin-top: 0;">Most Asked Questions</h3>
            <p style="color: var(--text-color); margin-bottom: 0;">See what your audience is most curious about.</p>
        </div>
    """, unsafe_allow_html=True)
    
    most_asked = get_most_asked_questions()
    
    if most_asked:
        # Create a DataFrame for the questions
        questions_df = pd.DataFrame(most_asked, columns=["Question", "Count"])
        
        # Style the plot for dark theme
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#1e1e1e')
        ax.set_facecolor('#1e1e1e')
        
        # Create horizontal bar chart
        bars = ax.barh(
            questions_df["Question"].str.slice(0, 30), 
            questions_df["Count"], 
            color='#9c27b0',
            alpha=0.7,
            height=0.7
        )
        
        # Add a gradient effect to bars
        for i, bar in enumerate(bars):
            bar.set_alpha(0.6 + (i * 0.04))
        
        # Style the plot
        ax.set_title("Top Questions by Frequency", color='white', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel("Number of Times Asked", color='white', fontsize=12, labelpad=10)
        ax.tick_params(colors='white', which='both')
        ax.grid(True, linestyle='--', alpha=0.3, color='#555555', axis='x')
        
        # Add count labels to bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, f"{width:.0f}", 
                    ha='left', va='center', color='white', fontweight='bold')
        
        plt.tight_layout(pad=3)
        st.pyplot(fig)
        
        # Display interactive table of questions
        st.markdown("""
            <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-top: 30px;">
                <h3 style="color: var(--primary-color-light); margin-top: 0; margin-bottom: 20px;">Top Questions Details</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Create clickable cards for each question
        for i, (question, count) in enumerate(most_asked, 1):
            with st.expander(f"#{i}: {question}", expanded=False):
                st.markdown(f"""
                    <div style="background-color: #2d2d2d; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                        <p style="color: var(--text-color); margin: 0; font-size: 16px;">{question}</p>
                        <p style="color: #888; margin: 10px 0 0 0; font-size: 14px;">Asked {count} times</p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([3, 2, 1])
                with col3:
                    if st.button(f"Add to FAQ", key=f"add_faq_{i}"):
                        st.session_state.add_to_faq = question
                        st.rerun()
    else:
        st.info("No questions have been asked yet. Share your clone link to get started!")

with tab4:  # Usage Summary tab
    st.header("Usage Summary")
    
    # Current month stats
    st.subheader("Current Month Statistics")
    
    usage_data = get_usage_history()
    if not usage_data.empty:
        # Get the current month data
        current_month = datetime.datetime.now().strftime("%Y-%m")
        month_data = usage_data[pd.to_datetime(usage_data["date"]).dt.strftime("%Y-%m") == current_month]
        
        if not month_data.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_chats = month_data["chats"].sum()
                st.metric("Total Chats", total_chats)
            
            with col2:
                total_messages = month_data["messages"].sum()
                st.metric("Total Messages", total_messages)
            
            with col3:
                total_users = month_data["unique_users"].sum()
                st.metric("Total Users Served", total_users)
            
            # Weekly trends
            st.subheader("Weekly Trends")
            
            # Group by week
            usage_data["week"] = pd.to_datetime(usage_data["date"]).dt.isocalendar().week
            weekly_data = usage_data.groupby("week").sum().reset_index()
            
            # Plot weekly data
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(weekly_data["week"], weekly_data["chats"], marker='o', label='Chats')
            ax.plot(weekly_data["week"], weekly_data["messages"], marker='s', label='Messages')
            ax.plot(weekly_data["week"], weekly_data["unique_users"], marker='^', label='Users')
            
            ax.set_title("Weekly Usage Trends")
            ax.set_xlabel("Week of Year")
            ax.set_ylabel("Count")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.7)
            
            st.pyplot(fig)
            
            # Hours of operation
            st.subheader("Hours of Operation")
            st.info("This feature will show the most active hours for your clone based on user interactions. Data is not yet available.")
            
            # User retention
            st.subheader("User Retention")
            st.info("This feature will show how many users return to chat with your clone. Data is not yet available.")
        else:
            st.info("No data available for the current month.")
    else:
        st.info("No usage data available yet.")

with tab5:  # Bot Settings tab
    st.markdown("<h2 style='text-align: center; color: var(--primary-color-light); margin-bottom: 30px;'>Bot Configuration</h2>", unsafe_allow_html=True)
    
    # Get current settings
    current_settings = get_bot_settings()
    
    # Show preview of bot appearance
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
            <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-bottom: 30px;">
                <h3 style="color: var(--primary-color-light); margin-top: 0; margin-bottom: 20px;">Bot Settings</h3>
                <p style="color: var(--text-color); margin-bottom: 0;">Customize how your digital clone appears and interacts with users.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Bot configuration form with improved styling
        with st.form("bot_settings_form"):
            st.markdown("<h4 style='color: var(--text-color);'>Basic Settings</h4>", unsafe_allow_html=True)
            
            bot_name = st.text_input("Bot Name", value=current_settings["bot_name"])
            greeting_message = st.text_area("Greeting Message", value=current_settings["greeting_message"],
                                         help="This message is shown when a user first interacts with your clone")
            
            st.markdown("<h4 style='color: var(--text-color); margin-top: 20px;'>Appearance</h4>", unsafe_allow_html=True)
            
            # Color picker with custom styling
            st.markdown("""
                <p style="color: var(--text-color); margin-bottom: 8px;">Theme Color</p>
                <p style="color: #888; font-size: 12px; margin-top: 0;">Choose a primary color for your bot's interface</p>
            """, unsafe_allow_html=True)
            theme_color = st.color_picker("", value=current_settings["theme_color"])
            
            # Avatar selection with visual options
            st.markdown("""
                <p style="color: var(--text-color); margin-bottom: 8px; margin-top: 20px;">Avatar Style</p>
                <p style="color: #888; font-size: 12px; margin-top: 0;">Choose how your digital clone will be represented</p>
            """, unsafe_allow_html=True)
            
            # Visual avatar selection
            avatar_options = ["default", "robot", "assistant", "person"]
            avatar_cols = st.columns(4)
            
            # Display avatar options
            with avatar_cols[0]:
                st.markdown("""
                    <div style="background-color: #2d2d2d; border-radius: 10px; padding: 10px; text-align: center;">
                        <div style="width: 50px; height: 50px; background-color: #9c27b0; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; color: white; font-weight: bold;">DC</div>
                        <p style="margin-top: 10px; color: var(--text-color); font-size: 12px;">Default</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with avatar_cols[1]:
                st.markdown("""
                    <div style="background-color: #2d2d2d; border-radius: 10px; padding: 10px; text-align: center;">
                        <div style="width: 50px; height: 50px; background-color: #2d2d2d; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-size: 24px;">🤖</div>
                        <p style="margin-top: 10px; color: var(--text-color); font-size: 12px;">Robot</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with avatar_cols[2]:
                st.markdown("""
                    <div style="background-color: #2d2d2d; border-radius: 10px; padding: 10px; text-align: center;">
                        <div style="width: 50px; height: 50px; background-color: #2d2d2d; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-size: 24px;">👨‍💼</div>
                        <p style="margin-top: 10px; color: var(--text-color); font-size: 12px;">Assistant</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with avatar_cols[3]:
                st.markdown("""
                    <div style="background-color: #2d2d2d; border-radius: 10px; padding: 10px; text-align: center;">
                        <div style="width: 50px; height: 50px; background-color: #2d2d2d; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-size: 24px;">👤</div>
                        <p style="margin-top: 10px; color: var(--text-color); font-size: 12px;">Person</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Standard dropdown for actual selection
            avatar = st.selectbox("Select Avatar", avatar_options, index=avatar_options.index(current_settings["avatar"]),
                               label_visibility="collapsed")
            
            # Advanced settings section
            st.markdown("<h4 style='color: var(--text-color); margin-top: 30px;'>Advanced Settings</h4>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                # Placeholder for response speed setting
                response_speed = st.slider("Response Speed", min_value=1, max_value=10, value=5,
                                        help="Control how quickly your bot responds (1=slow, 10=fast)")
            
            with col2:
                # Placeholder for personality setting
                personality = st.select_slider("Personality", options=["Formal", "Balanced", "Casual"], value="Balanced",
                                            help="Set the tone of your bot's responses")
            
            # Save button with custom styling
            st.markdown("<div style='text-align: center; margin-top: 30px;'>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Save Settings")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submitted:
                new_settings = {
                    "bot_name": bot_name,
                    "greeting_message": greeting_message,
                    "theme_color": theme_color,
                    "avatar": avatar,
                    "response_speed": response_speed,  # New setting
                    "personality": personality  # New setting
                }
                update_bot_settings(new_settings)
    
    with col2:
        # Preview panel
        st.markdown(f"""
            <div style="background-color: var(--card-bg-color); border-radius: 15px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); height: 100%;">
                <h3 style="color: var(--primary-color-light); margin-top: 0; margin-bottom: 20px;">Live Preview</h3>
                
                <div style="background-color: #2d2d2d; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                    <div style="display: flex; align-items: center; margin-bottom: 15px;">
                        <div style="width: 40px; height: 40px; background-color: {current_settings['theme_color']}; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; color: white; font-weight: bold;">
                            {current_settings['bot_name'][0]}
                        </div>
                        <div>
                            <p style="margin: 0; color: white; font-weight: bold;">{current_settings['bot_name']}</p>
                            <p style="margin: 0; color: #888; font-size: 12px;">Digital Clone</p>
                        </div>
                    </div>
                    
                    <div style="background-color: #383838; border-radius: 15px; padding: 12px; margin-left: 50px; position: relative;">
                        <div style="position: absolute; left: -8px; top: 10px; width: 0; height: 0; border-top: 8px solid transparent; border-bottom: 8px solid transparent; border-right: 8px solid #383838;"></div>
                        <p style="margin: 0; color: var(--text-color);">{current_settings['greeting_message']}</p>
                    </div>
                </div>
                
                <div style="margin-top: 30px;">
                    <h4 style="color: var(--text-color); margin-bottom: 15px;">Chat Interface</h4>
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <div style="height: 10px; width: 40px; background-color: {current_settings['theme_color']}; border-radius: 5px;"></div>
                        <div style="height: 10px; width: 60px; background-color: #444; border-radius: 5px;"></div>
                        <div style="height: 10px; width: 30px; background-color: #444; border-radius: 5px;"></div>
                    </div>
                    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                        <div style="height: 10px; width: 50px; background-color: #444; border-radius: 5px;"></div>
                        <div style="height: 10px; width: 70px; background-color: {current_settings['theme_color']}; border-radius: 5px;"></div>
                        <div style="height: 10px; width: 40px; background-color: #444; border-radius: 5px;"></div>
                    </div>
                    
                    <div style="background-color: #222; border-radius: 20px; padding: 10px 15px; display: flex; align-items: center; margin-top: 30px;">
                        <input type="text" placeholder="Type a message..." style="background: none; border: none; color: white; width: 100%; outline: none;">
                        <span style="background-color: {current_settings['theme_color']}; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer;">➤</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with tab6:  # FAQ Builder tab
    st.header("FAQ Builder")
    
    # Handle adding FAQ from Analytics tab
    if "add_to_faq" in st.session_state:
        question = st.session_state.add_to_faq
        st.info(f"Adding question to FAQ: {question}")
        
        # Form to add the answer
        with st.form("add_faq_form"):
            st.write(f"**Question:** {question}")
            answer = st.text_area("Answer", height=100)
            
            submitted = st.form_submit_button("Save FAQ")
            
            if submitted and answer:
                if save_faq(question, answer):
                    st.success("FAQ added successfully!")
                    # Clear the session state
                    del st.session_state.add_to_faq
                    st.rerun()
    
    # Main FAQ management section
    st.subheader("Manage FAQs")
    
    # Create new FAQ
    with st.expander("Create New FAQ", expanded=False):
        with st.form("create_faq_form"):
            new_question = st.text_input("Question")
            new_answer = st.text_area("Answer", height=100)
            
            submitted = st.form_submit_button("Create FAQ")
            
            if submitted and new_question and new_answer:
                if save_faq(new_question, new_answer):
                    st.success("FAQ created successfully!")
                    st.rerun()
    
    # List existing FAQs
    faqs = get_saved_faqs()
    
    if faqs:
        for i, faq in enumerate(faqs):
            with st.expander(f"FAQ: {faq['question']}", expanded=False):
                st.write(f"**Question:** {faq['question']}")
                st.write(f"**Answer:** {faq['answer']}")
                st.write(f"**Created:** {faq.get('created_at', 'N/A')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Edit", key=f"edit_{i}"):
                        st.session_state.edit_faq = faq
                        st.rerun()
                with col2:
                    if st.button("Delete", key=f"delete_{i}"):
                        if delete_faq(faq["id"]):
                            st.success("FAQ deleted successfully!")
                            st.rerun()
        
        # Edit FAQ form
        if "edit_faq" in st.session_state:
            faq = st.session_state.edit_faq
            st.subheader("Edit FAQ")
            
            with st.form("edit_faq_form"):
                edit_question = st.text_input("Question", value=faq["question"])
                edit_answer = st.text_area("Answer", value=faq["answer"], height=100)
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Save Changes")
                with col2:
                    cancel = st.form_submit_button("Cancel")
                
                if submitted and edit_question and edit_answer:
                    if save_faq(edit_question, edit_answer):
                        st.success("FAQ updated successfully!")
                        del st.session_state.edit_faq
                        st.rerun()
                
                if cancel:
                    del st.session_state.edit_faq
                    st.rerun()
    else:
        st.info("No FAQs created yet. Use the form above to create your first FAQ.")
        
        # Sample FAQs
        st.write("### Sample FAQs to Get Started")
        sample_faqs = [
            {
                "question": "What services do you offer?",
                "answer": "Add your answer here..."
            },
            {
                "question": "How can someone contact you?",
                "answer": "Add your answer here..."
            },
            {
                "question": "What is your background and expertise?",
                "answer": "Add your answer here..."
            }
        ]
        
        for i, faq in enumerate(sample_faqs):
            if st.button(f"Use this sample", key=f"sample_{i}"):
                if save_faq(faq["question"], faq["answer"]):
                    st.success("Sample FAQ added successfully! Edit it to add your custom answer.")
                    st.rerun()
            st.write(f"**{faq['question']}**")
            st.write("---") 