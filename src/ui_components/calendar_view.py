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
        """Render simple mobile-friendly calendar as a list of dates."""
        
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
        
        # Simple approach: Show dates with data first, then all dates
        selected_date = None
        
        # Show dates with data prominently
        dates_with_data_list = sorted([d for d in dates_with_data if d.year == year and d.month == month])
        
        if dates_with_data_list:
            st.markdown("**📅 Dates with Data:**")
            cols = st.columns(min(4, len(dates_with_data_list)))
            for i, date_obj in enumerate(dates_with_data_list):
                col_idx = i % len(cols)
                with cols[col_idx]:
                    if st.button(
                        f"🟢 {date_obj.day}",
                        key=f"{calendar_key}_data_{date_obj.day}",
                        help=f"View data for {date_obj.strftime('%B %d, %Y')}"
                    ):
                        selected_date = date_obj.isoformat()
        
        # Show all dates in a simple grid
        st.markdown("**📆 All Dates:**")
        
        # Create a simple date picker as primary interface
        default_date = date(year, month, 1)
        selected_date_picker = st.date_input(
            "Select any date:",
            value=default_date,
            min_value=date(year, month, 1),
            max_value=date(year, month, cal.monthrange(year, month)[1]),
            key=f"{calendar_key}_picker"
        )
        
        # Use date picker if no button was clicked
        if not selected_date and selected_date_picker:
            selected_date = selected_date_picker.isoformat()
        
        # Show a simple visual calendar for reference (non-interactive)
        st.markdown("**Calendar View:**")
        calendar_display = ""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        calendar_display += " | ".join([f"**{day}**" for day in days]) + "\n"
        calendar_display += "|" + "---|" * 7 + "\n"
        
        for week in cal_data:
            week_display = []
            for day in week:
                if day == 0:
                    week_display.append(" ")
                else:
                    current_date = date(year, month, day)
                    if current_date in dates_with_data:
                        week_display.append(f"🟢**{day}**")
                    else:
                        week_display.append(str(day))
            calendar_display += " | ".join(week_display) + "\n"
        
        st.markdown(calendar_display)
        
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