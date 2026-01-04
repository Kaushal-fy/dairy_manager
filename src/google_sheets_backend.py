from src.data_manager import DataManager
from src.models import Expense, Buyer, MilkSale, Payment, Cow, CowEvent, DailyYield
from typing import List, Dict, Any
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json

class GoogleSheetsBackend(DataManager):
    def __init__(self, credentials_info: Dict[str, Any], sheet_name: str = "DairyManagerDB"):
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.creds = Credentials.from_service_account_info(credentials_info, scopes=self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet_name = sheet_name
        self.spreadsheet = self._get_or_create_spreadsheet()
        
        # Initialize worksheets
        self.worksheets = {
            "expenses": self._get_or_create_worksheet("expenses", ["id", "date", "name", "description", "amount", "is_recurring", "recurrence_type", "next_due_date", "cow_id"]),
            "buyers": self._get_or_create_worksheet("buyers", ["id", "name", "default_rate"]),
            "milk_sales": self._get_or_create_worksheet("milk_sales", ["id", "date", "buyer_name", "quantity", "rate", "total_amount"]),
            "daily_yields": self._get_or_create_worksheet("daily_yields", ["id", "date", "quantity", "notes"]),
            "payments": self._get_or_create_worksheet("payments", ["id", "date", "buyer_name", "entry_type", "amount", "notes"]),
            "cows": self._get_or_create_worksheet("cows", ["id", "name", "breed", "notes", "bought_date", "bought_from", "calf_birth_date"]),
            "cow_events": self._get_or_create_worksheet("cow_events", ["id", "date", "cow_id", "event_type", "value", "cost", "next_due_date", "notes"])
        }

    def _get_or_create_spreadsheet(self):
        try:
            return self.client.open(self.sheet_name)
        except gspread.SpreadsheetNotFound:
            try:
                return self.client.create(self.sheet_name)
            except gspread.exceptions.APIError as e:
                # Catch 403 or other creation errors
                raise Exception(
                    f"Found credentials but failed to open or create sheet '{self.sheet_name}'. "
                    f"Error: {e}. "
                    "SOLUTION: Create a Google Sheet named 'DairyManagerDB' manually and share it with the Service Account email."
                )

    def _get_or_create_worksheet(self, title: str, headers: List[str]):
        try:
            ws = self.spreadsheet.worksheet(title)
        except gspread.WorksheetNotFound:
            ws = self.spreadsheet.add_worksheet(title=title, rows=1000, cols=20)
            ws.append_row(headers)
        return ws

    def _get_all_records(self, ws_name: str):
        return self.worksheets[ws_name].get_all_records()

    def _append_row(self, ws_name: str, data: Dict[str, Any], headers: List[str]):
        row = [data.get(h, "") for h in headers]
        processed_row = []
        for item in row:
            if isinstance(item, bool):
                processed_row.append(str(item))
            elif item is None:
                processed_row.append("")
            else:
                processed_row.append(item)
        self.worksheets[ws_name].append_row(processed_row)
    
    def _delete_row_by_id(self, ws_name: str, record_id: str):
        ws = self.worksheets[ws_name]
        try:
            cell = ws.find(record_id)
            if cell:
                ws.delete_rows(cell.row)
        except gspread.CellNotFound:
            pass

    def _update_row_by_id(self, ws_name: str, record_id: str, data: Dict[str, Any], headers: List[str]):
        ws = self.worksheets[ws_name]
        try:
            cell = ws.find(record_id)
            if cell:
                row = [data.get(h, "") for h in headers]
                processed_row = []
                for item in row:
                    if isinstance(item, bool):
                        processed_row.append(str(item))
                    elif item is None:
                        processed_row.append("")
                    else:
                        processed_row.append(item)
                
                cell_list = ws.range(cell.row, 1, cell.row, len(headers))
                for i, c in enumerate(cell_list):
                    c.value = processed_row[i]
                ws.update_cells(cell_list)

        except gspread.CellNotFound:
            pass

    # Expenses
    def get_expenses(self) -> List[Expense]:
        records = self._get_all_records("expenses")
        expenses = []
        for r in records:
            is_rec = str(r.get('is_recurring', '')).lower() == 'true'
            expenses.append(Expense(
                id=str(r.get('id', '')),
                date=r.get('date'),
                name=r.get('name'),
                description=r.get('description'),
                amount=float(r.get('amount', 0)),
                is_recurring=is_rec,
                recurrence_type=r.get('recurrence_type'),
                next_due_date=r.get('next_due_date'),
                cow_id=r.get('cow_id')
            ))
        return expenses

    def add_expense(self, expense: Expense) -> None:
        headers = ["id", "date", "name", "description", "amount", "is_recurring", "recurrence_type", "next_due_date", "cow_id"]
        self._append_row("expenses", expense.__dict__, headers)

    def update_expense(self, expense: Expense) -> None:
        headers = ["id", "date", "name", "description", "amount", "is_recurring", "recurrence_type", "next_due_date", "cow_id"]
        self._update_row_by_id("expenses", expense.id, expense.__dict__, headers)

    def delete_expense(self, expense_id: str) -> None:
        self._delete_row_by_id("expenses", expense_id)

    # Buyers
    def get_buyers(self) -> List[Buyer]:
        records = self._get_all_records("buyers")
        return [Buyer(
            id=str(r.get('id', '')),
            name=r.get('name'),
            default_rate=float(r.get('default_rate', 0))
        ) for r in records]

    def add_buyer(self, buyer: Buyer) -> None:
        headers = ["id", "name", "default_rate"]
        self._append_row("buyers", buyer.__dict__, headers)

    def update_buyer(self, buyer_name: str, new_rate: float) -> None:
        ws = self.worksheets["buyers"]
        cell = ws.find(buyer_name)
        if cell:
            ws.update_cell(cell.row, 3, new_rate)

    # Milk Sales
    def get_milk_sales(self) -> List[MilkSale]:
        records = self._get_all_records("milk_sales")
        return [MilkSale(
            id=str(r.get('id', '')),
            date=r.get('date'),
            buyer_name=r.get('buyer_name'),
            quantity=float(r.get('quantity', 0)),
            rate=float(r.get('rate', 0)),
            total_amount=float(r.get('total_amount', 0))
        ) for r in records]

    def add_milk_sale(self, sale: MilkSale) -> None:
        headers = ["id", "date", "buyer_name", "quantity", "rate", "total_amount"]
        self._append_row("milk_sales", sale.__dict__, headers)

    def update_milk_sale(self, sale: MilkSale) -> None:
        headers = ["id", "date", "buyer_name", "quantity", "rate", "total_amount"]
        self._update_row_by_id("milk_sales", sale.id, sale.__dict__, headers)

    def delete_milk_sale(self, sale_id: str) -> None:
        self._delete_row_by_id("milk_sales", sale_id)

    # Daily Yields
    def get_daily_yields(self) -> List[DailyYield]:
        records = self._get_all_records("daily_yields")
        return [DailyYield(
            id=str(r.get('id', '')),
            date=r.get('date'),
            quantity=float(r.get('quantity', 0)),
            notes=r.get('notes')
        ) for r in records]

    def add_daily_yield(self, yield_record: DailyYield) -> None:
        headers = ["id", "date", "quantity", "notes"]
        self._append_row("daily_yields", yield_record.__dict__, headers)

    def update_daily_yield(self, yield_record: DailyYield) -> None:
        headers = ["id", "date", "quantity", "notes"]
        self._update_row_by_id("daily_yields", yield_record.id, yield_record.__dict__, headers)

    def delete_daily_yield(self, yield_id: str) -> None:
        self._delete_row_by_id("daily_yields", yield_id)

    # Payments
    def get_payments(self) -> List[Payment]:
        records = self._get_all_records("payments")
        return [Payment(
            id=str(r.get('id', '')),
            date=r.get('date'),
            buyer_name=r.get('buyer_name'),
            entry_type=r.get('entry_type'),
            amount=float(r.get('amount', 0)),
            notes=r.get('notes')
        ) for r in records]

    def add_payment(self, payment: Payment) -> None:
        headers = ["id", "date", "buyer_name", "entry_type", "amount", "notes"]
        self._append_row("payments", payment.__dict__, headers)

    # Cows
    def get_cows(self) -> List[Cow]:
        records = self._get_all_records("cows")
        return [Cow(
            id=str(r.get('id', '')),
            name=r.get('name'),
            breed=r.get('breed'),
            notes=r.get('notes'),
            bought_date=r.get('bought_date'),
            bought_from=r.get('bought_from'),
            calf_birth_date=r.get('calf_birth_date')
        ) for r in records]

    def add_cow(self, cow: Cow) -> None:
        headers = ["id", "name", "breed", "notes", "bought_date", "bought_from", "calf_birth_date"]
        self._append_row("cows", cow.__dict__, headers)
    
    def update_cow(self, cow_id: str, data: Dict[str, Any]) -> None:
         pass

    # Cow Events
    def get_cow_events(self) -> List[CowEvent]:
        records = self._get_all_records("cow_events")
        return [CowEvent(
            id=str(r.get('id', '')),
            date=r.get('date'),
            cow_id=r.get('cow_id'),
            event_type=r.get('event_type'),
            value=r.get('value'),
            cost=float(r.get('cost', 0)) if r.get('cost') else 0.0,
            next_due_date=r.get('next_due_date'),
            notes=r.get('notes')
        ) for r in records]

    def add_cow_event(self, event: CowEvent) -> None:
        headers = ["id", "date", "cow_id", "event_type", "value", "cost", "next_due_date", "notes"]
        self._append_row("cow_events", event.__dict__, headers)
