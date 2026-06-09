"""
Unit tests for JSON file database.
"""

import unittest
import tempfile
import json
from pathlib import Path

from src.db.backend.file import FileDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError


class TestFileDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = FileDatabase(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_table(self):
        self.db.create_table("test", {"name": str})
        self.assertTrue(self.db.table_exists("test"))
    
    def test_create_duplicate_table(self):
        self.db.create_table("test", {"name": str})
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("test", {"name": str})
    
    def test_create_record(self):
        self.db.create_table("test", {"name": str, "age": int})
        record = self.db.create_record("test", {"name": "John", "age": 25})
        self.assertEqual(record["id"], 1)
        self.assertEqual(record["name"], "John")
    
    def test_select_records(self):
        self.db.create_table("test", {"name": str})
        self.db.create_record("test", {"name": "John"})
        self.db.create_record("test", {"name": "Jane"})
        
        records = self.db.select_records("test")
        self.assertEqual(len(records), 2)
    
    def test_persistence(self):
        self.db.create_table("test", {"name": str})
        self.db.create_record("test", {"name": "John"})
        
        new_db = FileDatabase(self.temp_dir)
        records = new_db.select_records("test")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")
    
    def test_update_record(self):
        self.db.create_table("test", {"name": str})
        self.db.create_record("test", {"name": "John"})
        
        updated = self.db.update_record("test", 1, {"name": "Jane"})
        self.assertEqual(updated["name"], "Jane")
        
        records = self.db.select_records("test")
        self.assertEqual(records[0]["name"], "Jane")
    
    def test_delete_record(self):
        self.db.create_table("test", {"name": str})
        self.db.create_record("test", {"name": "John"})
        
        self.db.delete_record("test", 1)
        records = self.db.select_records("test")
        self.assertEqual(len(records), 0)
    
    def test_drop_table(self):
        self.db.create_table("test", {"name": str})
        self.assertTrue(self.db.table_exists("test"))
        
        self.db.drop_table("test")
        self.assertFalse(self.db.table_exists("test"))


if __name__ == "__main__":
    unittest.main()