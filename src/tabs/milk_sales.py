import streamlit as st
from src.data_manager import DataManager
from src.models import MilkSale, Payment, Buyer, DailyYield
from src.ui_components import CalendarView, EnhancedDataTable, NavigationControls, RowNumberFormatter, SearchInterface, DateRangeSelector
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

    # Expandable History for Daily Yields (With Edit) - Enhanced formatting
    with st.expander("Production History (All Time)"):
        all_daily_yields_sorted = sorted(all_daily_yields, key=lambda x: x.date, reverse=True)
        if all_daily_yields_sorted:
            for i, y in enumerate(all_daily_yields_sorted):
                row_number = RowNumberFormatter.get_row_number(i)
                
                # Use EnhancedDataTable for consistent formatting
                edit_clicked, delete_clicked = EnhancedDataTable.render_transaction_row(
                    y, row_number, "yield"
                )
                
                # Handle edit button click
                if edit_clicked:
                    st.session_state.dy_edit_mode = True
                    st.session_state.dy_edit_id = y.id
                    try:
                        st.session_state.dy_date = datetime.fromisoformat(y.date).date()
                    except (ValueError, AttributeError):
                        st.session_state.dy_date = date.today()
                    st.session_state.dy_qty = y.quantity
                    st.session_state.dy_notes = y.notes
                    st.rerun()
                
                # Handle delete button click
                if delete_clicked:
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
        # Enhanced Buyer Management with search and better formatting
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
            for i, b in enumerate(buyers):
                row_number = RowNumberFormatter.get_row_number(i)
                
                # Use EnhancedDataTable for consistent formatting and clickable names
                edit_clicked, delete_clicked, name_clicked = EnhancedDataTable.render_buyer_row(b, row_number)
                
                # Handle buyer name click - open calendar view
                if name_clicked:
                    st.session_state.selected_buyer_for_calendar = b.name
                    st.session_state.buyer_calendar_view = True
                    st.rerun()
                
                # Handle edit button click
                if edit_clicked:
                    # Pre-populate the form with existing buyer data
                    st.session_state.new_buyer_name = b.name
                    st.session_state.new_buyer_rate = b.default_rate
                    st.info(f"Editing {b.name} - update the form above")
                    st.rerun()
                
                # Handle delete button click
                if delete_clicked:
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

        # Sales History with Calendar View - Replace messy "All Time" view
        st.subheader("Sales History")
        
        # Convert sales data to calendar format
        sales_calendar_data = []
        for sale in all_sales:
            sales_calendar_data.append({
                'date': sale.date,
                'buyer_name': sale.buyer_name,
                'quantity': sale.quantity,
                'rate': sale.rate,
                'total_amount': sale.total_amount,
                'id': sale.id
            })
        
        # Debug information
        st.write(f"📊 Total sales records: {len(all_sales)}")
        if sales_calendar_data:
            st.write(f"📅 Date range: {min(s['date'] for s in sales_calendar_data)} to {max(s['date'] for s in sales_calendar_data)}")
        
        # Initialize calendar view state
        if 'sales_calendar_view' not in st.session_state:
            st.session_state.sales_calendar_view = True
        if 'sales_selected_date' not in st.session_state:
            st.session_state.sales_selected_date = None
        
        # Navigation controls for calendar
        current_date = NavigationControls.render(key_prefix="sales_nav")
        
        # Calendar view
        calendar_view = CalendarView()
        calendar_result = calendar_view.render(
            data_points=sales_calendar_data,
            selected_month=current_date,
            calendar_key="sales_calendar"
        )
        
        # Handle date selection from calendar
        selected_date = calendar_view.get_selected_date_from_calendar(calendar_result)
        if selected_date:
            st.session_state.sales_selected_date = selected_date
        
        # Display transactions for selected date
        if st.session_state.sales_selected_date:
            st.subheader(f"Sales for {st.session_state.sales_selected_date}")
            
            # Filter sales for selected date
            selected_sales = [s for s in all_sales if s.date == st.session_state.sales_selected_date]
            
            if selected_sales:
                for i, sale in enumerate(selected_sales):
                    row_number = RowNumberFormatter.get_row_number(i)
                    
                    # Use EnhancedDataTable for proper formatting and button positioning
                    edit_clicked, delete_clicked = EnhancedDataTable.render_transaction_row(
                        sale, row_number, "sale"
                    )
                    
                    # Handle edit button click
                    if edit_clicked:
                        st.session_state.sale_edit_mode = True
                        st.session_state.sale_edit_id = sale.id
                        try:
                            st.session_state.sale_date = datetime.fromisoformat(sale.date).date()
                        except (ValueError, AttributeError):
                            st.session_state.sale_date = date.today()
                        st.session_state.sale_buyer = sale.buyer_name
                        st.session_state.sale_qty = sale.quantity
                        st.session_state.sale_rate = sale.rate
                        st.rerun()
                    
                    # Handle delete button click
                    if delete_clicked:
                        if st.session_state.get(f"confirm_del_sale_{sale.id}", False):
                            dm.delete_milk_sale(sale.id)
                            st.success("Sale deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_del_sale_{sale.id}"] = True
                            st.warning("Click again to confirm deletion")
                            st.rerun()
            else:
                st.info(f"No sales recorded for {st.session_state.sales_selected_date}")
            
            # Clear selection button
            if st.button("Clear Date Selection", key="clear_sales_date"):
                st.session_state.sales_selected_date = None
                st.rerun()
        else:
            st.info("Click on a date in the calendar above to view sales for that day.")

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

        # Payment History with Calendar View - Enhanced Interface
        st.subheader("Payment History")
        
        # Get all payments for calendar view
        all_payments = dm.get_payments()
        
        # Convert payments data to calendar format
        payments_calendar_data = []
        for payment in all_payments:
            payments_calendar_data.append({
                'date': payment.date,
                'buyer_name': payment.buyer_name,
                'entry_type': payment.entry_type,
                'amount': payment.amount,
                'notes': payment.notes or '',
                'id': payment.id
            })
        
        # Initialize payment calendar view state
        if 'payments_selected_date' not in st.session_state:
            st.session_state.payments_selected_date = None
        
        # Navigation controls for payment calendar
        payments_current_date = NavigationControls.render(key_prefix="payments_nav")
        
        # Payment calendar view
        payments_calendar_view = CalendarView()
        payments_calendar_result = payments_calendar_view.render(
            data_points=payments_calendar_data,
            selected_month=payments_current_date,
            calendar_key="payments_calendar"
        )
        
        # Handle date selection from calendar
        payments_selected_date = payments_calendar_view.get_selected_date_from_calendar(payments_calendar_result)
        if payments_selected_date:
            st.session_state.payments_selected_date = payments_selected_date
        
        # Display payments for selected date
        if st.session_state.payments_selected_date:
            st.subheader(f"Payments for {st.session_state.payments_selected_date}")
            
            # Filter payments for selected date
            selected_payments = [p for p in all_payments if p.date == st.session_state.payments_selected_date]
            
            if selected_payments:
                for i, payment in enumerate(selected_payments):
                    row_number = RowNumberFormatter.get_row_number(i)
                    
                    # Use EnhancedDataTable for proper formatting and button positioning
                    edit_clicked, delete_clicked = EnhancedDataTable.render_payment_row(
                        payment, row_number
                    )
                    
                    # Handle edit button click
                    if edit_clicked:
                        st.session_state.pay_edit_mode = True
                        st.session_state.pay_edit_id = payment.id
                        try:
                            st.session_state.pay_date = datetime.fromisoformat(payment.date).date()
                        except (ValueError, AttributeError):
                            st.session_state.pay_date = date.today()
                        st.session_state.pay_buyer = payment.buyer_name
                        st.session_state.pay_type = payment.entry_type
                        st.session_state.pay_amount = payment.amount
                        st.session_state.pay_notes = payment.notes or ""
                        st.rerun()
                    
                    # Handle delete button click
                    if delete_clicked:
                        if st.session_state.get(f"confirm_del_pay_{payment.id}", False):
                            dm.delete_payment(payment.id)
                            st.success("Payment deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_del_pay_{payment.id}"] = True
                            st.warning("Click again to confirm deletion")
                            st.rerun()
            else:
                st.info(f"No payments recorded for {st.session_state.payments_selected_date}")
            
            # Clear selection button
            if st.button("Clear Date Selection", key="clear_payments_date"):
                st.session_state.payments_selected_date = None
                st.rerun()
        else:
            st.info("Click on a date in the calendar above to view payments for that day.")

    with tab3:
        st.subheader("Buyer Ledgers")
        
        # Initialize buyer calendar state
        if 'selected_buyer_for_calendar' not in st.session_state:
            st.session_state.selected_buyer_for_calendar = None
        if 'buyer_calendar_view' not in st.session_state:
            st.session_state.buyer_calendar_view = False
        
        # Check if we should show buyer calendar view
        if st.session_state.buyer_calendar_view and st.session_state.selected_buyer_for_calendar:
            buyer_name = st.session_state.selected_buyer_for_calendar
            
            st.subheader(f"Calendar View for {buyer_name}")
            
            # Back button
            if st.button("← Back to Buyer List", key="back_to_buyers"):
                st.session_state.buyer_calendar_view = False
                st.session_state.selected_buyer_for_calendar = None
                st.rerun()
            
            # Get buyer's sales data
            buyer_sales = [s for s in all_sales if s.buyer_name == buyer_name]
            
            # Convert to calendar format
            buyer_calendar_data = []
            for sale in buyer_sales:
                buyer_calendar_data.append({
                    'date': sale.date,
                    'buyer_name': sale.buyer_name,
                    'quantity': sale.quantity,
                    'rate': sale.rate,
                    'total_amount': sale.total_amount,
                    'id': sale.id
                })
            
            # Navigation controls for buyer calendar
            buyer_current_date = NavigationControls.render(key_prefix=f"buyer_{buyer_name}_nav")
            
            # Buyer calendar view
            buyer_calendar_view = CalendarView()
            buyer_calendar_result = buyer_calendar_view.render(
                data_points=buyer_calendar_data,
                selected_month=buyer_current_date,
                calendar_key=f"buyer_{buyer_name}_calendar"
            )
            
            # Handle date selection from buyer calendar
            buyer_selected_date = buyer_calendar_view.get_selected_date_from_calendar(buyer_calendar_result)
            if buyer_selected_date:
                st.session_state[f'buyer_{buyer_name}_selected_date'] = buyer_selected_date
            
            # Display transactions for selected date
            selected_date_key = f'buyer_{buyer_name}_selected_date'
            if st.session_state.get(selected_date_key):
                selected_date = st.session_state[selected_date_key]
                st.subheader(f"Purchases by {buyer_name} on {selected_date}")
                
                # Filter sales for selected date and buyer
                selected_buyer_sales = [s for s in buyer_sales if s.date == selected_date]
                
                if selected_buyer_sales:
                    for i, sale in enumerate(selected_buyer_sales):
                        row_number = RowNumberFormatter.get_row_number(i)
                        
                        # Display sale details
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"**{sale.date}** | {sale.buyer_name}")
                                st.caption(f"Qty: {sale.quantity}L @ ₹{sale.rate}/L | Total: ₹{sale.total_amount}")
                            with col2:
                                st.write(f"#{row_number}")
                            st.divider()
                else:
                    st.info(f"No purchases by {buyer_name} on {selected_date}")
                
                # Clear selection button
                if st.button("Clear Date Selection", key=f"clear_buyer_{buyer_name}_date"):
                    if selected_date_key in st.session_state:
                        del st.session_state[selected_date_key]
                    st.rerun()
            else:
                st.info("Click on a date in the calendar above to view purchases for that day.")
            
            # Date range export functionality
            st.markdown("---")
            st.subheader("Export Purchase Data")
            DateRangeSelector.render_with_export(
                buyer=buyer_name,
                sales_data=buyer_sales,
                key_prefix=f"export_{buyer_name}"
            )
        
        else:
            # Regular ledger view with search functionality
            # Search interface for buyers
            buyer_names = [b.name for b in buyers]
            
            if buyer_names:
                st.subheader("Search and Select Buyer")
                
                # Search functionality
                search_result = SearchInterface.render_buyer_list_with_search(
                    buyers=buyer_names,
                    key_prefix="buyer_ledger_search"
                )
                
                if search_result:
                    st.session_state.selected_buyer_for_calendar = search_result
                    st.session_state.buyer_calendar_view = True
                    st.rerun()
            
            # Summary ledger table
            st.markdown("---")
            st.subheader("Buyer Balance Summary")
            summary_data = []
            all_sales = dm.get_milk_sales()
            all_payments = dm.get_payments()
            for i, b in enumerate(buyers):
                row_number = RowNumberFormatter.get_row_number(i)
                b_sales = [s for s in all_sales if s.buyer_name == b.name]
                b_payments = [p for p in all_payments if p.buyer_name == b.name]
                bal = sum(s.total_amount for s in b_sales) - sum(p.amount for p in b_payments)
                summary_data.append({
                    "#": row_number,
                    "Buyer": b.name, 
                    "Balance": f"₹{bal:.2f}"
                })
            
            if summary_data:
                st.dataframe(pd.DataFrame(summary_data), width='stretch', hide_index=True)
