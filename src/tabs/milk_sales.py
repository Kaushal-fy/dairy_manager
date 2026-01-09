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
        with st.form("daily_yield_form", clear_on_submit=False): 
            col1, col2 = st.columns(2)
            with col1:
                d_val = st.session_state.dy_date if st.session_state.dy_edit_mode else date.today()
                dy_date = st.date_input("Date", value=d_val)
            with col2:
                q_val = st.session_state.dy_qty if st.session_state.dy_edit_mode else 0.0
                dy_qty = st.number_input("Quantity (Litres)", min_value=0.0, step=0.1, value=float(q_val))
            
            n_val = st.session_state.dy_notes if st.session_state.dy_edit_mode else ""
            dy_notes = st.text_input("Notes", value=n_val)
            
            btn_txt = "Update Record" if st.session_state.dy_edit_mode else "Record Production"
            submitted = st.form_submit_button(btn_txt)
            
            if submitted:
                if dy_qty > 0:
                    new_id = st.session_state.dy_edit_id if st.session_state.dy_edit_mode else str(uuid.uuid4())
                    
                    new_yield = DailyYield(
                        id=new_id,
                        date=dy_date.isoformat(),
                        quantity=dy_qty,
                        notes=dy_notes
                    )
                    
                    if st.session_state.dy_edit_mode:
                        dm.update_daily_yield(new_yield)
                        st.success("Updated.")
                    else:
                        dm.add_daily_yield(new_yield)
                        st.success("Recorded.")
                    
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

    # Expandable History for Daily Yields (With Edit)
    with st.expander("Production History (All Time)"):
        all_daily_yields_sorted = sorted(all_daily_yields, key=lambda x: x.date, reverse=True)
        if all_daily_yields_sorted:
            c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 0.5, 0.5])
            c1.markdown("**Date**")
            c2.markdown("**Qty (L)**")
            c3.markdown("**Notes**")
            c4.markdown("**Ed**")
            c5.markdown("**Del**")
            
            for y in all_daily_yields_sorted:
                c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 0.5, 0.5])
                c1.write(y.date)
                c2.write(f"{y.quantity}")
                c3.write(y.notes)
                if c4.button("✏️", key=f"ed_y_hist_{y.id}"):
                    st.session_state.dy_edit_mode = True
                    st.session_state.dy_edit_id = y.id
                    st.session_state.dy_date = datetime.fromisoformat(y.date).date()
                    st.session_state.dy_qty = y.quantity
                    st.session_state.dy_notes = y.notes
                    st.rerun()
                if c5.button("🗑️", key=f"del_y_hist_{y.id}"):
                    if st.session_state.get(f"confirm_del_yield_{y.id}", False):
                        dm.delete_daily_yield(y.id)
                        st.success("Production record deleted!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_del_yield_{y.id}"] = True
                        st.warning("Click again to confirm deletion")
                        st.rerun()
        else:
            st.info("No records found.")

    st.divider()

    # --- Buyer Management ---
    with st.expander("Manage Buyers"):
        st.subheader("Add / Update Buyer")
        b_name_input = st.text_input("Buyer Name", key="new_buyer_name")
        b_rate_input = st.number_input("Default Rate/L", min_value=0.0, step=0.5, key="new_buyer_rate")
        
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
        
        st.markdown("---")
        st.subheader("Existing Buyers")
        buyers = dm.get_buyers()
        if buyers:
            c1, c2, c3, c4 = st.columns([3, 2, 0.5, 0.5])
            c1.markdown("**Name**")
            c2.markdown("**Rate/L**")
            c3.markdown("**Ed**")
            c4.markdown("**Del**")
            
            for b in buyers:
                c1, c2, c3, c4 = st.columns([3, 2, 0.5, 0.5])
                c1.write(b.name)
                c2.write(f"₹{b.default_rate}")
                
                if c3.button("✏️", key=f"ed_buyer_{b.name}"):
                    # Pre-populate the form with existing buyer data
                    st.session_state.new_buyer_name = b.name
                    st.session_state.new_buyer_rate = b.default_rate
                    st.info(f"Editing {b.name} - update the form above")
                    st.rerun()
                    
                if c4.button("🗑️", key=f"del_buyer_{b.name}"):
                    if st.session_state.get(f"confirm_del_buyer_{b.name}", False):
                        dm.delete_buyer(b.name)
                        st.success(f"Buyer {b.name} deleted!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_del_buyer_{b.name}"] = True
                        st.warning("Click again to confirm deletion")
                        st.rerun()

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

        # Sales History (With Edit)
        with st.expander("Sales History (All Time)"):
            all_sales_sorted = sorted(all_sales, key=lambda x: x.date, reverse=True)
            if all_sales_sorted:
                c1, c2, c3, c4, c5, c6 = st.columns([2, 3, 2, 2, 0.5, 0.5])
                c1.markdown("**Date**")
                c2.markdown("**Buyer**")
                c3.markdown("**Qty**")
                c4.markdown("**Total**")
                c5.markdown("**Ed**")
                c6.markdown("**Del**")
                
                for s in all_sales_sorted:
                    c1, c2, c3, c4, c5, c6 = st.columns([2, 3, 2, 2, 0.5, 0.5])
                    c1.write(s.date)
                    c2.write(s.buyer_name)
                    c3.write(f"{s.quantity}L")
                    c4.write(f"₹{s.total_amount}")
                    if c5.button("✏️", key=f"ed_s_hist_{s.id}"):
                        st.session_state.sale_edit_mode = True
                        st.session_state.sale_edit_id = s.id
                        st.session_state.sale_date = datetime.fromisoformat(s.date).date()
                        st.session_state.sale_buyer = s.buyer_name
                        st.session_state.sale_qty = s.quantity
                        st.session_state.sale_rate = s.rate
                        st.rerun()
                    if c6.button("🗑️", key=f"del_s_hist_{s.id}"):
                        if st.session_state.get(f"confirm_del_sale_{s.id}", False):
                            dm.delete_milk_sale(s.id)
                            st.success("Sale deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_del_sale_{s.id}"] = True
                            st.warning("Click again to confirm deletion")
                            st.rerun()
            else:
                st.info("No records.")

    with tab2:
        st.subheader("Payments & Advances")
        
        # Init Payment Edit State
        if 'pay_edit_mode' not in st.session_state: st.session_state.pay_edit_mode = False
        if 'pay_edit_id' not in st.session_state: st.session_state.pay_edit_id = None
        if 'pay_date' not in st.session_state: st.session_state.pay_date = date.today()
        if 'pay_buyer' not in st.session_state: st.session_state.pay_buyer = buyer_names[0] if buyer_names else ""
        if 'pay_type' not in st.session_state: st.session_state.pay_type = "Payment"
        if 'pay_amount' not in st.session_state: st.session_state.pay_amount = 0.0
        if 'pay_notes' not in st.session_state: st.session_state.pay_notes = ""

        form_title = "Edit Payment" if st.session_state.pay_edit_mode else "Record Payment"
        with st.expander(form_title, expanded=True):
            if not st.session_state.pay_edit_mode:
                p_buyer = st.selectbox("Buyer", buyer_names, key="pay_buyer_select")
            else:
                try:
                    b_idx = buyer_names.index(st.session_state.pay_buyer)
                except: b_idx = 0
                p_buyer = st.selectbox("Buyer", buyer_names, index=b_idx, key="pay_buyer_select_edit")
            
            with st.form("pay_form"):
                col1, col2 = st.columns(2)
                with col1:
                    d_val = st.session_state.pay_date if st.session_state.pay_edit_mode else date.today()
                    p_date = st.date_input("Date", value=d_val)
                    t_val = st.session_state.pay_type if st.session_state.pay_edit_mode else "Payment"
                    p_type = st.radio("Type", ["Payment", "Advance"], index=0 if t_val == "Payment" else 1)
                with col2:
                    a_val = st.session_state.pay_amount if st.session_state.pay_edit_mode else 0.0
                    p_amount = st.number_input("Amount", min_value=0.0, step=100.0, value=float(a_val))
                    n_val = st.session_state.pay_notes if st.session_state.pay_edit_mode else ""
                    p_desc = st.text_input("Notes", value=n_val)
                
                btn_txt = "Update Payment" if st.session_state.pay_edit_mode else "Save Payment"
                if st.form_submit_button(btn_txt):
                    if p_amount > 0:
                        new_id = st.session_state.pay_edit_id if st.session_state.pay_edit_mode else str(uuid.uuid4())
                        
                        payment = Payment(
                            id=new_id,
                            date=p_date.isoformat(),
                            buyer_name=p_buyer,
                            entry_type=p_type,
                            amount=p_amount,
                            notes=p_desc
                        )
                        
                        if st.session_state.pay_edit_mode:
                            dm.update_payment(payment)
                            st.success("Payment updated!")
                        else:
                            dm.add_payment(payment)
                            st.success("Payment saved!")
                        
                        # Reset state
                        st.session_state.pay_edit_mode = False
                        st.session_state.pay_edit_id = None
                        st.session_state.pay_amount = 0.0
                        st.session_state.pay_notes = ""
                        st.rerun()
                    else:
                        st.error("Amount must be greater than 0")
            
            if st.session_state.pay_edit_mode:
                if st.button("Cancel Edit", key="cancel_payment"):
                    st.session_state.pay_edit_mode = False
                    st.session_state.pay_edit_id = None
                    st.session_state.pay_amount = 0.0
                    st.session_state.pay_notes = ""
                    st.rerun()

        # Payment History with Edit/Delete
        with st.expander("Payment History"):
            all_payments = dm.get_payments()
            if all_payments:
                payments_sorted = sorted(all_payments, key=lambda x: x.date, reverse=True)
                c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 3, 2, 2, 3, 0.5, 0.5])
                c1.markdown("**Date**")
                c2.markdown("**Buyer**")
                c3.markdown("**Type**")
                c4.markdown("**Amount**")
                c5.markdown("**Notes**")
                c6.markdown("**Ed**")
                c7.markdown("**Del**")
                
                for p in payments_sorted:
                    c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 3, 2, 2, 3, 0.5, 0.5])
                    c1.write(p.date)
                    c2.write(p.buyer_name)
                    c3.write(p.entry_type)
                    c4.write(f"₹{p.amount}")
                    c5.write(p.notes or "")
                    if c6.button("✏️", key=f"ed_pay_{p.id}"):
                        st.session_state.pay_edit_mode = True
                        st.session_state.pay_edit_id = p.id
                        st.session_state.pay_date = datetime.fromisoformat(p.date).date()
                        st.session_state.pay_buyer = p.buyer_name
                        st.session_state.pay_type = p.entry_type
                        st.session_state.pay_amount = p.amount
                        st.session_state.pay_notes = p.notes or ""
                        st.rerun()
                    if c7.button("🗑️", key=f"del_pay_{p.id}"):
                        if st.session_state.get(f"confirm_del_pay_{p.id}", False):
                            dm.delete_payment(p.id)
                            st.success("Payment deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_del_pay_{p.id}"] = True
                            st.warning("Click again to confirm deletion")
                            st.rerun()
            else:
                st.info("No payment records found.")

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
