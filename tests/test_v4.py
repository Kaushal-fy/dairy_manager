import unittest
import os
import shutil
from src.data_manager import LocalJSONBackend
from src.models import Expense, DailyYield

class TestUpdateDelete(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data_v4"
        self.dm = LocalJSONBackend(data_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_expense_crud(self):
        e = Expense(date="2023-11-01", name="Feed", description="Grain", amount=100.0)
        self.dm.add_expense(e)
        
        # Update
        e.amount = 150.0
        self.dm.update_expense(e)
        updated = self.dm.get_expenses()[0]
        self.assertEqual(updated.amount, 150.0)
        
        # Delete
        self.dm.delete_expense(e.id)
        self.assertEqual(len(self.dm.get_expenses()), 0)

    def test_daily_yield_crud(self):
        dy = DailyYield(date="2023-11-01", quantity=10.0, notes="Morning")
        self.dm.add_daily_yield(dy)
        
        # Update
        dy.quantity = 12.0
        self.dm.update_daily_yield(dy)
        updated = self.dm.get_daily_yields()[0]
        self.assertEqual(updated.quantity, 12.0)
        
        # Delete
        self.dm.delete_daily_yield(dy.id)
        self.assertEqual(len(self.dm.get_daily_yields()), 0)

if __name__ == '__main__':
    unittest.main()
