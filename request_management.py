import streamlit as st
import pandas as pd
from supabase import create_client, Client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def load_leave_requests():
    try:
        response = supabase.table("LeaveRequests").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df.sort_values(by="ID").reset_index(drop=True)
        else:
            st.warning("No leave requests found.")
            return []
    except Exception as e:
        st.error(f"An exception occurred: {e}")
        return []

def manage_requests():
    st.title("Manage Leave Requests")

    try:
        response = supabase.table("LeaveRequests").select("*").execute()

        if response.data:
            requests_to_show = [req for req in response.data if req["Status"] == "Pending"]

            if not requests_to_show:
                st.success("No pending leave requests!")
                return

            for request in requests_to_show:
                request_id = request["id"]
                employee_id = request["EmployeeID"]
                employee_name = request["Name"]
                days_requested = request["Days Requested"]
                reason = request["Reason"]
                current_status = request["Status"]

                st.divider()
                st.subheader(f"Request ID: {request_id}")
                st.write(f"**Employee Name:** {employee_name}")
                st.write(f"**Days Requested:** {days_requested}")
                st.write(f"**Reason:** {reason}")

                new_status = st.selectbox(
                    f"Update Status for Request {request_id}",
                    ["Pending", "Approved", "Denied"],
                    index=["Pending", "Approved", "Denied"].index(current_status),
                    key=f"status_select_{request_id}"
                )

                if st.button(f"Update Request {request_id}", key=f"update_{request_id}"):
                    try:
                        if new_status == "Approved":
                            emp_response = (
                                supabase.table("Employees")
                                .select('"Leaves Available"')  
                                .eq("ID", employee_id)
                                .execute()
                            )

                            if emp_response.data:
                                current_leaves = emp_response.data[0]["Leaves Available"]

                                if current_leaves >= days_requested:
                                    new_leave_balance = current_leaves - days_requested
                                    
                                    supabase.table("Employees").update(
                                        {"Leaves Available": new_leave_balance}
                                    ).eq("ID", employee_id).execute()
                                else:
                                    st.error(f"Insufficient leave balance for {employee_name}.")
                                    return
                            else:
                                st.error(f"Failed to fetch leave balance for {employee_name}.")
                                return

                        update_response = (
                            supabase.table("LeaveRequests")
                            .update({"Status": new_status})
                            .eq("id", request_id)
                            .execute()
                        )

                        if update_response.data:
                            st.success(f"Request {request_id} updated to '{new_status}'.")
                            st.rerun()  
                        else:
                            st.error(f"Failed to update request {request_id}.")
                    except Exception as e:
                        st.error(f"Error updating request {request_id}: {e}")

        else:
            st.info("No leave requests found.")
    except Exception as e:
        st.error(f"Error fetching leave requests: {e}")

manage_requests()
