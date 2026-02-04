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
        
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button("◀", key=f"{key_prefix}_prev_month", help="Previous Month"):
                # Go to previous month
                if current_date.month == 1:
                    new_date = current_date.replace(year=current_date.year - 1, month=12)
                else:
                    new_date = current_date.replace(month=current_date.month - 1)
                st.session_state[f"{key_prefix}_current_date"] = new_date
                st.rerun()
        
        with col2:
            if st.button("Today", key=f"{key_prefix}_today", help="Go to Current Month"):
                st.session_state[f"{key_prefix}_current_date"] = datetime.now()
                st.rerun()
        
        with col3:
            # Display current month/year
            st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 5px;'>"
                       f"{current_date.strftime('%B %Y')}</div>", 
                       unsafe_allow_html=True)
        
        with col4:
            if st.button("▶", key=f"{key_prefix}_next_month", help="Next Month"):
                # Go to next month
                if current_date.month == 12:
                    new_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    new_date = current_date.replace(month=current_date.month + 1)
                st.session_state[f"{key_prefix}_current_date"] = new_date
                st.rerun()
        
        with col5:
            # Optional: Year selector
            years = list(range(2020, 2030))
            current_year_idx = years.index(current_date.year) if current_date.year in years else 0
            selected_year = st.selectbox("", years, index=current_year_idx, 
                                       key=f"{key_prefix}_year_select", label_visibility="collapsed")
            
            if selected_year != current_date.year:
                new_date = current_date.replace(year=selected_year)
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