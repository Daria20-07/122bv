"""
Unit tests for Table class.
"""

import unittest
from src.db.backend.table import Table
from src.db.backend.errors import (
    MissingFieldError, 
    InvalidFieldTypeError, 
    RecordNotFoundError,
    ValidationError
)


class TestTable(unittest.TestCase):
    def setUp(self):
        self.schema = {"name": str, "age": int, "city": str}
        self.table = Table("test_table", self.schema)
    
    def test_create_table(self):
        self.assertEqual(self.table.name, "test_table")
        self.assertEqual(self.table.schema, self.schema)
        self.assertEqual(self.table.count(), 0)
    
    def test_create_record(self):
        record = self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.assertEqual(record["id"], 1)
        self.assertEqual(record["name"], "John")
        self.assertEqual(self.table.count(), 1)
    
    def test_create_record_missing_field(self):
        with self.assertRaises(MissingFieldError):
            self.table.create({"name": "John", "age": 25})
    
    def test_create_record_invalid_type(self):
        with self.assertRaises(InvalidFieldTypeError):
            self.table.create({"name": "John", "age": "twenty", "city": "Moscow"})
    
    def test_read_all_records(self):
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.table.create({"name": "Jane", "age": 30, "city": "SPb"})
        records = self.table.read()
        self.assertEqual(len(records), 2)
    
    def test_read_with_filters(self):
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.table.create({"name": "Jane", "age": 30, "city": "SPb"})
        self.table.create({"name": "John", "age": 35, "city": "SPb"})
        
        records = self.table.read(name="John")
        self.assertEqual(len(records), 2)
        
        records = self.table.read(city="SPb")
        self.assertEqual(len(records), 2)
        
        records = self.table.read(name="John", city="Moscow")
        self.assertEqual(len(records), 1)
    
    def test_read_with_invalid_filter_field(self):
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        with self.assertRaises(InvalidFieldTypeError):
            self.table.read(invalid_field="value")
    
    def test_update_record(self):
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        updated = self.table.update(1, {"age": 26, "city": "SPb"})
        self.assertEqual(updated["age"], 26)
        self.assertEqual(updated["city"], "SPb")
    
    def test_update_nonexistent_record(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.update(999, {"name": "Test"})
    
    def test_delete_record(self):
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.assertEqual(self.table.count(), 1)
        self.table.delete(1)
        self.assertEqual(self.table.count(), 0)
    
    def test_delete_nonexistent_record(self):
        with self.assertRaises(RecordNotFoundError):
            self.table.delete(999)
    
    def test_clear_table(self):
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.table.create({"name": "Jane", "age": 30, "city": "SPb"})
        self.assertEqual(self.table.count(), 2)
        self.table.clear()
        self.assertEqual(self.table.count(), 0)
    
    def test_sort_ascending(self):
        self.table.create({"name": "John", "age": 30, "city": "Moscow"})
        self.table.create({"name": "Alice", "age": 25, "city": "SPb"})
        self.table.create({"name": "Bob", "age": 35, "city": "Kazan"})
        
        sorted_records = self.table.sort("age", reverse=False)
        self.assertEqual(sorted_records[0]["age"], 25)
        self.assertEqual(sorted_records[1]["age"], 30)
        self.assertEqual(sorted_records[2]["age"], 35)
    
    def test_sort_descending(self):
        self.table.create({"name": "John", "age": 30, "city": "Moscow"})
        self.table.create({"name": "Alice", "age": 25, "city": "SPb"})
        self.table.create({"name": "Bob", "age": 35, "city": "Kazan"})
        
        sorted_records = self.table.sort("age", reverse=True)
        self.assertEqual(sorted_records[0]["age"], 35)
        self.assertEqual(sorted_records[1]["age"], 30)
        self.assertEqual(sorted_records[2]["age"], 25)
    
    def test_sort_empty_table(self):
        sorted_records = self.table.sort("age")
        self.assertEqual(sorted_records, [])
    
    def test_sort_invalid_field(self):
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        with self.assertRaises(ValidationError):
            self.table.sort("invalid_field")
    
    def test_create_index(self):
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.table.create({"name": "Jane", "age": 30, "city": "SPb"})
        
        self.table.create_index("name")
        indexes = self.table.get_indexes()
        self.assertIn("name", indexes)
        self.assertIn("John", indexes["name"])
        self.assertIn(1, indexes["name"]["John"])
    
    def test_index_lookup(self):
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.table.create({"name": "Jane", "age": 30, "city": "SPb"})
        self.table.create({"name": "John", "age": 35, "city": "SPb"})
        
        self.table.create_index("name")
        records = self.table.read(name="John")
        self.assertEqual(len(records), 2)
    
    def test_drop_index(self):
        self.table.create_index("name")
        self.table.drop_index("name")
        indexes = self.table.get_indexes()
        self.assertNotIn("name", indexes)
    
    def test_to_dict_with_indexes(self):
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.table.create_index("name")
        
        data = self.table.to_dict()
        self.assertIn("indexes", data)
        self.assertIn("name", data["indexes"])
    
    def test_from_dict_with_indexes(self):
        original = Table("original", {"name": str})
        original.create({"name": "Test"})
        original.create_index("name")
        
        data = original.to_dict()
        restored = Table.from_dict(data)
        
        self.assertEqual(restored.name, "original")
        self.assertEqual(restored.count(), 1)
        indexes = restored.get_indexes()
        self.assertIn("name", indexes)


if __name__ == "__main__":
    unittest.main()