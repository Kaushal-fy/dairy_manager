from typing import List, Any

class RowNumberFormatter:
    """Consistent row numbering logic starting from 1 across the entire application."""
    
    @staticmethod
    def get_row_number(index: int) -> int:
        """Convert 0-based index to 1-based row number."""
        return index + 1
    
    @staticmethod
    def format_row_with_number(index: int, content: str) -> str:
        """Format content with 1-based row number prefix."""
        row_num = RowNumberFormatter.get_row_number(index)
        return f"{row_num}. {content}"
    
    @staticmethod
    def add_row_numbers_to_list(items: List[Any]) -> List[tuple]:
        """Add 1-based row numbers to a list of items."""
        return [(RowNumberFormatter.get_row_number(i), item) for i, item in enumerate(items)]
    
    @staticmethod
    def validate_row_numbering(items: List[tuple]) -> bool:
        """Validate that row numbering starts from 1 and is sequential."""
        if not items:
            return True
        
        for i, (row_num, _) in enumerate(items):
            expected_row_num = i + 1
            if row_num != expected_row_num:
                return False
        
        return True
    
    @staticmethod
    def get_display_range(total_items: int, page_size: int = 50, page: int = 1) -> tuple:
        """Get display range for paginated data with 1-based numbering."""
        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_items)
        
        start_row_num = RowNumberFormatter.get_row_number(start_index)
        end_row_num = RowNumberFormatter.get_row_number(end_index - 1) if end_index > start_index else start_row_num
        
        return start_row_num, end_row_num, start_index, end_index