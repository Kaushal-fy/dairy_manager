import streamlit as st
from src.data_manager import DataManager
from src.models import Expense
from datetime import date, datetime
import pandas as pd
import uuid

def render(dm: DataManager):
    st.header("Expenses Management")

    # --- Initialization ---
    if 'exp_edit_mode' not in st.session_state: st.session_state.exp_edit_mode = False
    if 'exp_edit_id' not in st.session_state: st.session_state.exp_edit_id = None
    
    # Defaults for inputs
    if 'exp_date' not in st.session_state: st.session_state.exp_date = date.today()
    if 'exp_name' not in st.session_state: st.session_state.exp_name = ""
    if 'exp_amount' not in st.session_state: st.session_state.exp_amount = 0.0
    if 'exp_desc' not in st.session_state: st.session_state.exp_desc = ""
    if 'exp_is_recurring' not in st.session_state: st.session_state.exp_is_recurring = False
    if 'exp_rec_type' not in st.session_state: st.session_state.exp_rec_type = "Monthly"
    if 'exp_next_due' not in st.session_state: st.session_state.exp_next_due = None

    # --- Add / Edit Form ---
    form_title = "Edit Expense" if st.session_state.exp_edit_mode else "Add New Expense"
    with st.expander(form_title, expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            new_date = st.date_input("Date", value=st.session_state.exp_date, key="w_exp_date")
            st.session_state.exp_name = st.text_input("Expense Name / Category", value=st.session_state.exp_name, key="w_exp_name")
        with col2:
            st.session_state.exp_amount = st.number_input("Amount (INR)", min_value=0.0, step=10.0, value=float(st.session_state.exp_amount), key="w_exp_amount")
        
        st.session_state.exp_desc = st.text_area("Description", value=st.session_state.exp_desc, key="w_exp_desc")
        
        # Dynamic Interaction
        is_rec_val = st.session_state.exp_is_recurring
        st.session_state.exp_is_recurring = st.checkbox("Recurring Expense?", value=is_rec_val, key="w_exp_is_rec")
        
        recurrence_type = None
        next_due_date = None
        
        if st.session_state.exp_is_recurring:
            col3, col4 = st.columns(2)
            with col3:
                opts = ["Monthly", "Yearly", "Custom"]
                try:
                    idx = opts.index(st.session_state.exp_rec_type) if st.session_state.exp_rec_type in opts else 0
                except: idx=0
                recurrence_type = st.selectbox("Recurrence Type", opts, index=idx, key="w_exp_rec_type")
            with col4:
                default_next = st.session_state.exp_next_due if st.session_state.exp_next_due else date.today()
                next_due_date = st.date_input("Next Due Date", value=default_next, key="w_exp_next_due")
        
        btn_text = "Update Expense" if st.session_state.exp_edit_mode else "Save Expense"
        
        col_b1, col_b2 = st.columns([1, 5])
        with col_b1:
            if st.button(btn_text):
                e_name = st.session_state.exp_name
                e_amount = st.session_state.exp_amount
                e_desc = st.session_state.exp_desc
                
                if not e_name:
                    st.error("Expense Name is required.")
                elif e_amount <= 0:
                    st.error("Amount must be greater than 0.")
                else:
                    new_id = st.session_state.exp_edit_id if st.session_state.exp_edit_mode else str(uuid.uuid4())
                    
                    new_expense = Expense(
                        id=new_id,
                        date=new_date.isoformat(),
                        name=e_name,
                        description=e_desc,
                        amount=e_amount,
                        is_recurring=st.session_state.exp_is_recurring,
                        recurrence_type=recurrence_type,
                        next_due_date=next_due_date.isoformat() if next_due_date else None
                    )
                    
                    if st.session_state.exp_edit_mode:
                        dm.update_expense(new_expense)
                        st.success("Expense updated!")
                    else:
                        dm.add_expense(new_expense)
                        st.success("Expense added!")
                    
                    # Reset state
                    st.session_state.exp_edit_mode = False
                    st.session_state.exp_edit_id = None
                    st.session_state.exp_name = ""
                    st.session_state.exp_amount = 0.0
                    st.session_state.exp_desc = ""
                    st.session_state.exp_is_recurring = False
                    st.session_state.exp_date = date.today()
                    st.rerun()
        
        with col_b2:
            if st.session_state.exp_edit_mode:
                if st.button("Cancel Edit"):
                    st.session_state.exp_edit_mode = False
                    st.session_state.exp_edit_id = None
                    st.session_state.exp_name = ""
                    st.session_state.exp_amount = 0.0
                    st.session_state.exp_desc = ""
                    st.session_state.exp_is_recurring = False
                    st.session_state.exp_date = date.today()
                    st.rerun()


    st.divider()

    # --- History Management (Edit / Delete) ---
    st.subheader("Recent Expenses History")
    expenses = dm.get_expenses()
    
    if expenses:
        # Sort desc by date
        expenses = sorted(expenses, key=lambda x: x.date, reverse=True)
        
        # Mobile-friendly card layout
        # Show last 50 for performance
        for exp in expenses[:50]:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{exp.date}** | {exp.name}")
                    st.caption(f"₹{exp.amount} | {exp.description}")
                    if exp.is_recurring:
                        st.caption(f"🔄 Recurring: {exp.recurrence_type} | Next: {exp.next_due_date or 'N/A'}")
                with col2:
                    # Edit Button
                    if st.button("✏️", key=f"edit_exp_{exp.id}", help="Edit"):
                        st.session_state.exp_edit_mode = True
                        st.session_state.exp_edit_id = exp.id
                        # Populate state
                        st.session_state.exp_date = datetime.fromisoformat(exp.date).date()
                        st.session_state.exp_name = exp.name
                        st.session_state.exp_amount = exp.amount
                        st.session_state.exp_desc = exp.description
                        st.session_state.exp_is_recurring = exp.is_recurring
                        st.session_state.exp_rec_type = exp.recurrence_type
                        if exp.next_due_date:
                            st.session_state.exp_next_due = datetime.fromisoformat(exp.next_due_date).date()
                        st.rerun()

                    # Delete Button with confirmation
                    if st.button("🗑️", key=f"del_exp_{exp.id}", help="Delete"):
                        if st.session_state.get(f"confirm_del_exp_{exp.id}", False):
                            dm.delete_expense(exp.id)
                            st.success("Expense deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_del_exp_{exp.id}"] = True
                            st.warning("Click again to confirm deletion")
                            st.rerun()
                st.divider()
    else:
        st.info("No expenses recorded yet.")
