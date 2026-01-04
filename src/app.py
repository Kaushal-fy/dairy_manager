import streamlit as st
import sys
import os
import json

# Fix Python Path to allow importing from src when running from root or src
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from src.data_manager import LocalJSONBackend
from src.google_sheets_backend import GoogleSheetsBackend
from src.tabs import dashboard, expenses, milk_sales, cows, reports

# Page Config
st.set_page_config(page_title="Dairy Manager", layout="wide", page_icon="🐄")

# --- Backend Initialization Logic ---
def get_backend():
    creds_found = None
    
    # 1. Check Streamlit Secrets (Best for Cloud Deployment)
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds_found = creds_dict
            return GoogleSheetsBackend(creds_dict), "Cloud (Google Sheets)"
    except Exception as e:
        # Save exception to report if credentials were found but connection failed
        if creds_found:
             return LocalJSONBackend(data_dir=os.path.join(parent_dir, "local_data")), f"Local (Connection Error: {e})"
        pass

    # 2. Check for local credentials.json file
    cred_paths = ["credentials.json", os.path.join(parent_dir, "credentials.json")]
    
    for path in cred_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    creds_dict = json.load(f)
                creds_found = creds_dict
                return GoogleSheetsBackend(creds_dict), "Cloud (Google Sheets - Local Key)"
            except Exception as e:
                # Return Local Backend but with error info + extracted email
                client_email = "Unknown"
                if creds_found and 'client_email' in creds_found:
                    client_email = creds_found['client_email']
                
                # Store email in session state for UI display
                st.session_state.service_account_email = client_email
                return LocalJSONBackend(data_dir=os.path.join(parent_dir, "local_data")), f"Local (Error: {e})"

    # 3. Fallback to Local JSON
    data_dir = os.path.join(parent_dir, "local_data")
    return LocalJSONBackend(data_dir=data_dir), "Local Mode (No Credentials Found)"

if 'data_manager' not in st.session_state:
    dm, mode_name = get_backend()
    st.session_state.data_manager = dm
    st.session_state.app_mode = mode_name

# --- UI Layout ---

st.title("🐄 Dairy Business Management")

# Sidebar
with st.sidebar:
    status_color = "green" if "Cloud" in st.session_state.app_mode and "Error" not in st.session_state.app_mode else "orange"
    st.caption(f"Backend Status:")
    st.markdown(f":{status_color}[{st.session_state.app_mode}]")
    
    # Logic Fix: Only show troubleshooting if we are strictly in Local Mode (Offline or Error)
    # The string "Cloud (Google Sheets - Local Key)" contains "Local", so we must check for "Cloud" first.
    
    if "Cloud" not in st.session_state.app_mode:
        if "No Credentials Found" in st.session_state.app_mode:
            st.info("To enable Google Sheets sync, add 'credentials.json' to the root folder or configure secrets.")
        elif "Error" in st.session_state.app_mode:
             st.error("Connection Failed.")
             if 'service_account_email' in st.session_state:
                 st.markdown("### Action Required")
                 st.markdown("Ensure you have created a Google Sheet named **DairyManagerDB**.")
                 st.markdown("Share it with this email:")
                 st.code(st.session_state.service_account_email, language="text")
    
    st.divider()
    st.caption("Navigation")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard", "Expenses", "Milk Sales", "Cows", "Reports"
])

with tab1:
    dashboard.render(st.session_state.data_manager)

with tab2:
    expenses.render(st.session_state.data_manager)

with tab3:
    milk_sales.render(st.session_state.data_manager)

with tab4:
    cows.render(st.session_state.data_manager)

with tab5:
    reports.render(st.session_state.data_manager)
