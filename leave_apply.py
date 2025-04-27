import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def load_employee_data():
    try:
        response = supabase.table("Employees").select("*").execute()
        if response.data:
            return response.data
        else:
            st.error("Failed to fetch employee data or no data available.")
            return []
    except Exception as e:
        st.error(f"An exception occurred: {e}")
        return []

def save_leave_request_to_db(employee_id, name, days_requested, reason):
    try:
        response = supabase.table("LeaveRequests").insert({
            "EmployeeID": employee_id,
            "Name": name,
            "Days Requested": days_requested,  
            "Reason": reason,
            "Status": "Pending"
        }).execute()

        if response.data:
            st.success(f"Leave request for {name} submitted successfully.")
        else:
            st.error("Failed to submit leave request.")
            st.error(f"Error details: {response.data}")
    except Exception as e:
        st.error(f"An exception occurred: {e}")


def leave_apply():
    st.title("Leave Application")

    employee_data = load_employee_data()

    if not employee_data:
        st.warning("No employee data found.")
        return

    employee_data_sorted = sorted(employee_data, key=lambda x: x["ID"])

    employee_names = [emp["Name"] for emp in employee_data_sorted]
    
    selected_name = st.selectbox("Select an Employee", employee_names)

    if selected_name:
        selected_employee = next(emp for emp in employee_data_sorted if emp["Name"] == selected_name)

        st.header("Request Leave")
        st.write(f"**Employee ID**: {selected_employee['ID']}")
        st.write(f"**Position**: {selected_employee['Position']}")
        st.write(f"**Available Leaves**: {selected_employee['Leaves Available']}")

        days_requested = st.number_input(
            "Number of days (Max available)", min_value=1, max_value=int(selected_employee["Leaves Available"]), step=1
        )
        reason = st.text_area("Reason for leave (250 chars max)", max_chars=250)

        if st.button("Submit Leave Request"):
            save_leave_request_to_db(
                selected_employee["ID"], selected_employee["Name"], days_requested, reason
            )

leave_apply()
