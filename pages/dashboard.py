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
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_creator = None
        st.switch_page("main.py")

# Top bar with key metrics
stats = get_stats()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Chats", stats["total_chats"][0])
with col2:
    st.metric("Total Messages", stats["total_messages"][0])
with col3:
    st.metric("Unique Users", stats["unique_users"][0])

# Clone link
st.subheader("Your Digital Clone Link")
clone_link = generate_clone_link()
st.code(clone_link, language=None)
st.info("Share this link with your audience so they can chat with your digital clone.")

# st.write("Your clone is also accessible through the shared chat page at:")
# shared_page_url = "http://localhost:8501/chatwith"
# if "server" in st.query_params:
#     server_url = st.query_params["server"]
#     shared_page_url = f"{server_url}/chatwith"
# st.code(shared_page_url, language=None)
# st.info("Users can select your clone from the list of available creators on this page.")

# Main dashboard tabs - Updated to include new sections
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Profile", "Edit Profile", "Analytics", "Usage Summary", "Bot Settings", "FAQ Builder"
])

with tab1:  # Profile Summary tab
    st.header("Profile Summary")
    
    profile = get_creator_profile()
    if profile:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Avatar placeholder
            st.image("https://via.placeholder.com/150", caption=profile["name"])
        
        with col2:
            st.subheader(profile["name"])
            st.write(f"**Username:** {profile['username']}")
            st.write(f"**Joined:** {profile.get('join_date', 'N/A')}")
            
            # Bio section
            st.subheader("Bio")
            st.write(profile.get("bio", "No bio yet."))
            
            # Expertise
            st.subheader("Expertise")
            st.write(profile.get("expertise", "No expertise listed."))
            
            # Contact & Links
            if any([profile.get("contact_email"), profile.get("website"), 
                   any(profile.get("social_links", {}).values())]):
                st.subheader("Contact & Links")
                
                if profile.get("contact_email"):
                    st.write(f"**Email:** {profile['contact_email']}")
                
                if profile.get("website"):
                    st.write(f"**Website:** [{profile['website']}]({profile['website']})")
                
                for platform, link in profile.get("social_links", {}).items():
                    if link:
                        st.write(f"**{platform.capitalize()}:** [{link}]({link})")

with tab2:  # Edit Profile tab
    st.header("Edit Profile")
    
    profile = get_creator_profile()
    if profile:
        with st.form("edit_profile_form"):
            name = st.text_input("Name", value=profile.get("name", ""))
            bio = st.text_area("Bio", value=profile.get("bio", ""), height=100)
            expertise = st.text_area("Areas of Expertise", value=profile.get("expertise", ""), height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                contact_email = st.text_input("Contact Email", value=profile.get("contact_email", ""))
            with col2:
                website = st.text_input("Website", value=profile.get("website", ""))
            
            # Social links
            st.subheader("Social Links")
            social_links = profile.get("social_links", {})
            
            col1, col2 = st.columns(2)
            with col1:
                twitter = st.text_input("Twitter", value=social_links.get("twitter", ""))
                instagram = st.text_input("Instagram", value=social_links.get("instagram", ""))
            with col2:
                linkedin = st.text_input("LinkedIn", value=social_links.get("linkedin", ""))
                github = st.text_input("GitHub", value=social_links.get("github", ""))
            
            submitted = st.form_submit_button("Save Profile")
            
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
    st.header("Analytics")
    
    # User engagement metrics
    st.subheader("User Engagement")
    
    # Usage stats
    usage_data = get_usage_history()
    if not usage_data.empty:
        # Convert date to datetime for plotting
        usage_data["date"] = pd.to_datetime(usage_data["date"])
        
        # Create tabs for different metrics
        metric_tab1, metric_tab2, metric_tab3 = st.tabs(["Chats", "Messages", "Unique Users"])
        
        with metric_tab1:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(usage_data["date"], usage_data["chats"], marker='o', linestyle='-', color='blue')
            ax.set_title("Daily Chats")
            ax.set_xlabel("Date")
            ax.set_ylabel("Number of Chats")
            ax.grid(True, linestyle='--', alpha=0.7)
            fig.autofmt_xdate()  # Rotate date labels
            st.pyplot(fig)
        
        with metric_tab2:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(usage_data["date"], usage_data["messages"], marker='o', linestyle='-', color='green')
            ax.set_title("Daily Messages")
            ax.set_xlabel("Date")
            ax.set_ylabel("Number of Messages")
            ax.grid(True, linestyle='--', alpha=0.7)
            fig.autofmt_xdate()
            st.pyplot(fig)
        
        with metric_tab3:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(usage_data["date"], usage_data["unique_users"], marker='o', linestyle='-', color='purple')
            ax.set_title("Daily Unique Users")
            ax.set_xlabel("Date")
            ax.set_ylabel("Number of Users")
            ax.grid(True, linestyle='--', alpha=0.7)
            fig.autofmt_xdate()
            st.pyplot(fig)
    
    # Most asked questions
    st.subheader("Most Asked Questions")
    most_asked = get_most_asked_questions()
    
    if most_asked:
        # Create a DataFrame for the questions
        questions_df = pd.DataFrame(most_asked, columns=["Question", "Count"])
        
        # Display as a bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(questions_df["Question"].str.slice(0, 30), questions_df["Count"], color='skyblue')
        ax.set_title("Top Questions")
        ax.set_xlabel("Count")
        
        # Add count labels to bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f"{width:.0f}", 
                    ha='left', va='center')
        
        st.pyplot(fig)
        
        # Also display as a table
        st.write("### Top Questions Details")
        for i, (question, count) in enumerate(most_asked, 1):
            st.write(f"{i}. **{question}** (asked {count} times)")
            
            # Add a button to convert to FAQ
            if st.button(f"Add to FAQ #{i}", key=f"add_faq_{i}"):
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
    st.header("Bot Settings")
    
    # Get current settings
    current_settings = get_bot_settings()
    
    # Bot configuration form
    with st.form("bot_settings_form"):
        bot_name = st.text_input("Bot Name", value=current_settings["bot_name"])
        greeting_message = st.text_area("Greeting Message", value=current_settings["greeting_message"])
        theme_color = st.color_picker("Theme Color", value=current_settings["theme_color"])
        
        # Avatar selection (in a real app, you would allow image upload)
        avatar_options = ["default", "robot", "assistant", "person"]
        avatar = st.selectbox("Avatar Style", avatar_options, index=avatar_options.index(current_settings["avatar"]))
        
        # Save button
        submitted = st.form_submit_button("Save Settings")
        
        if submitted:
            new_settings = {
                "bot_name": bot_name,
                "greeting_message": greeting_message,
                "theme_color": theme_color,
                "avatar": avatar
            }
            update_bot_settings(new_settings)

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