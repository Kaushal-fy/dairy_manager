import streamlit as st
from src.data_manager import DataManager
from src.ui_components import CalendarView, NavigationControls, SearchInterface, DateRangeSelector, RowNumberFormatter
import pandas as pd
from datetime import date, timedelta, datetime

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def render(dm: DataManager):
    st.header("Reports & Summaries")
    
    # Date Range Filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today().replace(day=1))
    with col2:
        end_date = st.date_input("End Date", value=date.today())
        
    start_str = start_date.isoformat()
    end_str = end_date.isoformat()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Daily Summary", "Monthly Summary", "Buyer Report", "Cow Report"])
    
    # 1. Daily Summary (Expenses vs Revenue) - Enhanced with Row Numbers
    with tab1:
        st.subheader("Daily Income vs Expense")
        all_sales = dm.get_milk_sales()
        all_expenses = dm.get_expenses()
        all_yields = dm.get_daily_yields()
        
        # Filter by date range
        sales_in_range = [s for s in all_sales if start_str <= s.date <= end_str]
        expenses_in_range = [e for e in all_expenses if start_str <= e.date <= end_str]
        yields_in_range = [y for y in all_yields if start_str <= y.date <= end_str]
        
        # Aggregate by Date
        daily_data = {}
        
        # Sales
        for s in sales_in_range:
            d = s.date
            if d not in daily_data: daily_data[d] = {"Date": d, "Milk Revenue": 0.0, "Expenses": 0.0, "Milk (L)": 0.0, "Production (L)": 0.0}
            daily_data[d]["Milk Revenue"] += s.total_amount
            daily_data[d]["Milk (L)"] += s.quantity
            
        # Expenses
        for e in expenses_in_range:
            d = e.date
            if d not in daily_data: daily_data[d] = {"Date": d, "Milk Revenue": 0.0, "Expenses": 0.0, "Milk (L)": 0.0, "Production (L)": 0.0}
            daily_data[d]["Expenses"] += e.amount
        
        # Daily Yields (Production)
        for y in yields_in_range:
            d = y.date
            if d not in daily_data: daily_data[d] = {"Date": d, "Milk Revenue": 0.0, "Expenses": 0.0, "Milk (L)": 0.0, "Production (L)": 0.0}
            daily_data[d]["Production (L)"] += y.quantity

        df_daily = pd.DataFrame(daily_data.values())
        if not df_daily.empty:
            df_daily = df_daily.sort_values(by="Date")
            df_daily["Net Profit"] = df_daily["Milk Revenue"] - df_daily["Expenses"]
            
            # Add row numbers (1-based) - Preserve existing functionality with enhancement
            df_daily = df_daily.reset_index(drop=True)
            df_daily.insert(0, "#", [RowNumberFormatter.get_row_number(i) for i in range(len(df_daily))])
            
            # Reorder columns
            cols = ["#", "Date", "Production (L)", "Milk (L)", "Milk Revenue", "Expenses", "Net Profit"]
            # Ensure cols exist
            cols = [c for c in cols if c in df_daily.columns]
            
            st.dataframe(df_daily[cols], width='stretch', hide_index=True)
            
            csv = convert_df(df_daily[cols])
            st.download_button(
                "Download Daily Summary CSV",
                csv,
                "daily_summary.csv",
                "text/csv",
                key='download-daily'
            )
        else:
            st.info("No data in range.")

    # 2. Enhanced Monthly Summary with Historical Data
    with tab2:
        st.subheader("Monthly Summary - Historical View")
        
        # Get all historical data (not just current date range)
        all_sales_hist = dm.get_milk_sales()
        all_expenses_hist = dm.get_expenses()
        all_yields_hist = dm.get_daily_yields()
        
        # Create comprehensive monthly data
        monthly_data = {}
        
        # Process all sales
        for s in all_sales_hist:
            try:
                sale_date = datetime.fromisoformat(s.date)
                month_key = sale_date.strftime("%Y-%m")
                month_display = sale_date.strftime("%B %Y")
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "Month": month_display,
                        "Milk Revenue": 0.0,
                        "Expenses": 0.0,
                        "Milk (L)": 0.0,
                        "Production (L)": 0.0,
                        "sort_key": month_key
                    }
                
                monthly_data[month_key]["Milk Revenue"] += s.total_amount
                monthly_data[month_key]["Milk (L)"] += s.quantity
            except:
                continue
        
        # Process all expenses
        for e in all_expenses_hist:
            try:
                expense_date = datetime.fromisoformat(e.date)
                month_key = expense_date.strftime("%Y-%m")
                month_display = expense_date.strftime("%B %Y")
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "Month": month_display,
                        "Milk Revenue": 0.0,
                        "Expenses": 0.0,
                        "Milk (L)": 0.0,
                        "Production (L)": 0.0,
                        "sort_key": month_key
                    }
                
                monthly_data[month_key]["Expenses"] += e.amount
            except:
                continue
        
        # Process all yields
        for y in all_yields_hist:
            try:
                yield_date = datetime.fromisoformat(y.date)
                month_key = yield_date.strftime("%Y-%m")
                month_display = yield_date.strftime("%B %Y")
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        "Month": month_display,
                        "Milk Revenue": 0.0,
                        "Expenses": 0.0,
                        "Milk (L)": 0.0,
                        "Production (L)": 0.0,
                        "sort_key": month_key
                    }
                
                monthly_data[month_key]["Production (L)"] += y.quantity
            except:
                continue
        
        if monthly_data:
            # Convert to DataFrame and sort by date (newest first)
            df_monthly_hist = pd.DataFrame(monthly_data.values())
            df_monthly_hist = df_monthly_hist.sort_values(by="sort_key", ascending=False)
            df_monthly_hist["Net Profit"] = df_monthly_hist["Milk Revenue"] - df_monthly_hist["Expenses"]
            
            # Add row numbers (1-based)
            df_monthly_hist = df_monthly_hist.reset_index(drop=True)
            df_monthly_hist.insert(0, "#", [RowNumberFormatter.get_row_number(i) for i in range(len(df_monthly_hist))])
            
            # Display columns in desired order
            display_cols = ["#", "Month", "Production (L)", "Milk (L)", "Milk Revenue", "Expenses", "Net Profit"]
            display_cols = [c for c in display_cols if c in df_monthly_hist.columns]
            
            st.dataframe(df_monthly_hist[display_cols], width='stretch', hide_index=True)
            
            # Download functionality
            csv_m = convert_df(df_monthly_hist[display_cols])
            st.download_button(
                "Download Historical Monthly Summary CSV",
                csv_m,
                "historical_monthly_summary.csv",
                "text/csv",
                key='download-monthly-hist'
            )
        else:
            st.info("No historical data available.")

    # 3. Enhanced Buyer Report with Calendar Logic
    with tab3:
        st.subheader("Buyer Report")
        
        # Initialize buyer report state
        if 'buyer_report_view_mode' not in st.session_state:
            st.session_state.buyer_report_view_mode = 'summary'  # 'summary' or 'calendar'
        if 'buyer_report_selected_buyer' not in st.session_state:
            st.session_state.buyer_report_selected_buyer = None
        
        # Get all buyers and sales data
        all_buyers = dm.get_buyers()
        all_sales_for_report = dm.get_milk_sales()
        
        if not all_buyers:
            st.info("No buyers available.")
        else:
            # Mode selection
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Summary View", key="buyer_report_summary", 
                           disabled=st.session_state.buyer_report_view_mode == 'summary'):
                    st.session_state.buyer_report_view_mode = 'summary'
                    st.session_state.buyer_report_selected_buyer = None
                    st.rerun()
            
            with col2:
                if st.button("📅 Calendar View", key="buyer_report_calendar",
                           disabled=st.session_state.buyer_report_view_mode == 'calendar'):
                    st.session_state.buyer_report_view_mode = 'calendar'
                    st.rerun()
            
            st.markdown("---")
            
            if st.session_state.buyer_report_view_mode == 'summary':
                # Summary view with date range filtering
                if sales_in_range:
                    df_sales = pd.DataFrame([s.__dict__ for s in sales_in_range])
                    buyer_summary = df_sales.groupby('buyer_name')[['quantity', 'total_amount']].sum().reset_index()
                    buyer_summary.columns = ['Buyer', 'Total Litres', 'Total Revenue']
                    
                    # Add row numbers (1-based)
                    buyer_summary = buyer_summary.reset_index(drop=True)
                    buyer_summary.insert(0, "#", [RowNumberFormatter.get_row_number(i) for i in range(len(buyer_summary))])
                    
                    st.dataframe(buyer_summary, width='stretch', hide_index=True)
                    
                    csv_b = convert_df(buyer_summary)
                    st.download_button(
                        "Download Buyer Report CSV",
                        csv_b,
                        "buyer_report.csv",
                        "text/csv",
                        key='download-buyer'
                    )
                else:
                    st.info("No sales in selected date range.")
            
            elif st.session_state.buyer_report_view_mode == 'calendar':
                # Calendar view - similar to Buyer Ledger
                if st.session_state.buyer_report_selected_buyer:
                    # Show calendar for selected buyer
                    buyer_name = st.session_state.buyer_report_selected_buyer
                    
                    st.subheader(f"Calendar View - {buyer_name}")
                    
                    # Back button
                    if st.button("← Back to Buyer Selection", key="back_to_buyer_selection"):
                        st.session_state.buyer_report_selected_buyer = None
                        st.rerun()
                    
                    # Get buyer's sales data
                    buyer_sales_report = [s for s in all_sales_for_report if s.buyer_name == buyer_name]
                    
                    # Convert to calendar format
                    buyer_calendar_data_report = []
                    for sale in buyer_sales_report:
                        buyer_calendar_data_report.append({
                            'date': sale.date,
                            'buyer_name': sale.buyer_name,
                            'quantity': sale.quantity,
                            'rate': sale.rate,
                            'total_amount': sale.total_amount,
                            'id': sale.id
                        })
                    
                    # Navigation controls
                    report_current_date = NavigationControls.render(key_prefix=f"buyer_report_{buyer_name}_nav")
                    
                    # Calendar view
                    report_calendar_view = CalendarView()
                    report_calendar_result = report_calendar_view.render(
                        data_points=buyer_calendar_data_report,
                        selected_month=report_current_date,
                        calendar_key=f"buyer_report_{buyer_name}_calendar"
                    )
                    
                    # Handle date selection
                    report_selected_date = report_calendar_view.get_selected_date_from_calendar(report_calendar_result)
                    if report_selected_date:
                        st.session_state[f'buyer_report_{buyer_name}_selected_date'] = report_selected_date
                    
                    # Display transactions for selected date
                    selected_date_key = f'buyer_report_{buyer_name}_selected_date'
                    if st.session_state.get(selected_date_key):
                        selected_date = st.session_state[selected_date_key]
                        st.subheader(f"Sales on {selected_date}")
                        
                        # Filter sales for selected date and buyer
                        selected_sales_report = [s for s in buyer_sales_report if s.date == selected_date]
                        
                        if selected_sales_report:
                            for i, sale in enumerate(selected_sales_report):
                                row_number = RowNumberFormatter.get_row_number(i)
                                
                                with st.container():
                                    col1, col2 = st.columns([4, 1])
                                    with col1:
                                        st.markdown(f"**{sale.date}** | {sale.buyer_name}")
                                        st.caption(f"Qty: {sale.quantity}L @ ₹{sale.rate}/L | Total: ₹{sale.total_amount}")
                                    with col2:
                                        st.write(f"#{row_number}")
                                    st.divider()
                        else:
                            st.info(f"No sales for {buyer_name} on {selected_date}")
                        
                        # Clear selection button
                        if st.button("Clear Date Selection", key=f"clear_buyer_report_{buyer_name}_date"):
                            if selected_date_key in st.session_state:
                                del st.session_state[selected_date_key]
                            st.rerun()
                    else:
                        st.info("Click on a date in the calendar above to view sales for that day.")
                    
                    # Export functionality
                    st.markdown("---")
                    st.subheader("Export Data")
                    DateRangeSelector.render_with_export(
                        buyer=buyer_name,
                        sales_data=buyer_sales_report,
                        key_prefix=f"buyer_report_export_{buyer_name}"
                    )
                
                else:
                    # Buyer selection with search
                    st.subheader("Select Buyer for Calendar View")
                    
                    buyer_names = [b.name for b in all_buyers]
                    
                    # Search functionality
                    search_result = SearchInterface.render_buyer_list_with_search(
                        buyers=buyer_names,
                        key_prefix="buyer_report_search"
                    )
                    
                    if search_result:
                        st.session_state.buyer_report_selected_buyer = search_result
                        st.rerun()

    # 4. Cow Report
    with tab4:
        st.subheader("Cow Production & Expenses in Range")
        # Need cow events (yield) and expenses linked to cows
        all_events = dm.get_cow_events()
        events_in_range = [e for e in all_events if start_str <= e.date <= end_str]
        expenses_linked = [e for e in expenses_in_range if e.cow_id]
        
        cow_stats = {} # cow_id -> {yield, expenses}
        
        # 1. Sum Yields
        for e in events_in_range:
            if e.event_type == 'Yield':
                try:
                    val_clean = e.value.lower().replace('l', '').replace('litres', '').strip()
                    val = float(val_clean)
                    
                    if e.cow_id not in cow_stats: cow_stats[e.cow_id] = {"Yield (L)": 0.0, "Direct Expenses": 0.0}
                    cow_stats[e.cow_id]["Yield (L)"] += val
                except:
                    pass 
        
        # 2. Sum Expenses linked to cows
        for e in expenses_linked:
            if e.cow_id not in cow_stats: cow_stats[e.cow_id] = {"Yield (L)": 0.0, "Direct Expenses": 0.0}
            cow_stats[e.cow_id]["Direct Expenses"] += e.amount
        
        if cow_stats:
            data = [{"Cow ID": k, **v} for k,v in cow_stats.items()]
            df_cows = pd.DataFrame(data)
            st.dataframe(df_cows, width='stretch')
            
            csv_c = convert_df(df_cows)
            st.download_button(
                "Download Cow Report CSV",
                csv_c,
                "cow_report.csv",
                "text/csv",
                key='download-cow'
            )
        else:
            st.info("No cow data in range.")
