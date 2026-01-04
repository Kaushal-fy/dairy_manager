import streamlit as st
from src.data_manager import DataManager
from src.models import MilkSale, Payment, Buyer, DailyYield
from datetime import date, datetime
import pandas as pd
import uuid

def render(dm: DataManager):
    st.header("Milk Sales & Payments")
    
    # --- Top Stats ---
    today_iso = date.today().isoformat()
    all_events = dm.get_cow_events()
    all_daily_yields = dm.get_daily_yields()
    all_sales = dm.get_milk_sales()
    
    # 1. Produced
    yield_events = [e for e in all_events if e.date == today_iso and e.event_type == 'Yield']
    total_produced_cows = 0.0
    for e in yield_events:
        try:
            val_clean = e.value.lower().replace('l', '').replace('litres', '').strip()
            total_produced_cows += float(val_clean)
        except: pass
            
    yield_records = [y for y in all_daily_yields if y.date == today_iso]
    total_produced_daily = sum(y.quantity for y in yield_records)
    total_produced = total_produced_cows + total_produced_daily
            
    # 2. Sold
    sales_today = [s for s in all_sales if s.date == today_iso]
    total_sold = sum(s.quantity for s in sales_today)
    
    col_stat1, col_stat2 = st.columns(2)
    col_stat1.metric("Milk Produced Today", f"{total_produced:.1f} L")
    col_stat2.metric("Milk Sold Today", f"{total_sold:.1f} L", delta=f"{total_sold - total_produced:.1f} L" if total_produced > 0 else None)
    
    st.divider()
    
    # --- Daily Production Recording (With Edit/Delete) ---
    st.subheader("Daily Production Recording")
    
    # Init State for Yield Edit
    if 'dy_edit_mode' not in st.session_state: st.session_state.dy_edit_mode = False
    if 'dy_edit_id' not in st.session_state: st.session_state.dy_edit_id = None
    if 'dy_date' not in st.session_state: st.session_state.dy_date = date.today()
    if 'dy_qty' not in st.session_state: st.session_state.dy_qty = 0.0
    if 'dy_notes' not in st.session_state: st.session_state.dy_notes = ""

    with st.expander("Record Production", expanded=True):
        with st.form("daily_yield_form", clear_on_submit=False): # Must be False to keep values during edit
            col1, col2 = st.columns(2)
            with col1:
                # Use widget keys linked to session state? 
                # st.date_input doesn't sync bidirectional easily inside form without rerun.
                # Better to use values from state.
                d_val = st.date_input("Date", value=st.session_state.dy_date)
            with col2:
                q_val = st.number_input("Quantity (Litres)", min_value=0.0, step=0.1, value=float(st.session_state.dy_qty))
            
            n_val = st.text_input("Notes", value=st.session_state.dy_notes)
            
            btn_txt = "Update Record" if st.session_state.dy_edit_mode else "Record Production"
            submitted = st.form_submit_button(btn_txt)
            
            if submitted:
                if q_val > 0:
                    new_id = st.session_state.dy_edit_id if st.session_state.dy_edit_mode else str(uuid.uuid4())
                    
                    new_yield = DailyYield(
                        id=new_id,
                        date=d_val.isoformat(),
                        quantity=q_val,
                        notes=n_val
                    )
                    
                    if st.session_state.dy_edit_mode:
                        dm.update_daily_yield(new_yield)
                        st.success("Updated.")
                    else:
                        dm.add_daily_yield(new_yield)
                        st.success("Recorded.")
                    
                    # Reset
                    st.session_state.dy_edit_mode = False
                    st.session_state.dy_edit_id = None
                    st.session_state.dy_qty = 0.0
                    st.session_state.dy_notes = ""
                    st.rerun()
                else:
                    st.error("Quantity > 0 required.")
        
        if st.session_state.dy_edit_mode:
            if st.button("Cancel Edit", key="cancel_dy"):
                st.session_state.dy_edit_mode = False
                st.session_state.dy_edit_id = None
                st.session_state.dy_qty = 0.0
                st.session_state.dy_notes = ""
                st.rerun()

    # Expandable History for Daily Yields
    with st.expander("Production History (All Time)"):
        # Sort by Date Descending
        all_daily_yields_sorted = sorted(all_daily_yields, key=lambda x: x.date, reverse=True)
        if all_daily_yields_sorted:
            # Table Header
            c1, c2, c3, c4 = st.columns([2, 2, 3, 1])
            c1.markdown("**Date**")
            c2.markdown("**Qty (L)**")
            c3.markdown("**Notes**")
            c4.markdown("**Action**")
            
            for y in all_daily_yields_sorted:
                c1, c2, c3, c4 = st.columns([2, 2, 3, 1])
                c1.write(y.date)
                c2.write(f"{y.quantity}")
                c3.write(y.notes)
                if c4.button("🗑️", key=f"del_y_hist_{y.id}"):
                    dm.delete_daily_yield(y.id)
                    st.rerun()
        else:
            st.info("No records found.")

    st.divider()

    # --- Buyer Management ---
    with st.expander("Manage Buyers"):
        st.subheader("Add / Update Buyer")
        b_name_input = st.text_input("Buyer Name", key="new_buyer_name")
        b_rate_input = st.number_input("Default Rate/L", min_value=0.0, step=0.5, key="new_buyer_rate")
        
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("Add/Update Buyer"):
                if b_name_input and b_rate_input > 0:
                    existing = [b for b in dm.get_buyers() if b.name == b_name_input]
                    if existing:
                        dm.update_buyer(b_name_input, b_rate_input)
                        st.success(f"Updated rate for {b_name_input}")
                    else:
                        dm.add_buyer(Buyer(name=b_name_input, default_rate=b_rate_input))
                        st.success(f"Added buyer {b_name_input}")
                    st.rerun()
                else:
                    st.error("Name and Rate required.")
        
        st.markdown("---")
        st.subheader("Existing Buyers")
        buyers = dm.get_buyers()
        if buyers:
            for b in buyers:
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(b.name)
                c2.write(f"₹{b.default_rate}/L")
                if c3.button("Delete", key=f"del_buyer_{b.name}"):
                    dm.delete_buyer(b.name)
                    st.success(f"Deleted {b.name}")
                    st.rerun()
        else:
            st.info("No buyers added.")

    st.divider()

    # --- Milk Sales (With Edit/Delete) ---
    buyers = dm.get_buyers()
    if not buyers:
        st.warning("Please add buyers first.")
        return

    buyer_names = [b.name for b in buyers]
    
    # Init Sales Edit State
    if 'sale_edit_mode' not in st.session_state: st.session_state.sale_edit_mode = False
    if 'sale_edit_id' not in st.session_state: st.session_state.sale_edit_id = None
    # We need separate variables to pre-fill the form
    if 'sale_date' not in st.session_state: st.session_state.sale_date = date.today()
    if 'sale_buyer' not in st.session_state: st.session_state.sale_buyer = buyer_names[0] if buyer_names else ""
    if 'sale_qty' not in st.session_state: st.session_state.sale_qty = 0.0
    if 'sale_rate' not in st.session_state: st.session_state.sale_rate = 0.0

    
    tab1, tab2, tab3 = st.tabs(["Daily Entry", "Payments/Advances", "Buyer Ledgers"])

    with tab1:
        st.subheader("Record Milk Sale")
        
        if not st.session_state.sale_edit_mode:
            # Normal Flow
            sel_buyer = st.selectbox("Select Buyer", buyer_names, key="s_buyer_sel")
            current_buyer = next((b for b in buyers if b.name == sel_buyer), None)
            def_rate = current_buyer.default_rate if current_buyer else 0.0
        else:
            # Edit Flow
            try:
                b_idx = buyer_names.index(st.session_state.sale_buyer)
            except: b_idx = 0
            sel_buyer = st.selectbox("Select Buyer", buyer_names, index=b_idx, key="s_buyer_sel_edit")
            def_rate = st.session_state.sale_rate 
            
        with st.form("sale_form"):
            col1, col2 = st.columns(2)
            with col1:
                d_val = st.session_state.sale_date if st.session_state.sale_edit_mode else date.today()
                s_date = st.date_input("Date", value=d_val)
                q_val = st.session_state.sale_qty if st.session_state.sale_edit_mode else 0.0
                s_qty = st.number_input("Quantity (Litres)", min_value=0.0, step=0.1, value=float(q_val))
            
            with col2:
                r_val = def_rate
                s_rate = st.number_input("Rate (INR/L)", value=float(r_val), step=0.5)
            
            btn_txt = "Update Sale" if st.session_state.sale_edit_mode else "Record Sale"
            submit = st.form_submit_button(btn_txt)
            
            if submit:
                if s_qty > 0 and s_rate > 0:
                    total = s_qty * s_rate
                    new_id = st.session_state.sale_edit_id if st.session_state.sale_edit_mode else str(uuid.uuid4())
                    
                    sale = MilkSale(
                        id=new_id,
                        date=s_date.isoformat(),
                        buyer_name=sel_buyer,
                        quantity=s_qty,
                        rate=s_rate,
                        total_amount=total
                    )
                    
                    if st.session_state.sale_edit_mode:
                        dm.update_milk_sale(sale)
                        st.success("Updated.")
                    else:
                        dm.add_milk_sale(sale)
                        st.success("Recorded.")
                    
                    st.session_state.sale_edit_mode = False
                    st.session_state.sale_edit_id = None
                    st.session_state.sale_qty = 0.0
                    st.rerun()
                else:
                    st.error("Invalid Input")
        
        if st.session_state.sale_edit_mode:
            if st.button("Cancel Edit", key="cancel_sale"):
                st.session_state.sale_edit_mode = False
                st.session_state.sale_edit_id = None
                st.session_state.sale_qty = 0.0
                st.rerun()

        # Expandable History for Sales
        with st.expander("Sales History (All Time)"):
            all_sales_sorted = sorted(all_sales, key=lambda x: x.date, reverse=True)
            if all_sales_sorted:
                c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 1])
                c1.markdown("**Date**")
                c2.markdown("**Buyer**")
                c3.markdown("**Qty**")
                c4.markdown("**Total**")
                c5.markdown("**Del**")
                
                for s in all_sales_sorted:
                    c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 1])
                    c1.write(s.date)
                    c2.write(s.buyer_name)
                    c3.write(f"{s.quantity}L")
                    c4.write(f"₹{s.total_amount}")
                    if c5.button("🗑️", key=f"del_s_hist_{s.id}"):
                        dm.delete_milk_sale(s.id)
                        st.rerun()
            else:
                st.info("No records.")

    with tab2:
        st.subheader("Record Payment")
        p_buyer = st.selectbox("Buyer", buyer_names, key="pay_buyer_select")
        with st.form("pay_form"):
            col1, col2 = st.columns(2)
            with col1:
                p_date = st.date_input("Date", value=date.today())
                p_type = st.radio("Type", ["Payment", "Advance"])
            with col2:
                p_amount = st.number_input("Amount", min_value=0.0, step=100.0)
                p_desc = st.text_input("Notes")
            if st.form_submit_button("Save"):
                dm.add_payment(Payment(str(uuid.uuid4()), p_date.isoformat(), p_buyer, p_type, p_amount, p_desc))
                st.success("Saved")
                st.rerun()

    with tab3:
        st.subheader("Ledger")
        summary_data = []
        all_sales = dm.get_milk_sales()
        all_payments = dm.get_payments()
        for b in buyers:
            b_sales = [s for s in all_sales if s.buyer_name == b.name]
            b_payments = [p for p in all_payments if p.buyer_name == b.name]
            bal = sum(s.total_amount for s in b_sales) - sum(p.amount for p in b_payments)
            summary_data.append({"Buyer": b.name, "Balance": bal})
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
