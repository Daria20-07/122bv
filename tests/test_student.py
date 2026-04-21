import unittest
from models.student import StudentTable
class TestStudentTable(unittest, TestCase):
    def setUp(self):
        self.students=StudentTable()
    def test_create_valid(self):
        rec=self.students.create({
            "first_name":"Анна",
            "second_name": "Петрова",
            "age": 20,
            "sex": "Ж"
        })
        self.assertEqual(rec["id"],1)
    def test_create_duplicate(self):
        data={"first_name":"Иван", "second_name":"Иванов", "age":21, "sex": "М"}
        self.students.create(data)
        with self.assertRaises(ValueError):
            self.students.create(data)
    def test_invalid_age(self):
        with self.assertRaises(Valueerror):
            self.students.create({
                "first_name"="Анна",
                "second_name"="Петрова",
                "age"=-5,
                "sex"="Ж"
            })
    def test_invalid_gender(self):
        with self.assertRaises(ValueError):
            self.students.create({
                "first_name":"Анна",
                "second_name":"Петрова",
                "age":20,
                "sex": "Х"
            })
