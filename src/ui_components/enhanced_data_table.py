import streamlit as st
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

class EnhancedDataTable:
    """Enhanced table rendering with right-aligned action buttons and improved formatting."""
    
    @staticmethod
    def apply_global_button_styles():
        """Apply global CSS styles for consistent button positioning."""
        st.markdown("""
        <style>
        /* Global responsive button styling */
        .stButton > button {
            width: 100%;
            border-radius: 6px;
            border: 1px solid #ddd;
            background-color: #f8f9fa;
            color: #495057;
            font-size: 14px;
            padding: 0.25rem 0.5rem;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            background-color: #e9ecef;
            border-color: #adb5bd;
            transform: translateY(-1px);
        }
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Action button specific styling */
        .action-buttons {
            display: flex;
            gap: 0.5rem;
            justify-content: flex-end;
            align-items: center;
        }
        
        /* Mobile responsive adjustments */
        @media (max-width: 768px) {
            .stButton > button {
                font-size: 12px;
                padding: 0.2rem 0.4rem;
            }
            .action-buttons {
                gap: 0.25rem;
            }
        }
        
        /* Ensure buttons stay on right side */
        .element-container:has(.stButton) {
            display: flex;
            justify-content: flex-end;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_expense_row(expense, row_number: int) -> Tuple[bool, bool]:
        """Render expense row with right-aligned action buttons."""
        # Custom CSS for responsive button alignment
        st.markdown("""
        <style>
        .expense-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            width: 100%;
            margin-bottom: 1rem;
            padding: 0.5rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #fafafa;
        }
        .expense-content {
            flex: 1;
            min-width: 0;
        }
        .expense-actions {
            display: flex;
            gap: 0.5rem;
            margin-left: 1rem;
            flex-shrink: 0;
        }
        @media (max-width: 768px) {
            .expense-row {
                flex-direction: column;
                gap: 0.5rem;
            }
            .expense-actions {
                align-self: flex-end;
                margin-left: 0;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            col1, col2 = st.columns([5, 1], gap="small")
            
            with col1:
                # Single-line formatting: Date and Name on same line
                st.markdown(f"**{expense.date}** | {expense.name}")
                st.caption(f"₹{expense.amount} | {expense.description}")
                if expense.is_recurring:
                    st.caption(f"🔄 Recurring: {expense.recurrence_type} | Next: {expense.next_due_date or 'N/A'}")
            
            with col2:
                # Right-aligned action buttons with responsive design
                button_col1, button_col2 = st.columns(2)
                with button_col1:
                    edit_clicked = st.button("✏️", key=f"edit_exp_{expense.id}", help="Edit", use_container_width=True)
                with button_col2:
                    delete_clicked = st.button("🗑️", key=f"del_exp_{expense.id}", help="Delete", use_container_width=True)
            
            st.divider()
            return edit_clicked, delete_clicked
    
    @staticmethod
    def render_transaction_row(transaction, row_number: int, transaction_type: str = "sale") -> Tuple[bool, bool]:
        """Render transaction row with right-aligned action buttons."""
        # Custom CSS for responsive button alignment
        st.markdown("""
        <style>
        .transaction-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            width: 100%;
            margin-bottom: 1rem;
            padding: 0.5rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
        .transaction-content {
            flex: 1;
            min-width: 0;
        }
        .transaction-actions {
            display: flex;
            gap: 0.5rem;
            margin-left: 1rem;
            flex-shrink: 0;
        }
        @media (max-width: 768px) {
            .transaction-row {
                flex-direction: column;
                gap: 0.5rem;
            }
            .transaction-actions {
                align-self: flex-end;
                margin-left: 0;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            col1, col2 = st.columns([5, 1], gap="small")
            
            with col1:
                if transaction_type == "sale":
                    st.markdown(f"**{transaction.date}** | {transaction.buyer_name}")
                    st.caption(f"Qty: {transaction.quantity}L @ ₹{transaction.rate}/L | Total: ₹{transaction.total_amount}")
                elif transaction_type == "yield":
                    st.markdown(f"**{transaction.date}** | {transaction.quantity}L")
                    if hasattr(transaction, 'notes') and transaction.notes:
                        st.caption(f"Notes: {transaction.notes}")
            
            with col2:
                # Right-aligned action buttons with responsive design
                button_col1, button_col2 = st.columns(2)
                with button_col1:
                    edit_clicked = st.button("✏️", key=f"edit_{transaction_type}_{transaction.id}", help="Edit", use_container_width=True)
                with button_col2:
                    delete_clicked = st.button("🗑️", key=f"del_{transaction_type}_{transaction.id}", help="Delete", use_container_width=True)
            
            st.divider()
            return edit_clicked, delete_clicked
    
    @staticmethod
    def render_payment_row(payment, row_number: int) -> Tuple[bool, bool]:
        """Render payment row with right-aligned action buttons."""
        # Custom CSS for responsive button alignment
        st.markdown("""
        <style>
        .payment-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            width: 100%;
            margin-bottom: 1rem;
            padding: 0.5rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #f0f8ff;
        }
        .payment-content {
            flex: 1;
            min-width: 0;
        }
        .payment-actions {
            display: flex;
            gap: 0.5rem;
            margin-left: 1rem;
            flex-shrink: 0;
        }
        @media (max-width: 768px) {
            .payment-row {
                flex-direction: column;
                gap: 0.5rem;
            }
            .payment-actions {
                align-self: flex-end;
                margin-left: 0;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            col1, col2 = st.columns([5, 1], gap="small")
            
            with col1:
                st.markdown(f"**{payment.date}** | {payment.buyer_name}")
                st.caption(f"{payment.entry_type}: ₹{payment.amount}")
                if hasattr(payment, 'notes') and payment.notes:
                    st.caption(f"Notes: {payment.notes}")
            
            with col2:
                # Right-aligned action buttons with responsive design
                button_col1, button_col2 = st.columns(2)
                with button_col1:
                    edit_clicked = st.button("✏️", key=f"edit_pay_{payment.id}", help="Edit", use_container_width=True)
                with button_col2:
                    delete_clicked = st.button("🗑️", key=f"del_pay_{payment.id}", help="Delete", use_container_width=True)
            
            st.divider()
            return edit_clicked, delete_clicked
    
    @staticmethod
    def render_buyer_row(buyer, row_number: int) -> Tuple[bool, bool, bool]:
        """Render buyer row with right-aligned action buttons and clickable name."""
        # Custom CSS for responsive button alignment
        st.markdown("""
        <style>
        .buyer-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            width: 100%;
            margin-bottom: 1rem;
            padding: 0.5rem;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: #fff8dc;
        }
        .buyer-content {
            flex: 1;
            min-width: 0;
        }
        .buyer-actions {
            display: flex;
            gap: 0.5rem;
            margin-left: 1rem;
            flex-shrink: 0;
        }
        @media (max-width: 768px) {
            .buyer-row {
                flex-direction: column;
                gap: 0.5rem;
            }
            .buyer-actions {
                align-self: flex-end;
                margin-left: 0;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            col1, col2 = st.columns([5, 1], gap="small")
            
            with col1:
                # Clickable buyer name
                name_clicked = st.button(f"📊 {buyer.name}", key=f"buyer_name_{buyer.name}", 
                                       help="Click to view calendar", use_container_width=True)
                st.caption(f"Rate: ₹{buyer.default_rate}/L")
            
            with col2:
                # Right-aligned action buttons with responsive design
                button_col1, button_col2 = st.columns(2)
                with button_col1:
                    edit_clicked = st.button("✏️", key=f"edit_buyer_{buyer.name}", help="Edit", use_container_width=True)
                with button_col2:
                    delete_clicked = st.button("🗑️", key=f"del_buyer_{buyer.name}", help="Delete", use_container_width=True)
            
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