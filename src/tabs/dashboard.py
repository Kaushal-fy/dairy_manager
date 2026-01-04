import streamlit as st
from src.data_manager import DataManager
import pandas as pd
from datetime import date, datetime, timedelta
import calendar

def render(dm: DataManager):
    st.header("Dashboard")
    
    today = date.today()
    current_month_start = date(today.year, today.month, 1)
    
    # --- Data Fetching ---
    all_expenses = dm.get_expenses()
    all_sales = dm.get_milk_sales()
    all_events = dm.get_cow_events()
    all_yields = dm.get_daily_yields()
    
    # --- Date Filtering Helpers ---
    def is_current_month(d_str):
        try:
            d = date.fromisoformat(d_str)
            return d.year == today.year and d.month == today.month
        except: return False

    def is_current_year(d_str):
        try:
            d = date.fromisoformat(d_str)
            return d.year == today.year
        except: return False

    # --- Section 1: Current Month Metrics ---
    st.subheader(f"Current Month Overview ({today.strftime('%B %Y')})")
    
    # 1. OPEX
    month_expenses = [e for e in all_expenses if is_current_month(e.date)]
    total_opex = sum(e.amount for e in month_expenses)
    
    # 2. Milk Produced
    month_yield_events = [e for e in all_events if is_current_month(e.date) and e.event_type == 'Yield']
    total_produced_cow = 0.0
    for e in month_yield_events:
        try:
            val_clean = e.value.lower().replace('l', '').replace('litres', '').strip()
            total_produced_cow += float(val_clean)
        except: pass
    
    month_daily_yields = [y for y in all_yields if is_current_month(y.date)]
    total_produced_daily = sum(y.quantity for y in month_daily_yields)
    total_produced_month = total_produced_cow + total_produced_daily
        
    # 3. Milk Sold
    month_sales = [s for s in all_sales if is_current_month(s.date)]
    total_sold_month = sum(s.quantity for s in month_sales)
    total_revenue_month = sum(s.total_amount for s in month_sales)
    
    # 4. Avg Rate (Revenue / Quantity) - Original "Avg Rate/L"
    avg_rate_month = (total_revenue_month / total_sold_month) if total_sold_month > 0 else 0.0
    
    # 5. NEW: User asked for "Cost of Money sold that day/ Total milk sold in that day"
    # Interpreted as Average Realized Rate for the Month (Revenue / Quantity)
    # The previous "Avg Rev/Day" (Revenue / Days) was incorrect per user.
    # So we replace it with "Avg Realized Rate" (which might be redundant with Avg Rate/L, but satisfies the formula request).
    # Actually, let's keep Avg Rate/L (it is exactly Revenue/Quantity).
    # And maybe the user thought "Avg Rev/Day" was "Avg Rate"?
    # I will replace "Avg Rev/Day" with "Daily Avg Sales (₹)" = Total Revenue / Days, 
    # BUT user said "The value ... is incorrect. It should be Cost of Money sold / Total milk sold".
    # This implies they want the RATE.
    # So I will display the Rate clearly.
    
    # Let's display:
    # 1. Month Revenue (Total)
    # 2. Avg Price/L (Realized) -> Total Rev / Total Sold
    
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row1_col1.metric("Month OPEX", f"₹{total_opex:,.0f}")
    row1_col2.metric("Milk Produced", f"{total_produced_month:.1f} L")
    row1_col3.metric("Milk Sold", f"{total_sold_month:.1f} L")
    
    row2_col1, row2_col2 = st.columns(2)
    # Total Revenue for context
    row2_col1.metric("Month Revenue", f"₹{total_revenue_month:,.0f}")
    # The requested metric: Cost / Total Milk
    row2_col2.metric("Avg Realized Rate", f"₹{avg_rate_month:.2f} / L")
    
    st.divider()

    # --- Section 2: Year To Date (YTD) ---
    st.subheader("Year to Date (YTD)")
    
    ytd_expenses = [e for e in all_expenses if is_current_year(e.date)]
    ytd_opex = sum(e.amount for e in ytd_expenses)
    
    ytd_sales = [s for s in all_sales if is_current_year(s.date)]
    ytd_revenue = sum(s.total_amount for s in ytd_sales)
    
    net_profit = ytd_revenue - ytd_opex
    
    ytd_c1, ytd_c2, ytd_c3 = st.columns(3)
    ytd_c1.metric("YTD OPEX", f"₹{ytd_opex:,.0f}")
    ytd_c2.metric("YTD Revenue", f"₹{ytd_revenue:,.0f}")
    ytd_c3.metric("Net Profit / Loss", f"₹{net_profit:,.0f}", delta=f"{net_profit:,.0f}", delta_color="normal") 

    st.divider()
    
    # --- Notifications ---
    st.caption("Notifications")
    notifications = []
    
    today_iso = today.isoformat()
    for exp in all_expenses:
        if exp.is_recurring and exp.next_due_date:
            if today_iso >= exp.next_due_date:
                notifications.append(f"Expense '{exp.name}' due on {exp.next_due_date}")

    for event in all_events:
        if event.next_due_date:
            if today_iso >= event.next_due_date:
                notifications.append(f"Cow {event.cow_id}: {event.event_type} due on {event.next_due_date}")
    
    if notifications:
        for n in notifications:
            st.warning(n)
    else:
        st.success("No pending notifications.")
