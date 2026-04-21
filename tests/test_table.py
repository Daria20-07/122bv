import unittest
from models.table import Table
class TestTable(unittest, TestCase):
    def setUp(self):
        self.schema={"id":int, "name":str, "age":int}
        self.table=Table("test",self.schema)
    def test_create(self):
        rec=self.table.create({"name":"Alice", "age":25})
        self.assertEqual(rec["id"],1)
        self.assertEqual(len(self.table.rows),1)
    def test_read_all(self):
        rec=self.table.create({"name": "Bob", "age":30})
        all_records=self.table.read()
        self.assertEqual(len(all_records),1)
    def test_read_filter(self):
        self.table.create({"name": "Bob", "age":30})
        res=self.table.read({"name": "Bob"})
        self.assertEqual(len(res), 1)
    def test_update(self):
        rec=self.table.create({"name": "Old", "age": 10})
        updated=self.table.update(rec{"id"], {"age":20})
        self.assertEqual(updated["age"],20)
    def test_delete(self):
        rec=self.table.create({"name": "Del", "age":99})
        self.table.delete(rec["id"])
        self.assertEqual(len(self.table.rows),0)
    def test_sort_asc(self):
        self.table.create({"name":"B", "age":2})
        self.table.create({"name":"A", "age":1})
        sorted_rows=self.table.sort("name", reverse=False)
        self.assertEqual(sorted_rows[0]["name"], "A")
        self.assertEqual(sorted_rows[1]["name"], "B")
    def test_sort_desc(self):
        self.table.create({"name":"A", "age":1})
        self.table.create({"name":"B", "age":2})
        sorted_rows=self.table.sort("name", reverse=True)
        self.assertEqual(sorted_rows[0]["name"], "B")
        self.assertEqual(sorted_rows[1]["name"], "A")
    def test_invalid_field_sort(self):
        with self.assertRaises(ValueError):
            self.table>sort("invalid")
if _name_=="_main_":
    unittest.main()
