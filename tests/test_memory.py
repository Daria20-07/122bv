"""
Unit tests for MemoryDatabase.
"""

import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError, RecordNotFoundError


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()
    
    def test_create_table(self):
        self.db.create_table("users", {"name": str, "age": int})
        self.assertTrue(self.db.table_exists("users"))
        self.assertEqual(self.db.list_tables(), ["users"])
    
    def test_create_duplicate_table(self):
        self.db.create_table("users", {"name": str})
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("users", {"name": str})
    
    def test_get_table(self):
        self.db.create_table("users", {"name": str})
        table = self.db.get_table("users")
        self.assertEqual(table.name, "users")
    
    def test_get_nonexistent_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_table("nonexistent")
    
    def test_drop_table(self):
        self.db.create_table("users", {"name": str})
        self.assertTrue(self.db.table_exists("users"))
        self.db.drop_table("users")
        self.assertFalse(self.db.table_exists("users"))
    
    def test_create_record(self):
        self.db.create_table("users", {"name": str, "age": int})
        record = self.db.create_record("users", {"name": "John", "age": 25})
        self.assertEqual(record["id"], 1)
        self.assertEqual(record["name"], "John")
    
    def test_select_records(self):
        self.db.create_table("users", {"name": str})
        self.db.create_record("users", {"name": "John"})
        self.db.create_record("users", {"name": "Jane"})
        
        records = self.db.select_records("users")
        self.assertEqual(len(records), 2)
    
    def test_select_with_filters(self):
        self.db.create_table("users", {"name": str})
        self.db.create_record("users", {"name": "John"})
        self.db.create_record("users", {"name": "Jane"})
        
        records = self.db.select_records("users", name="John")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")
    
    def test_update_record(self):
        self.db.create_table("users", {"name": str})
        self.db.create_record("users", {"name": "John"})
        
        updated = self.db.update_record("users", 1, {"name": "Jane"})
        self.assertEqual(updated["name"], "Jane")
    
    def test_delete_record(self):
        self.db.create_table("users", {"name": str})
        self.db.create_record("users", {"name": "John"})
        
        self.db.delete_record("users", 1)
        records = self.db.select_records("users")
        self.assertEqual(len(records), 0)
    
    def test_sort_records(self):
        self.db.create_table("users", {"name": str, "age": int})
        self.db.create_record("users", {"name": "John", "age": 30})
        self.db.create_record("users", {"name": "Alice", "age": 25})
        
        sorted_records = self.db.sort_records("users", "age")
        self.assertEqual(sorted_records[0]["age"], 25)
    
    def test_create_index(self):
        self.db.create_table("users", {"name": str})
        self.db.create_record("users", {"name": "John"})
        self.db.create_index("users", "name")
        
        table = self.db.get_table("users")
        indexes = table.get_indexes()
        self.assertIn("name", indexes)


if __name__ == "__main__":
    unittest.main()