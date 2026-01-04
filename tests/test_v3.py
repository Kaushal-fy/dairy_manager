import unittest
import os
import shutil
from src.data_manager import LocalJSONBackend
from src.models import DailyYield

class TestDailyYield(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data_v3"
        self.dm = LocalJSONBackend(data_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_daily_yield_crud(self):
        dy = DailyYield(date="2023-10-30", quantity=50.5, notes="Morning")
        self.dm.add_daily_yield(dy)
        
        yields = self.dm.get_daily_yields()
        self.assertEqual(len(yields), 1)
        self.assertEqual(yields[0].quantity, 50.5)
        self.assertEqual(yields[0].notes, "Morning")
        
        # Test appending logic (multiple entries per day)
        dy2 = DailyYield(date="2023-10-30", quantity=40.0, notes="Evening")
        self.dm.add_daily_yield(dy2)
        
        yields = self.dm.get_daily_yields()
        self.assertEqual(len(yields), 2)
        
        total_for_day = sum(y.quantity for y in yields if y.date == "2023-10-30")
        self.assertEqual(total_for_day, 90.5)

if __name__ == '__main__':
    unittest.main()
