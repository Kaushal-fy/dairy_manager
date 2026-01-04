import unittest
import os
import shutil
from src.data_manager import LocalJSONBackend
from src.models import Cow, CowEvent

class TestCowCrud(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data_crud_fix"
        self.dm = LocalJSONBackend(data_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cow_crud(self):
        c = Cow(id="C1", name="C1", breed="HF", notes="Initial")
        self.dm.add_cow(c)
        
        # Update using Object
        c_upd = Cow(id="C1", name="C1", breed="Jersey", notes="Updated")
        self.dm.update_cow(c_upd)
        
        saved = self.dm.get_cows()[0]
        self.assertEqual(saved.breed, "Jersey")
        self.assertEqual(saved.notes, "Updated")
        
        # Delete
        self.dm.delete_cow("C1")
        self.assertEqual(len(self.dm.get_cows()), 0)

    def test_cow_event_crud(self):
        e = CowEvent(id="E1", date="2023-01-01", cow_id="C1", event_type="Yield", value="10L")
        self.dm.add_cow_event(e)
        
        e_upd = CowEvent(id="E1", date="2023-01-01", cow_id="C1", event_type="Yield", value="15L")
        self.dm.update_cow_event(e_upd)
        
        saved = self.dm.get_cow_events()[0]
        self.assertEqual(saved.value, "15L")
        
        self.dm.delete_cow_event("E1")
        self.assertEqual(len(self.dm.get_cow_events()), 0)

if __name__ == '__main__':
    unittest.main()
