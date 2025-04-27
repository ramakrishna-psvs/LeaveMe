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

st.header("Leave Data")

leave_requests = fetch_leave_requests()

leave_history = [req for req in leave_requests if req["Status"] != "Pending"]

if leave_history:
    df_lh = pd.DataFrame(leave_history)
    st.dataframe(df_lh[["id", "EmployeeID", "Name", "Days Requested", "Reason", "Status"]])

    csv_data = df_lh.to_csv(index=False)
    st.download_button(
        label="Download Leave History as CSV",
        data=csv_data,
        file_name="leave_history.csv",
        mime="text/csv"
    )
else:
    st.info("No leave data available.")
