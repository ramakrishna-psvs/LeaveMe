import streamlit as st
import bcrypt
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

if "user" not in st.session_state:
    st.session_state.user = None

Roles = ["Employer", "Employee"]

# Password hashing and verification
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode(), hashed_password.encode())

# Check if username exists in the database
def username_exists(username):
    response = supabase.table("users").select("username").eq("username", username).execute()
    return len(response.data) > 0

def signup():
    st.header("Sign Up")

    username = st.text_input("Choose a Username", key="signup_username")
    password = st.text_input("Choose a Password", type="password", key="signup_password")
    role = st.selectbox("Select Your Role", Roles, key="signup_role")

    if username_exists(username):
        st.error("Username already exists. Please log in instead.")
    else:
        if st.button("Sign Up", key="signup_button"):
            if username and password:
                hashed_pw = hash_password(password)
                response = supabase.table("users").insert({
                    "username": username,
                    "password_hash": hashed_pw,
                    "role": role.lower()
                }).execute()

                if response.data:
                    st.session_state.user = {
                        "username": username,
                        "role": role.lower(),
                    }
                    st.success("Signup successful! You can now log in.")
                else:
                    st.error("Something went wrong. Try again.")
            else:
                st.error("Please enter all fields.")

def login():
    """User login page."""
    st.header("Log in")
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", key="login_button"):
        if username and password:
            response = supabase.table("users").select("*").eq("username", username).execute()
            
            if response.data:
                user_data = response.data[0]
                if verify_password(password, user_data["password_hash"]):
                    st.session_state.user = {
                        "username": user_data["username"],
                        "role": user_data["role"],
                    }

                   

                    st.rerun()  
                else:
                    st.error("Invalid password. Please try again.")
            else:
                st.error("User not found. Check your username.")
        else:
            st.error("Please enter both username and password.")

def logout():
    """Properly reset session state and log out the user."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]  
    st.session_state.user = None  
    st.rerun() 

def landing_page():
    """Landing page to greet users and show login/logout buttons."""
    st.title("Welcome to LeaveMe!")
    if st.session_state.user is None:
        pick = st.selectbox("Login or Sign Up?", ["Login", "Sign Up"], key="login_or_signup")
        
        if pick == "Sign Up":
            signup()
        elif pick == "Login":
            login()
    else:
        if st.button("Logout", key="logout_button_landing"):
            logout()
            

logout_page = st.Page(landing_page, title="Log out", icon=":material/logout:")

request_1 = st.Page(
    "emply.py",
    title="Your Employees",
    icon=":material/man:",
)

request_2 = st.Page(
    "leave_apply.py",
    title="Apply for Leave",
    icon=":material/edit:",
)

respond_1 = st.Page(
    "request_management.py",
    title="Manage Requests",
    icon=":material/check_circle:",
)

respond_2 = st.Page(
    "dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
)

respond_3 = st.Page(
    "addemp.py",
    title="Add Employee",
    icon=":material/add_circle:",
)

respond_4 = st.Page(
    "leave_data.py",
    title="Download Data",
    icon=":material/download:",
)

employee_pages = [respond_2, request_2]
employer_pages = [respond_1, request_1, respond_3, respond_4]
account_pages = [logout_page]


if st.session_state.user is None:
    landing_page()
else:
    user = st.session_state.user
    page_dict = {}

    if user["role"] == "Employee":
        page_dict["Employee Panel"] = employee_pages  
    elif user["role"] == "Employer":
        page_dict["Employer Panel"] = employer_pages  

    if page_dict:
        pg = st.navigation({"Account": account_pages} | page_dict)
    else:
        pg = st.navigation([st.Page(signup)])

    st.logo("LeaveMe.png", size="large")
    st.subheader("_'Stay in sync, Faster than you think!'_", divider="gray")

    pg.run()
    