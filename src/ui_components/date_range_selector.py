import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Optional, Tuple, List, Dict, Any
import io

class DateRangeSelector:
    """Date range selection functionality for buyer-specific data analysis and export."""
    
    @staticmethod
    def render(min_date: Optional[date] = None, max_date: Optional[date] = None, 
               key_prefix: str = "date_range") -> Tuple[Optional[date], Optional[date]]:
        """Render date range selector and return selected dates."""
        
        if min_date is None:
            min_date = date.today() - timedelta(days=365)  # Default to 1 year ago
        if max_date is None:
            max_date = date.today()
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key=f"{key_prefix}_start"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=max_date,
                min_value=start_date if start_date else min_date,
                max_value=max_date,
                key=f"{key_prefix}_end"
            )
        
        # Validate range
        if start_date and end_date and start_date > end_date:
            st.error("Start date must be before or equal to end date.")
            return None, None
        
        return start_date, end_date
    
    @staticmethod
    def validate_range(start: Optional[date], end: Optional[date]) -> bool:
        """Validate date range."""
        if not start or not end:
            return False
        return start <= end
    
    @staticmethod
    def prepare_export_data(buyer: str, sales_data: List[Dict[str, Any]], 
                          start_date: date, end_date: date) -> Dict[str, Any]:
        """Prepare export data for buyer within date range."""
        
        # Filter data for buyer and date range
        filtered_data = []
        total_quantity = 0.0
        total_amount = 0.0
        
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        for sale in sales_data:
            # Check if sale is for this buyer and within date range
            if (hasattr(sale, 'buyer_name') and sale.buyer_name == buyer and
                start_str <= sale.date <= end_str):
                
                sale_dict = {
                    'Date': sale.date,
                    'Buyer': sale.buyer_name,
                    'Quantity (L)': sale.quantity,
                    'Rate (₹/L)': sale.rate,
                    'Total Amount (₹)': sale.total_amount
                }
                filtered_data.append(sale_dict)
                total_quantity += sale.quantity
                total_amount += sale.total_amount
        
        return {
            'buyer_name': buyer,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'purchase_records': filtered_data,
            'total_quantity': total_quantity,
            'total_amount': total_amount,
            'record_count': len(filtered_data)
        }
    
    @staticmethod
    def generate_csv_download(export_data: Dict[str, Any], key_prefix: str = "export") -> None:
        """Generate CSV download button for export data."""
        
        if not export_data['purchase_records']:
            st.info("No data available for the selected date range.")
            return
        
        # Create DataFrame
        df = pd.DataFrame(export_data['purchase_records'])
        
        # Add summary row
        summary_row = {
            'Date': 'TOTAL',
            'Buyer': export_data['buyer_name'],
            'Quantity (L)': export_data['total_quantity'],
            'Rate (₹/L)': '',
            'Total Amount (₹)': export_data['total_amount']
        }
        df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", export_data['record_count'])
        with col2:
            st.metric("Total Quantity", f"{export_data['total_quantity']:.1f} L")
        with col3:
            st.metric("Total Amount", f"₹{export_data['total_amount']:.2f}")
        
        # Download button
        filename = f"{export_data['buyer_name']}_{export_data['start_date']}_to_{export_data['end_date']}.csv"
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            key=f"{key_prefix}_download",
            use_container_width=True
        )
    
    @staticmethod
    def render_with_export(buyer: str, sales_data: List[Dict[str, Any]], 
                          key_prefix: str = "buyer_export") -> None:
        """Render date range selector with export functionality for specific buyer."""
        
        st.subheader(f"Export Data for {buyer}")
        
        # Date range selection
        start_date, end_date = DateRangeSelector.render(key_prefix=key_prefix)
        
        if not DateRangeSelector.validate_range(start_date, end_date):
            st.warning("Please select a valid date range.")
            return
        
        # Prepare and display export data
        export_data = DateRangeSelector.prepare_export_data(buyer, sales_data, start_date, end_date)
        
        if export_data['record_count'] > 0:
            # Show preview of data
            with st.expander("Preview Data", expanded=False):
                df_preview = pd.DataFrame(export_data['purchase_records'])
                st.dataframe(df_preview, use_container_width=True)
            
            # Generate download
            DateRangeSelector.generate_csv_download(export_data, key_prefix)
        else:
            st.info(f"No sales records found for {buyer} between {start_date} and {end_date}.")
    
    @staticmethod
    def filter_data_by_range(data: List[Dict[str, Any]], start_date: date, end_date: date, 
                           date_field: str = 'date') -> List[Dict[str, Any]]:
        """Filter data by date range."""
        if not data or not start_date or not end_date:
            return data
        
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        
        filtered = []
        for item in data:
            item_date = item.get(date_field, '')
            if start_str <= item_date <= end_str:
                filtered.append(item)
        
        return filtered