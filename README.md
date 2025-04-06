# Digital Clone SaaS

A Streamlit-based SaaS application that allows creators to build AI digital clones of themselves and share with their audience.

## Features

- **For Creators:**
  - Create a personal account with unique username
  - Configure your digital clone's appearance and behavior
  - Share a personalized link with your audience
  - View analytics on most asked questions
  - Track user engagement statistics

- **For Audience:**
  - Chat with creators' digital clones
  - Get personalized responses
  - Easy-to-use chat interface

## Project Structure

```
digital-clone-saas/
├── main.py               # Home page with login/signup
├── requirements.txt      # Dependencies
├── data/                 # Data storage
│   ├── creators.csv      # Creator account information
│   └── creators/         # Individual creator data
│       └── {username}/   # Per-creator directories
│           ├── bot_settings.csv    # Bot configuration
│           ├── chat_history.txt    # Conversation logs
│           └── stats.csv           # Usage statistics
└── pages/                # Streamlit pages
    ├── dashboard.py      # Creator dashboard
    ├── {username}.py     # Dynamically generated chatbot pages
    └── 1_create-pages.py # Setup for dynamic pages
```

## Setup & Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/digital-clone-saas.git
   cd digital-clone-saas
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run main.py
   ```

4. Access the application at:
   ```
   http://localhost:8501
   ```

## Usage

### For Creators

1. Sign up with a unique username
2. Configure your digital clone in the dashboard
3. Share your unique link: `http://yourdomain.com/{username}`
4. Monitor user interactions and analytics in your dashboard

### For Audience

1. Visit a creator's unique link: `http://yourdomain.com/{username}`
2. Chat with the creator's digital clone
3. Get personalized responses based on the creator's configuration

## Deployment

This application can be deployed on any platform that supports Streamlit:

- [Streamlit Sharing](https://streamlit.io/sharing)
- [Heroku](https://heroku.com)
- [AWS](https://aws.amazon.com)
- [Digital Ocean](https://www.digitalocean.com/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.