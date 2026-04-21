from models.student import StudentTable
from models.grade import GradeTable
from storage.json_storage import JsonStorage
class ConsoleUI:
    def _init_(self):
        self.student=StudentTable()
        self.grades=GradeTable(self.students)
        self.current_table=self.students
        JsonStorage.load("data.json", {
            "students": self.students,
            "grades": self.grades
        })
    def run(self):
        while True:
            self._show_menu()
            choice=input("Выберите действие: ").strip()
            if choice=="1":
                self._add()
            elif choice=="2":
                self._list_all()
            elif choice=="3":
                self._filter()
            elif choice=="4":
                self._update()
            elif choice=="5":
                self._delete()
            elif choice=="6":
                self._sort_prompt()
            elif choice=="7":
                self._switch_table()
            elif choice=="8":
                self._exit()
                break
            else:
                print("Неверный ввод")
    def _show_menu(self):
        print("\n"+"="*50)
        print(f"ТЕКУЩАЯ ТАБЛИЦА: {self.current_table.name.upper()}")
        print("="*50)
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Поиск с фильтром")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("6. Сортировка")
        print("7. Переключить таблицу")
        print("8. Сохранить и выйти")
    def _add(self):
        try:
            print("n\Введите значения полей:")
            record={}
            for field, ftype in self.current_table.schema.items():
                if field=="id":
                    continue
                value=input(f"{field} ({ftype._name_}): ").strip()
                if ftype==int:
                    value=int(value)
                elif ftype==float:
                    value=float(value)
                record[field]=value
            result=self.current_table.creat(record)
            print(f"Запись добавлена с ID {result['id']}")
        except Exception as e:
            print(f"Ошибка: {e}")
    def _list_all(self):
        records=self.current_table.read()
        if not records:
            print("Записи не найдены")
            return
        for rec in records:
            print(rec)
    def _filters(self):
        filter_str=input("Фильтр (поле=значение, поле=значение): ").strip()
        if not filter_str:
            print("Фильтр не может быть пустым")
            return
        filters={}
        try:
            for part in filter_str.split(","):
                key, val=part.split("=",1)
                key=key.strip()
                if key in self.current_table.schema:
                    expected=self.current_table.schema[key]
                    if expected==int:
                        val=int(val)
                    elif expected==float:
                        val=float(val)
                filters[key]=vall
            records=self.current_table.read(filters)
            if not records:
                print("Записи не найдены")
            else:
                for rec in records:
                    print(rec)
        except Exception as e:
            print(f"Ошибка: {e}")
    def _update(self):
        try:
            rid=int(input("ID записи для обновления: "))
            print("Введите поля для обновления (поле=значениеб поле=значение):")
            upd_str=input().strip()
            updates={}
            for part in upd_str.split(","):
                key, val=part.split("=",1)
                key=key.strip()
                if key in self.current_table.schema:
                    expected=self.current_table.schema[key]
                    if expected==int:
                        val=int(val)
                    elif expected==float:
                        val=float(val)
                updates[key]=val
            updated=self.current_table.update(rid, updates)
            print(f"Запись обновлена: {updated}")
        except Exception as e:
            print(f"Ошибка: {e}")
    def _delete(self):
        try:
            rid=int(input("ID записи для удаления: "))
            self.current_table.delete(rid)
            print(f"Запись с ID {rid} удалена")
        except Exception as e:
            print(f"Ошибка: {e}")
    def _sort_prompt(self):
        print("Доступные поля:", ", ".join(self.current_table.schema.keys()))
        field=input("Поле для сортировки: ").strip()
        if field not in self.current_table.schema:
            print("Нет такого поля")
            return
        order=input("Порядок (ask/desk):").strip().lower()
        reverse=(order=="desc")
        try:
            sorted_data=self.current_table.sort(field, reverse)
            if not sorted_data:
                print("Нет данных для сортировки")
            else:
                for row in sorted_data:
                    print(row)
        except Exception as e:
            print(f"Ошибка: {e}")
    def _switch_table(self):
        if self.current_table==self.students:
            self.current_table=eslf.grades
        else:
            self.current_table=self.students
        print(f"Переключено на таблицу '{self.current_table.name}'")
    def _exit(self):
        JsonStorage.save("data.json", {
            "students": self.students,
            "grades": self.grades
        })
        print("Данные сохранены. До свидания!")
                
            
        
