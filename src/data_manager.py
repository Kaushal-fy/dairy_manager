from abc import ABC, abstractmethod
from typing import List, Dict, Any
import json
import os
import pandas as pd
from datetime import datetime
from src.models import Expense, Buyer, MilkSale, Payment, Cow, CowEvent, DailyYield

class DataManager(ABC):
    @abstractmethod
    def get_expenses(self) -> List[Expense]: pass
    @abstractmethod
    def add_expense(self, expense: Expense) -> None: pass
    @abstractmethod
    def update_expense(self, expense: Expense) -> None: pass
    @abstractmethod
    def delete_expense(self, expense_id: str) -> None: pass
    
    @abstractmethod
    def get_buyers(self) -> List[Buyer]: pass
    @abstractmethod
    def add_buyer(self, buyer: Buyer) -> None: pass
    @abstractmethod
    def update_buyer(self, buyer_name: str, new_rate: float) -> None: pass
    @abstractmethod
    def delete_buyer(self, buyer_name: str) -> None: pass

    @abstractmethod
    def get_milk_sales(self) -> List[MilkSale]: pass
    @abstractmethod
    def add_milk_sale(self, sale: MilkSale) -> None: pass
    @abstractmethod
    def update_milk_sale(self, sale: MilkSale) -> None: pass
    @abstractmethod
    def delete_milk_sale(self, sale_id: str) -> None: pass

    @abstractmethod
    def get_daily_yields(self) -> List[DailyYield]: pass
    @abstractmethod
    def add_daily_yield(self, yield_record: DailyYield) -> None: pass
    @abstractmethod
    def update_daily_yield(self, yield_record: DailyYield) -> None: pass
    @abstractmethod
    def delete_daily_yield(self, yield_id: str) -> None: pass

    @abstractmethod
    def get_payments(self) -> List[Payment]: pass
    @abstractmethod
    def add_payment(self, payment: Payment) -> None: pass

    @abstractmethod
    def get_cows(self) -> List[Cow]: pass
    @abstractmethod
    def add_cow(self, cow: Cow) -> None: pass
    @abstractmethod
    def update_cow(self, cow: Cow) -> None: pass
    @abstractmethod
    def delete_cow(self, cow_id: str) -> None: pass

    @abstractmethod
    def get_cow_events(self) -> List[CowEvent]: pass
    @abstractmethod
    def add_cow_event(self, event: CowEvent) -> None: pass
    @abstractmethod
    def update_cow_event(self, event: CowEvent) -> None: pass
    @abstractmethod
    def delete_cow_event(self, event_id: str) -> None: pass

