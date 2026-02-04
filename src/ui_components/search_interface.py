import streamlit as st
from typing import List, Optional

class SearchInterface:
    """Buyer name search functionality with real-time filtering."""
    
    @staticmethod
    def render(buyers: List[str], placeholder: str = "Search buyer name...", 
               key_prefix: str = "search") -> Optional[str]:
        """Render search interface and return selected buyer or search query."""
        
        # Search input
        search_query = st.text_input(
            "Search Buyers",
            placeholder=placeholder,
            key=f"{key_prefix}_input",
            label_visibility="collapsed"
        )
        
        if not search_query:
            return None
        
        # Filter buyers based on search query
        filtered_buyers = SearchInterface.filter_buyers(search_query, buyers)
        
        if not filtered_buyers:
            st.info("No buyers found matching your search.")
            return search_query
        
        # Display filtered results
        st.write(f"Found {len(filtered_buyers)} buyer(s):")
        
        selected_buyer = None
        for buyer in filtered_buyers[:10]:  # Limit to top 10 results
            if st.button(buyer, key=f"{key_prefix}_buyer_{buyer}", width="stretch"):
                selected_buyer = buyer
                # Store selected buyer in session state
                st.session_state[f"{key_prefix}_selected_buyer"] = buyer
                st.rerun()
        
        return selected_buyer or st.session_state.get(f"{key_prefix}_selected_buyer")
    
    @staticmethod
    def filter_buyers(query: str, buyers: List[str]) -> List[str]:
        """Filter buyers based on search query."""
        if not query or not buyers:
            return buyers
        
        query_lower = query.lower().strip()
        
        # Filter buyers that contain the query (case-insensitive)
        filtered = [buyer for buyer in buyers if query_lower in buyer.lower()]
        
        # Sort by relevance (exact matches first, then starts with, then contains)
        exact_matches = [b for b in filtered if b.lower() == query_lower]
        starts_with = [b for b in filtered if b.lower().startswith(query_lower) and b not in exact_matches]
        contains = [b for b in filtered if b not in exact_matches and b not in starts_with]
        
        return exact_matches + starts_with + contains
    
    @staticmethod
    def handle_search_state(key_prefix: str = "search") -> str:
        """Get current search state."""
        return st.session_state.get(f"{key_prefix}_input", "")
    
    @staticmethod
    def clear_search_state(key_prefix: str = "search"):
        """Clear search state."""
        if f"{key_prefix}_input" in st.session_state:
            del st.session_state[f"{key_prefix}_input"]
        if f"{key_prefix}_selected_buyer" in st.session_state:
            del st.session_state[f"{key_prefix}_selected_buyer"]
    
    @staticmethod
    def render_buyer_list_with_search(buyers: List[str], on_buyer_click_callback=None, 
                                    key_prefix: str = "buyer_list") -> Optional[str]:
        """Render searchable buyer list with click callbacks."""
        
        if not buyers:
            st.info("No buyers available.")
            return None
        
        # Search functionality
        search_query = st.text_input(
            "🔍 Search buyers...",
            key=f"{key_prefix}_search",
            placeholder="Type buyer name to search"
        )
        
        # Filter buyers
        if search_query:
            filtered_buyers = SearchInterface.filter_buyers(search_query, buyers)
        else:
            filtered_buyers = buyers
        
        if not filtered_buyers:
            st.warning("No buyers match your search.")
            return None
        
        # Display results
        st.write(f"Showing {len(filtered_buyers)} buyer(s):")
        
        selected_buyer = None
        for i, buyer in enumerate(filtered_buyers):
            row_number = i + 1  # 1-based indexing
            
            col1, col2 = st.columns([1, 4])
            with col1:
                st.write(f"{row_number}.")
            with col2:
                if st.button(f"📊 {buyer}", key=f"{key_prefix}_select_{buyer}", 
                           width="stretch", help="Click to view buyer details"):
                    selected_buyer = buyer
                    if on_buyer_click_callback:
                        on_buyer_click_callback(buyer)
                    st.session_state[f"{key_prefix}_selected"] = buyer
        
        return selected_buyer