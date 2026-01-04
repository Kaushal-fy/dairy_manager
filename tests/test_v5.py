import unittest
import os
import shutil
from src.data_manager import LocalJSONBackend
from src.models import Buyer

class TestBuyerDelete(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data_v5"
        self.dm = LocalJSONBackend(data_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_delete_buyer(self):
        # Create buyer
        b = Buyer(name="TestBuyer", default_rate=50.0)
        self.dm.add_buyer(b)
        
        # Verify added
        self.assertEqual(len(self.dm.get_buyers()), 1)
        
        # Delete
        self.dm.delete_buyer("TestBuyer")
        
        # Verify deleted
        self.assertEqual(len(self.dm.get_buyers()), 0)

if __name__ == '__main__':
    unittest.main()