class LocalJSONBackend(DataManager):
    def __init__(self, data_dir: str = "local_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.files = {
            "expenses": os.path.join(data_dir, "expenses.json"),
            "buyers": os.path.join(data_dir, "buyers.json"),
            "milk_sales": os.path.join(data_dir, "milk_sales.json"),
            "daily_yields": os.path.join(data_dir, "daily_yields.json"),
            "payments": os.path.join(data_dir, "payments.json"),
            "cows": os.path.join(data_dir, "cows.json"),
            "cow_events": os.path.join(data_dir, "cow_events.json"),
        }
        self._init_files()

    def _init_files(self):
        for fpath in self.files.values():
            if not os.path.exists(fpath):
                with open(fpath, 'w') as f:
                    json.dump([], f)

    def _read_json(self, key: str) -> List[Dict]:
        with open(self.files[key], 'r') as f:
            return json.load(f)

    def _write_json(self, key: str, data: List[Dict]):
        with open(self.files[key], 'w') as f:
            json.dump(data, f, indent=2)

    # Expenses
    def get_expenses(self) -> List[Expense]:
        data = self._read_json("expenses")
        return [Expense(**d) for d in data]

    def add_expense(self, expense: Expense) -> None:
        data = self._read_json("expenses")
        data.append(expense.__dict__)
        self._write_json("expenses", data)

    def update_expense(self, expense: Expense) -> None:
        data = self._read_json("expenses")
        for i, d in enumerate(data):
            if d.get('id') == expense.id:
                data[i] = expense.__dict__
                break
        self._write_json("expenses", data)

    def delete_expense(self, expense_id: str) -> None:
        data = self._read_json("expenses")
        data = [d for d in data if d.get('id') != expense_id]
        self._write_json("expenses", data)

    # Buyers
    def get_buyers(self) -> List[Buyer]:
        data = self._read_json("buyers")
        return [Buyer(**d) for d in data]

    def add_buyer(self, buyer: Buyer) -> None:
        data = self._read_json("buyers")
        if not any(b['name'] == buyer.name for b in data):
            data.append(buyer.__dict__)
            self._write_json("buyers", data)

    def update_buyer(self, buyer_name: str, new_rate: float) -> None:
        data = self._read_json("buyers")
        for b in data:
            if b['name'] == buyer_name:
                b['default_rate'] = new_rate
        self._write_json("buyers", data)
    
    def delete_buyer(self, buyer_name: str) -> None:
        data = self._read_json("buyers")
        data = [d for d in data if d.get('name') != buyer_name]
        self._write_json("buyers", data)

    # Milk Sales
    def get_milk_sales(self) -> List[MilkSale]:
        data = self._read_json("milk_sales")
        return [MilkSale(**d) for d in data]

    def add_milk_sale(self, sale: MilkSale) -> None:
        data = self._read_json("milk_sales")
        data.append(sale.__dict__)
        self._write_json("milk_sales", data)

    def update_milk_sale(self, sale: MilkSale) -> None:
        data = self._read_json("milk_sales")
        for i, d in enumerate(data):
            if d.get('id') == sale.id:
                data[i] = sale.__dict__
                break
        self._write_json("milk_sales", data)

    def delete_milk_sale(self, sale_id: str) -> None:
        data = self._read_json("milk_sales")
        data = [d for d in data if d.get('id') != sale_id]
        self._write_json("milk_sales", data)

    # Daily Yields
    def get_daily_yields(self) -> List[DailyYield]:
        data = self._read_json("daily_yields")
        return [DailyYield(**d) for d in data]

    def add_daily_yield(self, yield_record: DailyYield) -> None:
        data = self._read_json("daily_yields")
        data.append(yield_record.__dict__)
        self._write_json("daily_yields", data)

    def update_daily_yield(self, yield_record: DailyYield) -> None:
        data = self._read_json("daily_yields")
        for i, d in enumerate(data):
            if d.get('id') == yield_record.id:
                data[i] = yield_record.__dict__
                break
        self._write_json("daily_yields", data)

    def delete_daily_yield(self, yield_id: str) -> None:
        data = self._read_json("daily_yields")
        data = [d for d in data if d.get('id') != yield_id]
        self._write_json("daily_yields", data)

    # Payments
    def get_payments(self) -> List[Payment]:
        data = self._read_json("payments")
        return [Payment(**d) for d in data]

    def add_payment(self, payment: Payment) -> None:
        data = self._read_json("payments")
        data.append(payment.__dict__)
        self._write_json("payments", data)

    # Cows
    def get_cows(self) -> List[Cow]:
        data = self._read_json("cows")
        return [Cow(**d) for d in data]

    def add_cow(self, cow: Cow) -> None:
        data = self._read_json("cows")
        if not any(c['name'] == cow.name for c in data):
             data.append(cow.__dict__)
             self._write_json("cows", data)
    
    def update_cow(self, cow: Cow) -> None:
        data = self._read_json("cows")
        for i, c in enumerate(data):
            # Identifying by name/id since id is often name. 
            # If id is unique UUID, better. Here model uses 'id' which might be name.
            if c.get('id') == cow.id:
                 data[i] = cow.__dict__
                 break
        self._write_json("cows", data)

    def delete_cow(self, cow_id: str) -> None:
        data = self._read_json("cows")
        data = [c for c in data if c.get('id') != cow_id]
        self._write_json("cows", data)

    # Cow Events
    def get_cow_events(self) -> List[CowEvent]:
        data = self._read_json("cow_events")
        return [CowEvent(**d) for d in data]

    def add_cow_event(self, event: CowEvent) -> None:
        data = self._read_json("cow_events")
        data.append(event.__dict__)
        self._write_json("cow_events", data)

    def update_cow_event(self, event: CowEvent) -> None:
        data = self._read_json("cow_events")
        for i, d in enumerate(data):
            if d.get('id') == event.id:
                data[i] = event.__dict__
                break
        self._write_json("cow_events", data)

    def delete_cow_event(self, event_id: str) -> None:
        data = self._read_json("cow_events")
        data = [d for d in data if d.get('id') != event_id]
        self._write_json("cow_events", data)
