import streamlit as st
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

class EnhancedDataTable:
    """Enhanced table rendering with right-aligned action buttons and improved formatting."""
    
    @staticmethod
    def render_expense_row(expense, row_number: int) -> Tuple[bool, bool]:
        """Render expense row with right-aligned action buttons."""
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Single-line formatting: Date and Name on same line
                st.markdown(f"**{expense.date}** | {expense.name}")
                st.caption(f"₹{expense.amount} | {expense.description}")
                if expense.is_recurring:
                    st.caption(f"🔄 Recurring: {expense.recurrence_type} | Next: {expense.next_due_date or 'N/A'}")
            
            with col2:
                # Right-aligned action buttons
                edit_clicked = st.button("✏️", key=f"edit_exp_{expense.id}", help="Edit")
                delete_clicked = st.button("🗑️", key=f"del_exp_{expense.id}", help="Delete")
            
            st.divider()
            return edit_clicked, delete_clicked
    
    @staticmethod
    def render_transaction_row(transaction, row_number: int, transaction_type: str = "sale") -> Tuple[bool, bool]:
        """Render transaction row with right-aligned action buttons."""
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if transaction_type == "sale":
                    st.markdown(f"**{transaction.date}** | {transaction.buyer_name}")
                    st.caption(f"Qty: {transaction.quantity}L @ ₹{transaction.rate}/L | Total: ₹{transaction.total_amount}")
                elif transaction_type == "yield":
                    st.markdown(f"**{transaction.date}** | {transaction.quantity}L")
                    if hasattr(transaction, 'notes') and transaction.notes:
                        st.caption(f"Notes: {transaction.notes}")
            
            with col2:
                # Right-aligned action buttons
                edit_clicked = st.button("✏️", key=f"edit_{transaction_type}_{transaction.id}", help="Edit")
                delete_clicked = st.button("🗑️", key=f"del_{transaction_type}_{transaction.id}", help="Delete")
            
            st.divider()
            return edit_clicked, delete_clicked
    
    @staticmethod
    def render_payment_row(payment, row_number: int) -> Tuple[bool, bool]:
        """Render payment row with right-aligned action buttons."""
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{payment.date}** | {payment.buyer_name}")
                st.caption(f"{payment.entry_type}: ₹{payment.amount}")
                if hasattr(payment, 'notes') and payment.notes:
                    st.caption(f"Notes: {payment.notes}")
            
            with col2:
                # Right-aligned action buttons
                edit_clicked = st.button("✏️", key=f"edit_pay_{payment.id}", help="Edit")
                delete_clicked = st.button("🗑️", key=f"del_pay_{payment.id}", help="Delete")
            
            st.divider()
            return edit_clicked, delete_clicked
    
    @staticmethod
    def render_buyer_row(buyer, row_number: int) -> Tuple[bool, bool, bool]:
        """Render buyer row with right-aligned action buttons and clickable name."""
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Clickable buyer name
                name_clicked = st.button(f"**{buyer.name}**", key=f"buyer_name_{buyer.name}", 
                                       help="Click to view calendar", use_container_width=True)
                st.caption(f"Rate: ₹{buyer.default_rate}/L")
            
            with col2:
                # Right-aligned action buttons
                edit_clicked = st.button("✏️", key=f"edit_buyer_{buyer.name}", help="Edit")
                delete_clicked = st.button("🗑️", key=f"del_buyer_{buyer.name}", help="Delete")
            
            st.divider()
            return edit_clicked, delete_clicked, name_clicked
    
    @staticmethod
    def format_single_line(data: Dict[str, Any]) -> str:
        """Format data for single-line display."""
        if not data:
            return ""
        
        # Extract key information for single line display
        parts = []
        if 'date' in data:
            parts.append(f"**{data['date']}**")
        if 'name' in data:
            parts.append(data['name'])
        elif 'buyer_name' in data:
            parts.append(data['buyer_name'])
        
        return " | ".join(parts)
    
    @staticmethod
    def get_row_number(index: int) -> int:
        """Convert 0-based index to 1-based row number."""
        return index + 1