import streamlit as st
import pandas as pd
import time
from auth import authenticate, create_user_table, register_user, login_user
from recommendation import load_model, get_recommendations

# Set page configuration
st.set_page_config(
    page_title="Drug Recommendation System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_history' not in st.session_state:
    st.session_state.user_history = []

# Database setup
create_user_table()

# Load the model at app startup
model, vectorizer, all_symptoms, drug_names = load_model()

def main():
    # Show header
    st.markdown("<h1 style='text-align: center;'>Drug Recommendation System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Get medicine recommendations based on your symptoms</h3>", unsafe_allow_html=True)
    
    # Authentication section
    if not st.session_state.logged_in:
        login_section()
    else:
        recommendation_section()

def login_section():
    # Display login/register tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if login_username and login_password:
                result = login_user(login_username, login_password)
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")
    
    with tab2:
        st.subheader("Register")
        new_username = st.text_input("Username", key="new_username")
        new_password = st.text_input("Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Register", key="register_button"):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    result = register_user(new_username, new_password)
                    if result == "success":
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(result)
                else:
                    st.error("Passwords do not match")
            else:
                st.warning("Please fill in all fields")

def recommendation_section():
    # Create a sidebar for navigation
    with st.sidebar:
        st.write(f"Welcome, **{st.session_state.username}**!")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
        
        st.divider()
        st.markdown("## Navigation")
        page = st.radio("Go to", ["Get Recommendations", "My History"])
    
    if page == "Get Recommendations":
        st.header("Symptom Analysis")
        
        # Multiple select for symptoms
        user_symptoms = st.multiselect(
            "Select your symptoms:",
            options=all_symptoms,
            help="Select one or more symptoms you are experiencing"
        )
        
        severity = st.slider("Symptom Severity", 1, 10, 5, 
                             help="Rate how severe your symptoms are (1=mild, 10=severe)")
        
        duration = st.selectbox(
            "Symptom Duration",
            options=["Less than a day", "1-3 days", "3-7 days", "1-2 weeks", "More than 2 weeks"]
        )
        
        # Get recommendations
        if st.button("Get Recommendations"):
            if user_symptoms:
                with st.spinner('Analyzing symptoms and finding recommendations...'):
                    # Get recommendations
                    recommendations = get_recommendations(user_symptoms, vectorizer, model, drug_names)
                    
                    # Store in history
                    history_entry = {
                        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "symptoms": user_symptoms,
                        "severity": severity,
                        "duration": duration,
                        "recommendations": recommendations[:3]  # Store top 3 recommendations
                    }
                    st.session_state.user_history.append(history_entry)
                    
                    # Display recommendations
                    st.subheader("Recommended Medications")
                    
                    # Display top 5 recommendations in a more visually appealing way
                    for i, drug in enumerate(recommendations[:5], 1):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.markdown(f"### {i}.")
                        with col2:
                            st.markdown(f"### {drug}")
                    
                    st.info("Please consult with a healthcare professional before taking any medication.")
            else:
                st.warning("Please select at least one symptom.")
    
    elif page == "My History":
        st.header("Your Recommendation History")
        
        if not st.session_state.user_history:
            st.info("You haven't requested any recommendations yet.")
        else:
            # Display history in reverse chronological order
            for i, entry in enumerate(reversed(st.session_state.user_history)):
                with st.expander(f"Consultation on {entry['timestamp']}"):
                    st.write(f"**Symptoms:** {', '.join(entry['symptoms'])}")
                    st.write(f"**Severity:** {entry['severity']}/10")
                    st.write(f"**Duration:** {entry['duration']}")
                    st.write("**Top Recommendations:**")
                    for j, drug in enumerate(entry['recommendations'], 1):
                        st.write(f"{j}. {drug}")

if __name__ == "__main__":
    main()
