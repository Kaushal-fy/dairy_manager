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
        .fc-event {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
            border-radius: 50% !important;
            width: 8px !important;
            height: 8px !important;
            margin: 2px !important;
        }
        .fc-daygrid-event {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
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
            "dayMaxEvents": 3,
            "eventDisplay": "background",
            "height": 600
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
                    "title": f"{len(points)} record(s)",
                    "start": parsed_date.isoformat(),
                    "end": parsed_date.isoformat(),
                    "backgroundColor": "#28a745",
                    "borderColor": "#28a745",
                    "display": "background",
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
        """Return CSS for green dot indicators."""
        return """
        <style>
        .fc-event {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
        }
        .fc-daygrid-event {
            background-color: #28a745 !important;
            border-color: #28a745 !important;
            border-radius: 50% !important;
            width: 10px !important;
            height: 10px !important;
        }
        </style>
        """