"""
Unit tests for the in-memory database.
"""

import unittest
from src.db.backend.memory import Database, Table
from src.db.backend.errors import (
    TableNotFoundError,
    RecordNotFoundError,
    ValidationError,
    InvalidFieldTypeError,
    MissingFieldError
)


class TestTable(unittest.TestCase):
    """Test cases for Table class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.schema = {
            "name": str,
            "age": int,
            "city": str
        }
        self.table = Table("test_table", self.schema)
    
    def test_create_table(self):
        """Test table creation."""
        self.assertEqual(self.table.name, "test_table")
        self.assertEqual(self.table.schema, self.schema)
        self.assertEqual(self.table.count(), 0)
    
    def test_create_record(self):
        """Test creating a record."""
        record = self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        
        self.assertEqual(record["id"], 1)
        self.assertEqual(record["name"], "John")
        self.assertEqual(record["age"], 25)
        self.assertEqual(self.table.count(), 1)
    
    def test_create_record_missing_field(self):
        """Test creating record with missing field."""
        with self.assertRaises(MissingFieldError):
            self.table.create({"name": "John", "age": 25})
    
    def test_create_record_invalid_type(self):
        """Test creating record with invalid field type."""
        with self.assertRaises(InvalidFieldTypeError):
            self.table.create({"name": "John", "age": "twenty", "city": "Moscow"})
    
    def test_read_all_records(self):
        """Test reading all records."""
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.table.create({"name": "Jane", "age": 30, "city": "SPb"})
        
        records = self.table.read()
        self.assertEqual(len(records), 2)
    
    def test_read_with_filters(self):
        """Test reading with filters."""
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.table.create({"name": "Jane", "age": 30, "city": "SPb"})
        self.table.create({"name": "John", "age": 35, "city": "SPb"})
        
        records = self.table.read(name="John")
        self.assertEqual(len(records), 2)
        
        records = self.table.read(city="SPb")
        self.assertEqual(len(records), 2)
    
    def test_update_record(self):
        """Test updating a record."""
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        
        updated = self.table.update(1, {"age": 26, "city": "SPb"})
        
        self.assertEqual(updated["age"], 26)
        self.assertEqual(updated["city"], "SPb")
    
    def test_update_nonexistent_record(self):
        """Test updating non-existent record."""
        with self.assertRaises(RecordNotFoundError):
            self.table.update(999, {"name": "Test"})
    
    def test_delete_record(self):
        """Test deleting a record."""
        self.table.create({"name": "John", "age": 25, "city": "Moscow"})
        self.assertEqual(self.table.count(), 1)
        
        self.table.delete(1)
        self.assertEqual(self.table.count(), 0)
    
    def test_sort_ascending(self):
        """Test sorting records in ascending order."""
        self.table.create({"name": "John", "age": 30, "city": "Moscow"})
        self.table.create({"name": "Alice", "age": 25, "city": "SPb"})
        self.table.create({"name": "Bob", "age": 35, "city": "Kazan"})
        
        sorted_records = self.table.sort("age", reverse=False)
        
        self.assertEqual(sorted_records[0]["age"], 25)
        self.assertEqual(sorted_records[1]["age"], 30)
        self.assertEqual(sorted_records[2]["age"], 35)
    
    def test_sort_descending(self):
        """Test sorting records in descending order."""
        self.table.create({"name": "John", "age": 30, "city": "Moscow"})
        self.table.create({"name": "Alice", "age": 25, "city": "SPb"})
        self.table.create({"name": "Bob", "age": 35, "city": "Kazan"})
        
        sorted_records = self.table.sort("age", reverse=True)
        
        self.assertEqual(sorted_records[0]["age"], 35)
        self.assertEqual(sorted_records[1]["age"], 30)
        self.assertEqual(sorted_records[2]["age"], 25)


class TestDatabase(unittest.TestCase):
    """Test cases for Database class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.db = Database()
    
    def test_create_table(self):
        """Test creating a table."""
        schema = {"name": str, "age": int}
        table = self.db.create_table("users", schema)
        
        self.assertIsInstance(table, Table)
        self.assertTrue(self.db.table_exists("users"))
    
    def test_create_duplicate_table(self):
        """Test creating duplicate table."""
        schema = {"name": str, "age": int}
        self.db.create_table("users", schema)
        
        with self.assertRaises(ValidationError):
            self.db.create_table("users", schema)
    
    def test_get_nonexistent_table(self):
        """Test getting non-existent table."""
        with self.assertRaises(TableNotFoundError):
            self.db.get_table("nonexistent")
    
    def test_drop_table(self):
        """Test dropping a table."""
        schema = {"name": str, "age": int}
        self.db.create_table("users", schema)
        
        self.assertTrue(self.db.table_exists("users"))
        self.db.drop_table("users")
        self.assertFalse(self.db.table_exists("users"))


if __name__ == "__main__":
    unittest.main()