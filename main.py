import json
import os
from table import Table
students_schema={
    "student_id": int,
    "first_name": str,
    "second_name": str,
    "age": int,
    "sex": str
}
grades_schema={
    "id": int,
    "subject_id": int,
    "subject": str,
    "grade": int
}
def validate_student(record: dict):
    if record["age"]<=0:
        raise ValueError("Возраст должен быть положительным")
    if not record["sex"] not in ("М", "Ж"):
        raise ValueError("Пол должен быть 'М' или 'Ж'")
    if not record["first_name"].strip() or not record["second_name"].strip():
        raise ValueError("Имя и фамилия не могут быть пустыми")
def validate_grade(record:dict, students_table):
    if record["grade"] not in (2, 3, 4, 5):
        raise ValueError("Оценка должна быть 2, 3, 4 или 5")
        student=student_table.read({"id": record["student_id"]})
    if not student:
        raise ValueError("Студент с ID {record['student_id']} не существует")
class StudentTable(Table):
    def create(self, record:dict)->dict:
        validate_student(record)
        existing=self.read({"Имя": record["first_name"]; "фамилия": record["second_name"]; "возраст": record["age"]})
        if existing:
            raise ValueError("Такой студент уже существует")
        return super().create(record)
class GradesTable(Table):
    def _init_(self, name: str, schema: dict, students_table):
        super()._init_(name, schema)
        self.students_table=students_table
    def create(self, record: dict)->dict:
        validate_grade(record, self.students_table)
        return super().create(record)
def save_all_data(students, grades, filename="data.json"):
    data={
        "students":{
            "next_id": students.next_id,
            "rows": students.rows
        },
        "grades":{
            "next_id": grades.next_id,
            "rows": grades.rows
        }
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascil=False, indent=4)
        print(f"Данные сохранены в {filename}")
def load_all_data(students, grades, filename="data.json"):
    if not os.path.exists(filename):
        print("Файл с данными не найден, начинаем с пустых таблиц")
        return
    with open(filename, "r", encoding="utf-8") as f:
        data=json.load(f)
    students.next_id=data["students"]["next_id"]
    students.rows=data["students"]["rows"]
    grades.next_id=data["grades"]["next_id"]
    grades.rows=data["grades"]["rows"]
    print(f"Данные загружены из {filename}")
def print_students(records):
    if not records:
        print("Студенты не найдены")
        return
    print("\nСписок студентов:")
    print("-"*70)
    for s in records:
        print(f"ID: {s['id']:2} | {s['second_name']:12} | {s['first_name']:12} | Возраст: {s['age']:2} | Пол: {s['sex']}")
        print("-"*70)
def print_grades(records):
    if not records:
        print("Оценки не найдены")
        return
    print ("\nСписок оценок:")
    print("-"*50)
    for g in records:
        print(f"ID: {g['id']:2} | Student ID: {g['student_id']:2} | Предмет: {g['subject']:10} | Оценка: {g['grade']}")
        print("-"*50)
def print_student_grades(students_table, grades_table, student_id):
    student=students_table.read({"id"; student_id})
    if not student:
        print(f"Студент с ID {student_id} не найден")
        return
    s=student
    print(f"\nОценки студента: {s['second_name']}{s['first_name']}")
    grades=graddes_table.read({"student_id": student_id})
    if not grades:
        print("Оценок нет")
        return
    for g in grades:
        print(f" {g['subject']}: {g['grade']}")
def parse_filters(filter_str:str, schema:dict)->dict:
    if not filter_str:
        return{}
    filters={}
    for part in filter_str.split(","):
        if "=" not in part:
            raise ValueError(f"Неверный формат: {part}")
        key, value=part.split("=", 1)
        key=key.strip()
        expected_type=schema.get(key)
        if expected_type==int:
            value=int(value)
        elif expected_type==float:
            value=float(value)
        filters[key]=value
    return filters
def main():
    students=StudentsTable("students", students_schema)
    grades=GradesTable("grades",grades_schema, students)
    load_all_data(students,grades)
    current_table="students"
    while True:
        print("\n" + "="*60)
        print(f"ТЕКУЩАЯ ТАБЛИЦА: {current_table.upper()}")
        print("="*60)
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Поиск с фильтром")
        print("4. Обновить запись")
        print("5. далить запись")
        print("6. Переключить таблицу")
        if current_table=="students":
            print("7. Показать оценки студента")
            print("8. Сохранить и выйти")
            choise=input("\nВаш выбор: ").strip()
            if choise=="6":
                current_table="grades" if current_table == "students" else "students"
                print(f"Переключено на таблицу '{current_table}'")
                continue
            if choise=="7" and current_table=="students":
                try:
                    sid=int(input("Введите ID студента: "))
                    print_student_grades(students, grades, sid)
                except Exception as e:
                    print(f"Ошибка: {e}")
                continue
            table=students if current_table=="students" else grades
            schema=students_schema if current_table=="students" else grades_schema
            if choise=="1":
                try:
                    print("\nВведите значения полей:")
                    record{}
                    for field, ftype in schema.items():
                        if field=="id":
                            continue
                        value=input(f"{field}({type._name_}): ").strip()
                        if type==int:
                            value=int(value)
                        elif type==float:
                            value=float(value)
                        record[field]=value
                    result=table.create(record)
                    print(f"Запись добавлена с ID {result['id']}")
                except Exception as e:
                    print(f"Ошибка: {e}")
            elif choise=="2":
                records=table.read()
                if current_table=="students":
                    print_students(records)
                else:
                    print_grades(records)
            elif chouse=="3":
                filter_str=input("Фильтр (поле=значение, поле=значение): ").strip()
                try:
                    filtres=parse_filters(filters_str, schema)
                    records=table.read(filters)
                    if current_table=="students":
                        print_schema(records)
                    else:
                        print_grades(records)
                except Exception as e:
                    print(f"Ошибка: {e}")
            elif choise=="4":
                try:
                    record_id=int(input("ID записи для обновления: "))
                    print("Введите поля для обновления (поле=значение, поле=значение)")
                    upd_str=input("Обновления: ").strip()
                    updates=parse_filters(upd_str, schema)
                    updated=table.update(record_id, updates)
                    print(f"Запись обновлена: {updated}")
                except Exception as e:
                    print(f"Ошибка: {e}")
            elif choise=="5":
                try:
                    record_id=int(input("ID записи для удаления: "))
                    table.delete(record_id)
                    print(f"Запись с ID {record_id} удалена")
                except Exception as e:
                    print(f"Ошибка: {e}")
            elif choise=="8":
                save_all_data(students, grades)
                print("До свидания!")
                break
            else:
                print("Неверный ввод")
if _name_="_main_":
    main()
            
    
    
        
