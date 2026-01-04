import unittest
import os
import shutil
from src.data_manager import LocalJSONBackend
from src.models import Cow

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data_v2"
        self.dm = LocalJSONBackend(data_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cow_new_fields(self):
        # Test new fields: bought_date, bought_from, calf_birth_date
        c = Cow(
            name="NewCow", 
            breed="HF", 
            notes="Test",
            bought_date="2023-01-01",
            bought_from="Farm X",
            calf_birth_date="2023-06-01"
        )
        self.dm.add_cow(c)
        
        saved_cows = self.dm.get_cows()
        self.assertEqual(len(saved_cows), 1)
        self.assertEqual(saved_cows[0].bought_from, "Farm X")
        self.assertEqual(saved_cows[0].bought_date, "2023-01-01")

if __name__ == '__main__':
    unittest.main()
