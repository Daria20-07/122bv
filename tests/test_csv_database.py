"""
Unit tests for CSV file database (bonus task).
"""

import unittest
import tempfile
import json
import csv
from pathlib import Path

from src.db.backend.csvdb import CSVDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError, RecordNotFoundError


class TestCSVDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = CSVDatabase(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_table(self):
        self.db.create_table("test", {"name": str})
        self.assertTrue(self.db.table_exists("test"))
        self.assertIn("test", self.db.list_tables())
    
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
    
    def test_select_with_filters(self):
        self.db.create_table("test", {"name": str})
        self.db.create_record("test", {"name": "John"})
        self.db.create_record("test", {"name": "Jane"})
        
        records = self.db.select_records("test", name="John")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")
    
    def test_persistence(self):
        self.db.create_table("test", {"name": str})
        self.db.create_record("test", {"name": "John"})
        
        new_db = CSVDatabase(self.temp_dir)
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
    
    def test_csv_file_created(self):
        self.db.create_table("test", {"name": str, "age": int})
        self.db.create_record("test", {"name": "John", "age": 25})
        
        csv_path = Path(self.temp_dir) / "test.csv"
        schema_path = Path(self.temp_dir) / "test_schema.json"
        
        self.assertTrue(csv_path.exists())
        self.assertTrue(schema_path.exists())
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "John")
    
    def test_schema_file_correct(self):
        self.db.create_table("test", {"name": str, "age": int})
        
        schema_path = Path(self.temp_dir) / "test_schema.json"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        self.assertEqual(schema["name"], "str")
        self.assertEqual(schema["age"], "int")
    
    def test_load_nonexistent_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")
    
    def test_create_index(self):
        self.db.create_table("test", {"name": str})
        self.db.create_record("test", {"name": "John"})
        self.db.create_record("test", {"name": "Jane"})
        
        self.db.create_index("test", "name")
        
        records = self.db.select_records("test", name="John")
        self.assertEqual(len(records), 1)
    
    def test_sort_records(self):
        self.db.create_table("test", {"name": str, "age": int})
        self.db.create_record("test", {"name": "John", "age": 30})
        self.db.create_record("test", {"name": "Alice", "age": 25})
        
        table = self.db.get_table("test")
        sorted_records = table.sort("age")
        self.assertEqual(sorted_records[0]["age"], 25)


if __name__ == "__main__":
    unittest.main()