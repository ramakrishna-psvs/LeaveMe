import streamlit as st
import pandas as pd
from supabase import create_client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def fetch_leave_requests():
    try:
        response = supabase.table("LeaveRequests").select("*").execute()
        if response.data:
            return response.data
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching leave requests: {e}")
        return []

if "leave_requests" not in st.session_state:
    st.session_state.leave_requests = fetch_leave_requests()

leave_requests = st.session_state.leave_requests

st.header("Leave History")

leave_history = [req for req in leave_requests if req["Status"] != "Pending"]

if leave_history:
    df_history = pd.DataFrame(leave_history)
    st.dataframe(df_history[["id", "EmployeeID", "Name", "Days Requested", "Reason", "Status"]])
else:
    st.info("No leave history available.")

st.header("Active Leave Requests")

active_requests = [req for req in leave_requests if req["Status"] == "Pending"]

if active_requests:
    df_active = pd.DataFrame(active_requests)
    st.dataframe(df_active[["ID", "EmployeeID", "Name", "Days Requested", "Reason", "Status"]])
else:
    st.info("No active leave requests.")
