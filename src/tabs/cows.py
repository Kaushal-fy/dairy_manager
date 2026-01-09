import streamlit as st
from src.data_manager import DataManager
from src.models import Cow, CowEvent, Expense
from datetime import date, datetime
import pandas as pd
import uuid

def render(dm: DataManager):
    st.header("Cows Management")
    
    # --- State Init ---
    if 'cow_edit_mode' not in st.session_state: st.session_state.cow_edit_mode = False
    if 'cow_edit_id' not in st.session_state: st.session_state.cow_edit_id = None
    if 'cow_name' not in st.session_state: st.session_state.cow_name = ""
    if 'cow_breed' not in st.session_state: st.session_state.cow_breed = ""
    if 'cow_notes' not in st.session_state: st.session_state.cow_notes = ""
    if 'cow_bought_date' not in st.session_state: st.session_state.cow_bought_date = None
    if 'cow_bought_from' not in st.session_state: st.session_state.cow_bought_from = ""
    if 'cow_calf_born' not in st.session_state: st.session_state.cow_calf_born = None

    # --- Cow Master (Add / Edit) ---
    form_title = "Edit Cow" if st.session_state.cow_edit_mode else "Add New Cow"
    with st.expander(form_title, expanded=True):
        with st.form("cow_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                # Name is ID, so if editing, typically shouldn't change ID easily or it breaks links.
                # Simplification: Allow name change, but in a real app ID should be immutable UUID.
                # Here ID=Name. If we change Name, we essentially create new cow or need cascading update.
                # Let's disable Name editing if in edit mode to prevent breaking links.
                c_name = st.text_input("Cow Name / ID", value=st.session_state.cow_name, disabled=st.session_state.cow_edit_mode)
                c_breed = st.text_input("Breed", value=st.session_state.cow_breed)
                c_bought_from = st.text_input("Bought From", value=st.session_state.cow_bought_from)
            with col2:
                bd_val = st.session_state.cow_bought_date if st.session_state.cow_bought_date else None
                c_bought_date = st.date_input("Bought On Date", value=bd_val)
                
                cb_val = st.session_state.cow_calf_born if st.session_state.cow_calf_born else None
                c_calf_born = st.date_input("Calf Born On", value=cb_val)
            
            c_notes = st.text_area("Notes", value=st.session_state.cow_notes)
            
            btn_txt = "Update Cow" if st.session_state.cow_edit_mode else "Add Cow"
            c_submit = st.form_submit_button(btn_txt)
            
            if c_submit:
                if c_name:
                    # Logic
                    cow_obj = Cow(
                        id=st.session_state.cow_edit_id if st.session_state.cow_edit_mode else c_name,
                        name=c_name, 
                        breed=c_breed, 
                        notes=c_notes,
                        bought_date=c_bought_date.isoformat() if c_bought_date else None,
                        bought_from=c_bought_from,
                        calf_birth_date=c_calf_born.isoformat() if c_calf_born else None
                    )
                    
                    if st.session_state.cow_edit_mode:
                        dm.update_cow(cow_obj)
                        st.success("Updated.")
                    else:
                        existing = [c for c in dm.get_cows() if c.name == c_name]
                        if existing:
                            st.error("Cow exists.")
                        else:
                            dm.add_cow(cow_obj)
                            st.success("Added.")
                    
                    # Reset
                    st.session_state.cow_edit_mode = False
                    st.session_state.cow_edit_id = None
                    st.session_state.cow_name = ""
                    st.session_state.cow_breed = ""
                    st.session_state.cow_notes = ""
                    st.session_state.cow_bought_from = ""
                    st.session_state.cow_bought_date = None
                    st.session_state.cow_calf_born = None
                    st.rerun()
                else:
                    st.error("Name required.")
        
        if st.session_state.cow_edit_mode:
            if st.button("Cancel Edit", key="cancel_cow"):
                st.session_state.cow_edit_mode = False
                st.session_state.cow_edit_id = None
                # Reset fields logic...
                st.rerun()

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
        
        # Header with Edit/Delete
        c_head1, c_head2, c_head3 = st.columns([4, 1, 1])
        c_head1.subheader(f"Managing: {selected_cow.name}")
        if c_head2.button("Edit Cow", key=f"ed_cow_{selected_cow.id}"):
            st.session_state.cow_edit_mode = True
            st.session_state.cow_edit_id = selected_cow.id
            st.session_state.cow_name = selected_cow.name
            st.session_state.cow_breed = selected_cow.breed
            st.session_state.cow_notes = selected_cow.notes
            st.session_state.cow_bought_from = selected_cow.bought_from
            if selected_cow.bought_date: st.session_state.cow_bought_date = datetime.fromisoformat(selected_cow.bought_date).date()
            if selected_cow.calf_birth_date: st.session_state.cow_calf_born = datetime.fromisoformat(selected_cow.calf_birth_date).date()
            st.rerun()
            
        if c_head3.button("Delete Cow", key=f"del_cow_{selected_cow.id}"):
            if st.session_state.get(f"confirm_del_cow_{selected_cow.id}", False):
                dm.delete_cow(selected_cow.id)
                st.success("Cow deleted!")
                st.rerun()
            else:
                st.session_state[f"confirm_del_cow_{selected_cow.id}"] = True
                st.warning("Click again to confirm deletion")
                st.rerun()
            st.rerun()

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

        # --- Event Form (Init State) ---
        if 'cev_edit_mode' not in st.session_state: st.session_state.cev_edit_mode = False
        if 'cev_edit_id' not in st.session_state: st.session_state.cev_edit_id = None
        if 'cev_date' not in st.session_state: st.session_state.cev_date = date.today()
        if 'cev_type' not in st.session_state: st.session_state.cev_type = "Yield"
        if 'cev_val' not in st.session_state: st.session_state.cev_val = ""
        if 'cev_cost' not in st.session_state: st.session_state.cev_cost = 0.0
        if 'cev_notes' not in st.session_state: st.session_state.cev_notes = ""
        if 'cev_next_due' not in st.session_state: st.session_state.cev_next_due = None

        st.markdown("#### Record Event / Yield")
        
        with st.form("cow_event_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                ev_d_val = st.session_state.cev_date if st.session_state.cev_edit_mode else date.today()
                ev_date = st.date_input("Date", value=ev_d_val)
                
                types = ["Yield", "Vaccination", "Doctor Visit", "Other"]
                t_idx = types.index(st.session_state.cev_type) if st.session_state.cev_type in types else 0
                ev_type = st.selectbox("Event Type", types, index=t_idx)
            with col2:
                v_val = st.session_state.cev_val if st.session_state.cev_edit_mode else ""
                ev_value = st.text_input("Value", value=v_val, placeholder="e.g., 12.5 Litres")
                
                c_val = st.session_state.cev_cost if st.session_state.cev_edit_mode else 0.0
                ev_cost = st.number_input("Cost (if any)", min_value=0.0, step=10.0, value=float(c_val))
            
            n_val = st.session_state.cev_next_due if st.session_state.cev_next_due else None
            ev_next_due = st.date_input("Next Due Date", value=n_val)
            
            note_val = st.session_state.cev_notes if st.session_state.cev_edit_mode else ""
            ev_notes = st.text_input("Notes", value=note_val)
            
            btn_txt = "Update Record" if st.session_state.cev_edit_mode else "Save Record"
            ev_submit = st.form_submit_button(btn_txt)
            
            if ev_submit:
                if not ev_value:
                    st.error("Value required.")
                else:
                    new_id = st.session_state.cev_edit_id if st.session_state.cev_edit_mode else str(uuid.uuid4())
                    
                    new_event = CowEvent(
                        id=new_id,
                        date=ev_date.isoformat(),
                        cow_id=selected_cow.name,
                        event_type=ev_type,
                        value=ev_value,
                        cost=ev_cost,
                        next_due_date=ev_next_due.isoformat() if ev_next_due else None,
                        notes=ev_notes
                    )
                    
                    if st.session_state.cev_edit_mode:
                        dm.update_cow_event(new_event)
                        st.success("Updated.")
                    else:
                        dm.add_cow_event(new_event)
                        # Auto-add expense logic only on CREATE, not UPDATE to avoid dupes/confusion?
                        # Or checking if cost changed? simpler: only on create.
                        if ev_cost > 0:
                            # Add expense logic
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
                            st.success(f"Event recorded AND ₹{ev_cost} added to Expenses.")
                        else:
                            st.success("Event recorded.")
                    
                    # Reset
                    st.session_state.cev_edit_mode = False
                    st.session_state.cev_edit_id = None
                    st.session_state.cev_val = ""
                    st.session_state.cev_cost = 0.0
                    st.session_state.cev_notes = ""
                    st.session_state.cev_next_due = None
                    st.rerun()

        if st.session_state.cev_edit_mode:
            if st.button("Cancel Edit", key="cancel_cev"):
                st.session_state.cev_edit_mode = False
                st.session_state.cev_edit_id = None
                # Reset...
                st.rerun()

        # History Table (With Edit/Delete)
        st.markdown("#### History")
        all_events = dm.get_cow_events()
        cow_events = [e for e in all_events if e.cow_id == selected_cow.name]
        
        if cow_events:
            # Sort
            cow_events = sorted(cow_events, key=lambda x: x.date, reverse=True)
            
            # Custom Table
            c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 0.5, 0.5])
            c1.markdown("**Date**")
            c2.markdown("**Type**")
            c3.markdown("**Value**")
            c4.markdown("**Notes**")
            c5.markdown("**Ed**")
            c6.markdown("**Del**")
            
            for ev in cow_events:
                c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 0.5, 0.5])
                c1.write(ev.date)
                c2.write(ev.event_type)
                c3.write(ev.value)
                c4.write(ev.notes)
                
                if c5.button("✏️", key=f"ed_cev_{ev.id}"):
                    st.session_state.cev_edit_mode = True
                    st.session_state.cev_edit_id = ev.id
                    st.session_state.cev_date = datetime.fromisoformat(ev.date).date()
                    st.session_state.cev_type = ev.event_type
                    st.session_state.cev_val = ev.value
                    st.session_state.cev_cost = ev.cost
                    st.session_state.cev_notes = ev.notes
                    if ev.next_due_date:
                        st.session_state.cev_next_due = datetime.fromisoformat(ev.next_due_date).date()
                    st.rerun()
                    
                if c6.button("🗑️", key=f"del_cev_{ev.id}"):
                    if st.session_state.get(f"confirm_del_event_{ev.id}", False):
                        dm.delete_cow_event(ev.id)
                        st.success("Cow event deleted!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_del_event_{ev.id}"] = True
                        st.warning("Click again to confirm deletion")
                        st.rerun()
        else:
            st.info("No records found for this cow.")
