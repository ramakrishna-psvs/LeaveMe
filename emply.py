import streamlit as st
import pandas as pd
from supabase import create_client, Client

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def main():
    def load_employee_data():
        try:
            response = supabase.table("Employees").select("*").execute()
            if response.data:
                df = pd.DataFrame(response.data)
                return df.sort_values(by="ID").reset_index(drop=True) 
            else:
                st.warning("No data found in the Employees table.")
                return pd.DataFrame(columns=["ID", "Name", "Position", "Leaves Available"])
        except Exception as e:
            st.error(f"An exception occurred: {e}")
            return pd.DataFrame(columns=["ID", "Name", "Position", "Leaves Available"])

    def display_employees():
        st.title("Employee List")
        data = load_employee_data()

        if data.empty:
            st.warning("No employee data found. Add new employees to see them here.")
        else:
            employee_names = data["Name"].tolist()
            selected_name = st.selectbox("Select an Employee", employee_names)
            selected_employee = data[data["Name"] == selected_name]
            st.write("### Employee Details")
            st.write(selected_employee.reset_index(drop=True))
            
    display_employees()
main()
