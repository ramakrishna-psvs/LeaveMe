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
                return pd.DataFrame(response.data)  
            else:
                st.warning("No data found in the Employees table.")
                return pd.DataFrame(columns=["ID", "Name", "Position", "Leaves Available"])
        except Exception as e:
            st.error(f"An exception occurred: {e}")
            return pd.DataFrame(columns=["ID", "Name", "Position", "Leaves Available"])

    def add_employee_to_supabase(name, position, leaves):
        data = load_employee_data()
        new_id = int(data["ID"].max() + 1) if not data.empty else 1
        new_employee = {"ID": new_id, "Name": name, "Position": position, "Leaves Available": leaves}

        try:
            response = supabase.table("Employees").insert(new_employee).execute()
            if response.data:
                st.success(f"Employee '{name}' added successfully!")
            else:
                st.error(f"Failed to add employee. Response data: {response.data}")
        except Exception as e:
            st.error(f"An exception occurred while adding employee: {e}")

    def display_add_employee_form():
        st.title("Add New Employee")
        
        name = st.text_input("Employee Name", placeholder="Enter the employee's name")
        position = st.text_input("Position", placeholder="Enter the employee's position")
        leaves = st.number_input("Number of Leaves", min_value=0, step=1, value=10)

        if st.button("Add Employee"):
            if name.strip() and position.strip():  
                add_employee_to_supabase(name, position, leaves)
            else:
                st.error("Please fill out all fields.")

    display_add_employee_form()
main()
