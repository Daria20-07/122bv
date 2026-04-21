from .table import Table
from .student import StudentTable
class GradeTable(Table):
    def _init_(self, student_table: Student Table):
        schema={
            "id":int,
            "student_id":int,
            "subject":str,
            "grade":int
            }
        super()._init_("grades",schema)
        self.student_table=student_table
    def _validate(self, record:dict):
        super()._validate(record)
        if record["grade"] not in (2, 3, 4, 5):
            raise ValueError("Оценка должна быть 2, 3, 4, или 5")
        student=self.student_table.read({"id": record["student_id"]})
        if not student:
            raise ValueError(f"Студент с ID {record['student_id']} не существует")
