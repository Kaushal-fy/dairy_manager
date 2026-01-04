from datetime import date
from typing import List, Optional, Literal
from dataclasses import dataclass, field

@dataclass
class Buyer:
    name: str
    default_rate: float
    id: Optional[str] = None

@dataclass
class Expense:
    date: str  # YYYY-MM-DD
    name: str
    description: str
    amount: float
    is_recurring: bool = False
    recurrence_type: Optional[str] = None  # 'monthly', 'yearly', 'custom'
    next_due_date: Optional[str] = None
    cow_id: Optional[str] = None
    id: Optional[str] = None

@dataclass
class MilkSale:
    date: str
    buyer_name: str
    quantity: float
    rate: float
    total_amount: float
    id: Optional[str] = None

@dataclass
class DailyYield:
    date: str
    quantity: float
    notes: str
    id: Optional[str] = None

@dataclass
class Payment:
    date: str
    buyer_name: str
    entry_type: Literal['Payment', 'Advance']
    amount: float
    notes: str
    id: Optional[str] = None

@dataclass
class Cow:
    name: str
    breed: str
    notes: str
    bought_date: Optional[str] = None
    bought_from: Optional[str] = None
    calf_birth_date: Optional[str] = None
    id: Optional[str] = None

@dataclass
class CowEvent:
    date: str
    cow_id: str
    event_type: Literal['Vaccination', 'Doctor', 'Yield', 'Other']
    value: str  # e.g., Yield amount, or Vaccine name
    cost: float = 0.0
    next_due_date: Optional[str] = None
    notes: str = ""
    id: Optional[str] = None
