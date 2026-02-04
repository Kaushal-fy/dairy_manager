import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import calendar as cal

class DropdownDateSelector:
    """Mobile-friendly dropdown-based date selector."""
    
    @staticmethod
    def render(data_points: List[Dict[str, Any]], key_prefix: str = "dropdown_date") -> Optional[str]:
        """Render three dropdowns for year, month, and date selection."""
        
        # Get available years from data
        available_years = set()
        current_year = date.today().year
        available_years.add(current_year)  # Always include current year
        
        for point in data_points:
            date_str = point.get('date', '')
            if date_str:
                try:
                    if isinstance(date_str, str):
                        parsed_date = datetime.fromisoformat(date_str).date()
                    else:
                        parsed_date = date_str
                    available_years.add(parsed_date.year)
                except:
                    continue
        
        # Sort years in descending order (most recent first)
        years_list = sorted(list(available_years), reverse=True)
        
        # Create three columns for the dropdowns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Year dropdown
            try:
                current_year_index = years_list.index(current_year)
            except ValueError:
                current_year_index = 0
            
            selected_year = st.selectbox(
                "Year",
                years_list,
                index=current_year_index,
                key=f"{key_prefix}_year"
            )
        
        with col2:
            # Month dropdown
            months = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            current_month = date.today().month
            
            selected_month_name = st.selectbox(
                "Month",
                months,
                index=current_month - 1,  # Convert to 0-based index
                key=f"{key_prefix}_month"
            )
            selected_month = months.index(selected_month_name) + 1  # Convert back to 1-based
        
        with col3:
            # Date dropdown - dynamically updated based on year and month
            # Get valid dates for the selected year and month
            try:
                days_in_month = cal.monthrange(selected_year, selected_month)[1]
                valid_dates = list(range(1, days_in_month + 1))
                
                # Get dates with data for the selected year and month
                dates_with_data = set()
                for point in data_points:
                    date_str = point.get('date', '')
                    if date_str:
                        try:
                            if isinstance(date_str, str):
                                parsed_date = datetime.fromisoformat(date_str).date()
                            else:
                                parsed_date = date_str
                            
                            if parsed_date.year == selected_year and parsed_date.month == selected_month:
                                dates_with_data.add(parsed_date.day)
                        except:
                            continue
                
                # Create date options with indicators for data
                date_options = []
                for day in valid_dates:
                    if day in dates_with_data:
                        date_options.append(f"🟢 {day}")
                    else:
                        date_options.append(str(day))
                
                # Default selection - try today's date if it's in the selected month
                default_index = 0
                today = date.today()
                if today.year == selected_year and today.month == selected_month:
                    try:
                        default_index = valid_dates.index(today.day)
                    except ValueError:
                        default_index = 0
                
                selected_date_option = st.selectbox(
                    "Date",
                    date_options,
                    index=default_index,
                    key=f"{key_prefix}_date_{selected_year}_{selected_month}"  # Include year/month in key for auto-refresh
                )
                
                # Extract the actual day number from the option
                selected_day = int(selected_date_option.replace("🟢 ", ""))
                
            except Exception as e:
                st.error(f"Error generating dates: {e}")
                return None
        
        # Create the selected date
        try:
            selected_date = date(selected_year, selected_month, selected_day)
            return selected_date.isoformat()
        except Exception as e:
            st.error(f"Invalid date selection: {e}")
            return None
    
    @staticmethod
    def get_selected_date_info(selected_date_str: str, data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get information about the selected date."""
        if not selected_date_str:
            return {}
        
        # Count data points for the selected date
        data_count = 0
        for point in data_points:
            if point.get('date') == selected_date_str:
                data_count += 1
        
        return {
            'date': selected_date_str,
            'has_data': data_count > 0,
            'data_count': data_count
        }