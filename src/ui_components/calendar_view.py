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
        """Render modern calendar with CSS Grid layout that works on mobile."""
        
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
        
        # Modern CSS Grid Calendar
        calendar_css = """
        <style>
        .modern-calendar {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 4px;
            max-width: 100%;
            margin: 20px auto;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .calendar-header {
            background: #6c757d;
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
            font-size: 14px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        }
        
        .calendar-day {
            aspect-ratio: 1;
            min-height: 45px;
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 500;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
        }
        
        .calendar-day:hover {
            background: #e3f2fd;
            border-color: #2196f3;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .calendar-day.has-data {
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border-color: #4caf50;
            color: #2e7d32;
        }
        
        .calendar-day.has-data::after {
            content: '●';
            position: absolute;
            top: 4px;
            right: 6px;
            color: #4caf50;
            font-size: 12px;
        }
        
        .calendar-day.empty {
            background: transparent;
            border: none;
            cursor: default;
        }
        
        .calendar-day.today {
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%);
            border-color: #ff9800;
            color: #e65100;
            font-weight: 700;
        }
        
        @media (max-width: 768px) {
            .modern-calendar {
                gap: 2px;
                padding: 10px;
            }
            .calendar-header {
                padding: 8px 4px;
                font-size: 12px;
            }
            .calendar-day {
                min-height: 40px;
                font-size: 14px;
                border-width: 1px;
            }
            .calendar-day.has-data::after {
                font-size: 10px;
                top: 2px;
                right: 4px;
            }
        }
        
        @media (max-width: 480px) {
            .calendar-day {
                min-height: 35px;
                font-size: 12px;
            }
            .calendar-header {
                font-size: 10px;
                padding: 6px 2px;
            }
        }
        </style>
        """
        
        st.markdown(calendar_css, unsafe_allow_html=True)
        
        # Build calendar HTML
        calendar_html = '<div class="modern-calendar">'
        
        # Days of week headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for day in days:
            calendar_html += f'<div class="calendar-header">{day}</div>'
        
        # Calendar days
        today = date.today()
        selected_date = None
        
        # Store clickable days for Streamlit buttons
        clickable_days = []
        
        for week in cal_data:
            for day in week:
                if day == 0:
                    calendar_html += '<div class="calendar-day empty"></div>'
                else:
                    current_date = date(year, month, day)
                    has_data = current_date in dates_with_data
                    is_today = current_date == today
                    
                    classes = ['calendar-day']
                    if has_data:
                        classes.append('has-data')
                    if is_today:
                        classes.append('today')
                    
                    calendar_html += f'<div class="{" ".join(classes)}" onclick="selectDate(\'{current_date.isoformat()}\')">{day}</div>'
                    clickable_days.append((day, current_date, has_data))
        
        calendar_html += '</div>'
        
        # Display the calendar
        st.markdown(calendar_html, unsafe_allow_html=True)
        
        # Create invisible Streamlit buttons for functionality
        st.markdown('<div style="position: absolute; left: -9999px; opacity: 0;">', unsafe_allow_html=True)
        
        for day, current_date, has_data in clickable_days:
            button_text = f"{'🟢 ' if has_data else ''}{day}"
            if st.button(button_text, key=f"{calendar_key}_{day}"):
                selected_date = current_date.isoformat()
                # Store in session state for persistence
                st.session_state[f"{calendar_key}_selected"] = selected_date
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Check if we have a stored selection
        if f"{calendar_key}_selected" in st.session_state:
            selected_date = st.session_state[f"{calendar_key}_selected"]
            # Clear the selection after use
            del st.session_state[f"{calendar_key}_selected"]
        
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