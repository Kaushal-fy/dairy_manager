import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import calendar as cal

class CalendarView:
    """Interactive monthly calendar interface with visual indicators and date selection."""
    
    def __init__(self):
        pass
    
    def render(self, data_points: List[Dict[str, Any]], selected_month: Optional[datetime] = None, 
               calendar_key: str = "calendar") -> Dict[str, Any]:
        """Render calendar using HTML table approach for better mobile compatibility."""
        
        if selected_month is None:
            selected_month = datetime.now()
        
        # Get dates with data
        dates_with_data = set()
        for point in data_points:
            date_str = point.get('date', '')
            if date_str:
                try:
                    if isinstance(date_str, str):
                        parsed_date = datetime.fromisoformat(date_str).date()
                    else:
                        parsed_date = date_str
                    dates_with_data.add(parsed_date)
                except:
                    continue
        
        # Create calendar grid
        year = selected_month.year
        month = selected_month.month
        
        # Get calendar data
        cal_data = cal.monthcalendar(year, month)
        
        # Calendar header
        st.markdown(f"### {selected_month.strftime('%B %Y')}")
        
        # Create HTML table structure
        st.markdown("""
        <style>
        .calendar-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-family: Arial, sans-serif;
        }
        .calendar-table th {
            background: #6c757d;
            color: white;
            padding: 10px 5px;
            text-align: center;
            font-weight: 600;
            font-size: 14px;
        }
        .calendar-table td {
            width: 14.28%;
            height: 60px;
            padding: 2px;
            text-align: center;
            vertical-align: middle;
            border: 1px solid #ddd;
        }
        @media (max-width: 768px) {
            .calendar-table td {
                height: 50px;
                padding: 1px;
            }
            .calendar-table th {
                padding: 8px 3px;
                font-size: 12px;
            }
        }
        @media (max-width: 480px) {
            .calendar-table td {
                height: 45px;
            }
            .calendar-table th {
                font-size: 10px;
                padding: 6px 2px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create table header
        table_html = '<table class="calendar-table">'
        table_html += '<tr>'
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for day in days:
            table_html += f'<th>{day}</th>'
        table_html += '</tr>'
        
        # Create table rows for weeks
        for week_idx, week in enumerate(cal_data):
            table_html += '<tr>'
            for day_idx, day in enumerate(week):
                if day == 0:
                    table_html += '<td></td>'
                else:
                    table_html += f'<td id="cell_{week_idx}_{day_idx}"></td>'
            table_html += '</tr>'
        
        table_html += '</table>'
        
        # Display the table
        st.markdown(table_html, unsafe_allow_html=True)
        
        # Now create buttons for each day using Streamlit columns but in a more controlled way
        selected_date = None
        today = date.today()
        
        st.markdown("**Calendar Days:**")
        
        for week_idx, week in enumerate(cal_data):
            # Create a container for each week
            with st.container():
                cols = st.columns(7)
                for day_idx, day in enumerate(week):
                    with cols[day_idx]:
                        if day == 0:
                            st.write("")  # Empty space
                        else:
                            current_date = date(year, month, day)
                            has_data = current_date in dates_with_data
                            is_today = current_date == today
                            
                            # Create button text and styling
                            if has_data:
                                button_text = f"🟢{day}"
                                button_type = "primary" if is_today else "secondary"
                            else:
                                button_text = str(day)
                                button_type = "primary" if is_today else None
                            
                            # Create the button
                            if st.button(
                                button_text, 
                                key=f"{calendar_key}_{week_idx}_{day_idx}_{day}",
                                help=f"View data for {current_date}",
                                type=button_type
                            ):
                                selected_date = current_date.isoformat()
        
        # Return result in expected format
        result = {}
        if selected_date:
            result['dateClick'] = {'date': selected_date}
        
        return result
    
    def get_selected_date_from_calendar(self, calendar_result: Dict[str, Any]) -> Optional[str]:
        """Extract selected date from calendar result."""
        if not calendar_result:
            return None
        
        if 'dateClick' in calendar_result and calendar_result['dateClick']:
            date_str = calendar_result['dateClick']['date']
            return date_str.split('T')[0] if date_str else None
        
        return None