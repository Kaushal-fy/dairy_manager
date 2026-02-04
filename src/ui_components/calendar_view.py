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
        """Render single calendar with both visual indicators and clickable dates."""
        
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
        
        # Add CSS for better mobile layout
        st.markdown("""
        <style>
        .calendar-button button {
            width: 100% !important;
            min-height: 45px !important;
            font-size: 14px !important;
            border-radius: 8px !important;
            margin: 2px !important;
        }
        .calendar-button.has-data button {
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%) !important;
            border: 2px solid #4caf50 !important;
            color: #2e7d32 !important;
            font-weight: 600 !important;
        }
        .calendar-button.today button {
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%) !important;
            border: 2px solid #ff9800 !important;
            color: #e65100 !important;
            font-weight: 700 !important;
        }
        @media (max-width: 768px) {
            .calendar-button button {
                min-height: 40px !important;
                font-size: 12px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Days of week header
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        cols = st.columns(7)
        for i, day in enumerate(days):
            with cols[i]:
                st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 8px; background: #6c757d; color: white; border-radius: 6px; margin: 2px;'>{day}</div>", 
                           unsafe_allow_html=True)
        
        # Calendar grid with clickable buttons
        selected_date = None
        today = date.today()
        
        for week in cal_data:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.markdown("<div style='height: 45px;'></div>", unsafe_allow_html=True)
                    else:
                        current_date = date(year, month, day)
                        has_data = current_date in dates_with_data
                        is_today = current_date == today
                        
                        # Determine button styling
                        css_classes = ['calendar-button']
                        if has_data:
                            css_classes.append('has-data')
                            button_text = f"🟢 {day}"
                        else:
                            button_text = str(day)
                        
                        if is_today:
                            css_classes.append('today')
                        
                        # Create clickable button with styling
                        st.markdown(f'<div class="{" ".join(css_classes)}">', unsafe_allow_html=True)
                        if st.button(button_text, key=f"{calendar_key}_{day}", help=f"View data for {current_date}"):
                            selected_date = current_date.isoformat()
                        st.markdown('</div>', unsafe_allow_html=True)
        
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