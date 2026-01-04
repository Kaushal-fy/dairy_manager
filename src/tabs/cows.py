import streamlit as st
from src.data_manager import DataManager
from src.models import Cow, CowEvent, Expense
from datetime import date
import pandas as pd
import uuid

def render(dm: DataManager):
    st.header("Cows Management")
    
    # --- Cow Master (Add New Cow) ---
    with st.expander("Add New Cow"):
        # User requested fields: Bought on date, Bought from, Calf born on
        with st.form("add_cow_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                c_name = st.text_input("Cow Name / ID (Unique)")
                c_breed = st.text_input("Breed (Optional)")
                c_bought_from = st.text_input("Bought From (Optional)")
            with col2:
                c_bought_date = st.date_input("Bought On Date", value=None)
                c_calf_born = st.date_input("Calf Born On (if applicable)", value=None)
            
            c_notes = st.text_area("Notes")
            c_submit = st.form_submit_button("Add Cow")
            
            if c_submit:
                if c_name:
                    existing = [c for c in dm.get_cows() if c.name == c_name]
                    if existing:
                        st.error("Cow with this name/ID already exists.")
                    else:
                        new_cow = Cow(
                            id=c_name, 
                            name=c_name, 
                            breed=c_breed, 
                            notes=c_notes,
                            bought_date=c_bought_date.isoformat() if c_bought_date else None,
                            bought_from=c_bought_from,
                            calf_birth_date=c_calf_born.isoformat() if c_calf_born else None
                        )
                        dm.add_cow(new_cow)
                        st.success(f"Added Cow: {c_name}")
                        st.rerun()
                else:
                    st.error("Cow Name is required.")

    st.divider()
    
    # --- View & Manage Specific Cow ---
    all_cows = dm.get_cows()
    if not all_cows:
        st.info("No cows added yet.")
        return
        
    cow_names = [c.name for c in all_cows]
    selected_cow_name = st.selectbox("Select Cow to Manage", cow_names)
    
    if selected_cow_name:
        selected_cow = next(c for c in all_cows if c.name == selected_cow_name)
        
        # Display extended info
        st.subheader(f"Managing: {selected_cow.name}")
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.caption(f"**Breed:** {selected_cow.breed}")
            st.caption(f"**Bought From:** {selected_cow.bought_from or 'N/A'}")
        with info_col2:
            st.caption(f"**Bought Date:** {selected_cow.bought_date or 'N/A'}")
            st.caption(f"**Calf Born:** {selected_cow.calf_birth_date or 'N/A'}")
        with info_col3:
            st.caption(f"**Notes:** {selected_cow.notes}")
        
        st.divider()

        # Add Event Form (Vaccination/Doctor logic)
        st.markdown("#### Record Event / Yield")
        st.info("Use this form to record Vaccinations, Doctor Visits, or Milk Yield.")
        
        with st.form("cow_event_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ev_date = st.date_input("Date", value=date.today())
                # Explicitly list Vaccination and Doctor Visit as requested
                ev_type = st.selectbox("Event Type", ["Yield", "Vaccination", "Doctor Visit", "Other"])
            with col2:
                ev_value = st.text_input("Value (e.g., 12.5 Litres, 'FMD Vaccine', 'Checkup')")
                ev_cost = st.number_input("Cost (if any)", min_value=0.0, step=10.0)
                
            ev_next_due = st.date_input("Next Due Date (if recurring)", value=None)
            ev_notes = st.text_input("Notes")
            
            ev_submit = st.form_submit_button("Save Record")
            
            if ev_submit:
                if not ev_value:
                    st.error("Please provide a value/description.")
                else:
                    new_event = CowEvent(
                        id=str(uuid.uuid4()),
                        date=ev_date.isoformat(),
                        cow_id=selected_cow.name,
                        event_type=ev_type,
                        value=ev_value,
                        cost=ev_cost,
                        next_due_date=ev_next_due.isoformat() if ev_next_due else None,
                        notes=ev_notes
                    )
                    dm.add_cow_event(new_event)
                    
                    if ev_cost > 0:
                        expense_desc = f"Cow {selected_cow.name} - {ev_type}: {ev_value}"
                        new_expense = Expense(
                            id=str(uuid.uuid4()),
                            date=ev_date.isoformat(),
                            name=f"Cow Expense - {ev_type}",
                            description=expense_desc,
                            amount=ev_cost,
                            is_recurring=False,
                            cow_id=selected_cow.name
                        )
                        dm.add_expense(new_expense)
                        st.success(f"Event recorded AND ₹{ev_cost} added to main Expenses.")
                    else:
                        st.success("Event recorded.")
                    
                    st.rerun()

        # History Table
        st.markdown("#### History")
        all_events = dm.get_cow_events()
        cow_events = [e for e in all_events if e.cow_id == selected_cow.name]
        
        if cow_events:
            df = pd.DataFrame([e.__dict__ for e in cow_events])
            if 'id' in df.columns: df = df.drop(columns=['id'])
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by='date', ascending=False)
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No records found for this cow.")
