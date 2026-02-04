import streamlit as st
from datetime import datetime, timedelta
from typing import Optional

class NavigationControls:
    """Month/year navigation controls for calendar views."""
    
    @staticmethod
    def render(current_date: Optional[datetime] = None, view_type: str = "calendar", 
               key_prefix: str = "nav") -> datetime:
        """Render navigation controls and return selected date."""
        
        if current_date is None:
            current_date = datetime.now()
        
        # Create a more compact navigation layout
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("◀ Prev", key=f"{key_prefix}_prev_month", help="Previous Month", use_container_width=True):
                # Go to previous month
                if current_date.month == 1:
                    new_date = current_date.replace(year=current_date.year - 1, month=12)
                else:
                    new_date = current_date.replace(month=current_date.month - 1)
                st.session_state[f"{key_prefix}_current_date"] = new_date
                st.rerun()
        
        with col2:
            # Display current month/year with today button
            col2a, col2b = st.columns([2, 1])
            with col2a:
                st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 8px; font-size: 16px;'>"
                           f"{current_date.strftime('%B %Y')}</div>", 
                           unsafe_allow_html=True)
            with col2b:
                if st.button("Today", key=f"{key_prefix}_today", help="Go to Current Month", use_container_width=True):
                    st.session_state[f"{key_prefix}_current_date"] = datetime.now()
                    st.rerun()
        
        with col3:
            if st.button("Next ▶", key=f"{key_prefix}_next_month", help="Next Month", use_container_width=True):
                # Go to next month
                if current_date.month == 12:
                    new_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    new_date = current_date.replace(month=current_date.month + 1)
                st.session_state[f"{key_prefix}_current_date"] = new_date
                st.rerun()
        
        # Get current date from session state or use provided date
        return st.session_state.get(f"{key_prefix}_current_date", current_date)
    
    @staticmethod
    def get_navigation_state(key_prefix: str = "nav") -> datetime:
        """Get current navigation state."""
        return st.session_state.get(f"{key_prefix}_current_date", datetime.now())
    
    @staticmethod
    def set_navigation_state(new_date: datetime, key_prefix: str = "nav"):
        """Set navigation state."""
        st.session_state[f"{key_prefix}_current_date"] = new_date
    
    @staticmethod
    def handle_month_change(direction: int, current_date: datetime) -> datetime:
        """Handle month change programmatically."""
        if direction > 0:  # Next month
            if current_date.month == 12:
                return current_date.replace(year=current_date.year + 1, month=1)
            else:
                return current_date.replace(month=current_date.month + 1)
        else:  # Previous month
            if current_date.month == 1:
                return current_date.replace(year=current_date.year - 1, month=12)
            else:
                return current_date.replace(month=current_date.month - 1)