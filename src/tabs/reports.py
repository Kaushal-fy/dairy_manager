import streamlit as st
from src.data_manager import DataManager
import pandas as pd
from datetime import date, timedelta

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
    
    # 1. Daily Summary (Expenses vs Revenue)
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
            
            # Reorder columns
            cols = ["Date", "Production (L)", "Milk (L)", "Milk Revenue", "Expenses", "Net Profit"]
            # Ensure cols exist
            cols = [c for c in cols if c in df_daily.columns]
            
            st.dataframe(df_daily[cols], use_container_width=True)
            
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

    # 2. Monthly Summary
    with tab2:
        st.subheader("Monthly Summary")
        if not df_daily.empty:
            df_daily['Month'] = pd.to_datetime(df_daily['Date']).dt.to_period('M').astype(str)
            df_monthly = df_daily.groupby('Month')[['Milk Revenue', 'Expenses', 'Milk (L)', 'Production (L)', 'Net Profit']].sum().reset_index()
            
            st.dataframe(df_monthly, use_container_width=True)
            
            csv_m = convert_df(df_monthly)
            st.download_button(
                "Download Monthly Summary CSV",
                csv_m,
                "monthly_summary.csv",
                "text/csv",
                key='download-monthly'
            )
        else:
            st.info("No data.")

    # 3. Buyer Report (Totals in range)
    with tab3:
        st.subheader("Buyer Sales in Range")
        if sales_in_range:
            df_sales = pd.DataFrame([s.__dict__ for s in sales_in_range])
            buyer_summary = df_sales.groupby('buyer_name')[['quantity', 'total_amount']].sum().reset_index()
            buyer_summary.columns = ['Buyer', 'Total Litres', 'Total Revenue']
            
            st.dataframe(buyer_summary, use_container_width=True)
            
            csv_b = convert_df(buyer_summary)
            st.download_button(
                "Download Buyer Report CSV",
                csv_b,
                "buyer_report.csv",
                "text/csv",
                key='download-buyer'
            )
        else:
            st.info("No sales in range.")

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
            st.dataframe(df_cows, use_container_width=True)
            
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
