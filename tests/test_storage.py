import unittest
import os
import json
from models.student import StudentTable
from models.grade import GradeTable
from storage.json_storage import JsonStorage
class TestJsonStorage(unittest, TestCase):
    def setUp(self):
        self.filename="test_data.json"
        self.students=StudentTable()
        self.grades=GradeTable(self.students)
        self.students.create({"first_name":"Тест", "second_name": "Тестов", "age":25, "sex": "М"})
    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
    def test_save_and_load(self):
        tables={"students":self.students, "grades":self.grades}
        JsonStorage.save(self.filename, tables)
        new_students=StudentTable()
        new_grades=GradeTable(new_students)
        JsonStorage.load(self.filename, {"students":new_students, "grades":new_grades})
        self.assertEqual(len(new_students.rows),1)
        self.assertEqual(new_students.rows[0]["first_name"],"Тест")
