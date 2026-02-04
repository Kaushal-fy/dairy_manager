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
        """Render calendar with data points as green dot indicators using native Streamlit."""
        
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
        
        # Days of week header
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        cols = st.columns(7)
        for i, day in enumerate(days):
            with cols[i]:
                st.markdown(f"**{day}**")
        
        # Calendar grid
        selected_date = None
        for week in cal_data:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.write("")  # Empty cell for days not in current month
                    else:
                        current_date = date(year, month, day)
                        
                        # Check if this date has data
                        has_data = current_date in dates_with_data
                        
                        # Create button with green dot indicator
                        if has_data:
                            button_text = f"🟢 {day}"
                            help_text = f"Click to view data for {current_date}"
                        else:
                            button_text = str(day)
                            help_text = f"No data for {current_date}"
                        
                        # Make button clickable
                        if st.button(button_text, key=f"{calendar_key}_{day}", help=help_text):
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