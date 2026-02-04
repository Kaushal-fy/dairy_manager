import streamlit as st
from streamlit_calendar import calendar
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import json

class CalendarView:
    """Interactive monthly calendar interface with visual indicators and date selection."""
    
    def __init__(self):
        self.custom_css = """
        <style>
        /* Modern calendar styling with circular green dots */
        .fc-daygrid-event-dot {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
            border-radius: 50% !important;
            width: 10px !important;
            height: 10px !important;
            margin: 0 auto !important;
            display: block !important;
        }
        .fc-event-dot {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
            border-radius: 50% !important;
            width: 10px !important;
            height: 10px !important;
        }
        /* Hide event titles and text */
        .fc-event-title {
            display: none !important;
        }
        .fc-event-main {
            display: none !important;
        }
        .fc-event-time {
            display: none !important;
        }
        .fc-list-event-title {
            display: none !important;
        }
        /* Modern calendar header */
        .fc-toolbar {
            margin-bottom: 1rem !important;
            padding: 0.5rem !important;
        }
        .fc-button {
            background-color: #007bff !important;
            border-color: #007bff !important;
            border-radius: 6px !important;
            font-size: 14px !important;
            padding: 0.375rem 0.75rem !important;
        }
        .fc-button:hover {
            background-color: #0056b3 !important;
            border-color: #0056b3 !important;
        }
        .fc-button:focus {
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25) !important;
        }
        /* Day cell styling */
        .fc-daygrid-day {
            border: 1px solid #e9ecef !important;
            cursor: pointer !important;
        }
        .fc-daygrid-day:hover {
            background-color: #f8f9fa !important;
        }
        .fc-daygrid-day-number {
            color: #495057 !important;
            font-weight: 500 !important;
        }
        /* Calendar title */
        .fc-toolbar-title {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: #212529 !important;
        }
        /* Today highlighting */
        .fc-day-today {
            background-color: #fff3cd !important;
        }
        .fc-day-today .fc-daygrid-day-number {
            background-color: #ffc107 !important;
            color: #212529 !important;
            border-radius: 50% !important;
            width: 24px !important;
            height: 24px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 2px auto !important;
        }
        </style>
        """
    
    def render(self, data_points: List[Dict[str, Any]], selected_month: Optional[datetime] = None, 
               calendar_key: str = "calendar") -> Dict[str, Any]:
        """Render calendar with data points as green dot indicators."""
        
        # Apply custom CSS for green dots
        st.markdown(self.custom_css, unsafe_allow_html=True)
        
        # Convert data points to calendar events
        events = self._convert_to_calendar_events(data_points)
        
        # Set initial date
        if selected_month is None:
            selected_month = datetime.now()
        
        # Calendar options
        calendar_options = {
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth"
            },
            "initialDate": selected_month.strftime("%Y-%m-%d"),
            "initialView": "dayGridMonth",
            "selectable": True,
            "selectMirror": True,
            "dayMaxEvents": False,
            "eventDisplay": "dot",
            "height": 600,
            "aspectRatio": 1.35,
            "eventColor": "#28a745",
            "eventBorderColor": "#28a745",
            "eventTextColor": "transparent",
            "displayEventTime": False,
            "displayEventEnd": False
        }
        
        # Render calendar
        calendar_result = calendar(
            events=events,
            options=calendar_options,
            custom_css=self.custom_css,
            key=calendar_key
        )
        
        return calendar_result
    
    def _convert_to_calendar_events(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert data points to calendar events with green dot styling."""
        events = []
        
        # Group data points by date to avoid duplicate events
        date_groups = {}
        for point in data_points:
            date_str = point.get('date', '')
            if date_str:
                if date_str not in date_groups:
                    date_groups[date_str] = []
                date_groups[date_str].append(point)
        
        # Create calendar events for each date with data
        for date_str, points in date_groups.items():
            try:
                # Ensure proper date format
                if isinstance(date_str, str):
                    # Try to parse the date string
                    try:
                        parsed_date = datetime.fromisoformat(date_str).date()
                    except:
                        # Fallback parsing
                        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    parsed_date = date_str
                
                event = {
                    "id": f"event_{date_str}",
                    "title": "",  # Remove record count text
                    "start": parsed_date.isoformat(),
                    "end": parsed_date.isoformat(),
                    "backgroundColor": "#28a745",
                    "borderColor": "#28a745",
                    "display": "dot",  # Use dot display for modern circular look
                    "classNames": ["modern-event"],
                    "extendedProps": {
                        "data_points": points,
                        "count": len(points)
                    }
                }
                events.append(event)
            except Exception as e:
                # Skip invalid dates
                continue
        
        return events
    
    def handle_date_click(self, calendar_result: Dict[str, Any], data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Handle date selection and return filtered data for that date."""
        if not calendar_result or 'dateClick' not in calendar_result:
            return []
        
        selected_date = calendar_result['dateClick']['date']
        if not selected_date:
            return []
        
        # Extract date part only (remove time)
        selected_date_str = selected_date.split('T')[0]
        
        # Filter data points for selected date
        filtered_data = []
        for point in data_points:
            point_date = point.get('date', '')
            if point_date == selected_date_str:
                filtered_data.append(point)
        
        return filtered_data
    
    def get_selected_date_from_calendar(self, calendar_result: Dict[str, Any]) -> Optional[str]:
        """Extract selected date from calendar result."""
        if not calendar_result:
            return None
        
        if 'dateClick' in calendar_result and calendar_result['dateClick']:
            date_str = calendar_result['dateClick']['date']
            return date_str.split('T')[0] if date_str else None
        
        return None
    
    @staticmethod
    def apply_custom_styling() -> str:
        """Return CSS for modern circular green dot indicators."""
        return """
        <style>
        .fc-daygrid-event-dot {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
            border-radius: 50% !important;
            width: 10px !important;
            height: 10px !important;
            margin: 0 auto !important;
            display: block !important;
        }
        .fc-event-dot {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
            border-radius: 50% !important;
            width: 10px !important;
            height: 10px !important;
        }
        .fc-event-title {
            display: none !important;
        }
        .fc-event-main {
            display: none !important;
        }
        </style>
        """