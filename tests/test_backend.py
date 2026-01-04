import unittest
import os
import shutil
from src.data_manager import LocalJSONBackend
from src.models import Expense, Buyer, MilkSale, Payment, Cow, CowEvent

class TestLocalBackend(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data"
        self.dm = LocalJSONBackend(data_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_expenses(self):
        exp = Expense(date="2023-10-27", name="Test Feed", description="Bags", amount=500.0)
        self.dm.add_expense(exp)
        
        expenses = self.dm.get_expenses()
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].name, "Test Feed")
        self.assertEqual(expenses[0].amount, 500.0)

    def test_buyers_and_update(self):
        b = Buyer(name="John Doe", default_rate=45.0)
        self.dm.add_buyer(b)
        
        buyers = self.dm.get_buyers()
        self.assertEqual(len(buyers), 1)
        self.assertEqual(buyers[0].default_rate, 45.0)
        
        # Test Duplicate prevention
        self.dm.add_buyer(b)
        self.assertEqual(len(self.dm.get_buyers()), 1)
        
        # Test Update
        self.dm.update_buyer("John Doe", 50.0)
        updated = self.dm.get_buyers()[0]
        self.assertEqual(updated.default_rate, 50.0)

    def test_milk_sales(self):
        s = MilkSale(date="2023-10-27", buyer_name="John", quantity=10, rate=50, total_amount=500)
        self.dm.add_milk_sale(s)
        
        sales = self.dm.get_milk_sales()
        self.assertEqual(len(sales), 1)
        self.assertEqual(sales[0].total_amount, 500)

    def test_payments(self):
        p = Payment(date="2023-10-27", buyer_name="John", entry_type="Payment", amount=200, notes="Cash")
        self.dm.add_payment(p)
        
        payments = self.dm.get_payments()
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].amount, 200)

    def test_cows_and_events(self):
        c = Cow(name="Bessie", breed="Jersey", notes="Good cow")
        self.dm.add_cow(c)
        
        cows = self.dm.get_cows()
        self.assertEqual(len(cows), 1)
        
        evt = CowEvent(date="2023-10-27", cow_id="Bessie", event_type="Vaccination", value="FMD")
        self.dm.add_cow_event(evt)
        
        events = self.dm.get_cow_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].cow_id, "Bessie")

if __name__ == '__main__':
    unittest.main()
