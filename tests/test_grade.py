import unittest
from models.student import StudentTable
from models.grade import GradeTable
class TestGradeTable(unittest, TestCase):
    def setUp(self):
        self.students=StudentTable()
        self.grades=GradeTable(self, students)
        self.students.create({
            "first_name": "Анна",
            "second_name": "Петрова",
            "age": 20,
            "sex": "Ж"
        })
    def test_create_valid_grade(self):
        rec=self.grades.create({
            "student_id":1,
            "subject": "Математика",
            "grade":5
        })
        self.assertEqual(rec["id"],1)
    def test_invalid_student_id(self):
        with self.assertRaises(ValueError):
            self.grades.create({
                "student_id":999,
                "subject": "Физика",
                "grade": 4
            })
    def test_invalid_grade_value(self):
        with self.assertRaises(ValueError):
            self.grades.create({
                "student_id":1,
                "subject": "Химия",
                "grade": 6
            })
