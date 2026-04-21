from .table import Table
class StudentTable(Table):
    def _init_(self):
        schema={
            "id":int,
            "first_name":str,
            "second_name":str,
            "age":int,
            "sex":str
            }
        super()._init_("Students",schema)
    def _validate(self, record:dict):
        super()._validate(record)
        if record["age"]<=0:
            raise ValueError("Возраст должен быть положительным числом")
        if record["sex"] not in ("М","Ж"):
            raise ValueError("Пол должен быть 'М' или 'Ж'")
        if not record["first_name"].strip() or not record["second_name"].strip():
            raise ValueError("Имя и фамилия не могут быь пустыми")
    def create(self, record:dict)->dict:
        self._validate(record)
        for row in self.rows:
            if (row["first_name"]==record["first_name"] and row["second_name"]==record["second_name"] and row["age"]==record["age"]):
                raise ValueError("Такой студент уже существует")
        return super().create(record)
    def update(self, record_id:int, updates:dict)->dict:
        current=self.read({"id":record_id})
        if not current:
            raise ValueError(f"тудент с ID {record_id} не найден")
        test=current[0].copy()
        for k,v in updates.items():
            test[k]=v
        self._validate(test)
        for row in self.rows:
            if row["id"]!=record_id:
                if (row["first_name"]==test["first_name"] and row["second_name"]==test["second_name"] and row["age"]==test["age"]):
                    raise ValueError("бновление создаёт дубликат")
        return super().update(record_id, updates)
