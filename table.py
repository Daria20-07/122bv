class Table:
    def _init_(self, name: str, schema: dict):
        self.name=name
        self.schema=schema
        self.rows=[]
        self next.id=1
    def _validate(self, record: dict):
        for field, expected_type in self.schema.items():
            if field=="id":
                continue
            if field not in record:
                raise ValueError(f"Отсутствует обязательное поле: '{field}'")
            if not isinstance(record[field], expected_type):
                raise TypeError (f"Поле '{field}' Должно быть типа {expected_type._name_}")
            def create(self, record: dict)->dict:
                self._validate(record)
                new_record={"id":self.next_id}
                for field in self.schema:
                    if field!="id":
                        new_record[field]=record[field]
                self.rows.append(new_record)
                self.next_id+=1
                return new_record
            def read(self, filters: dict=None)->list:
                if not filters:
                    return self.rows.copy()
                result=[]
                for row in self.rows:
                    match=True
                    for key, value in filters.items():
                        if key not in row or row[key]!=value:
                            match=False
                            break
                        if match:
                            result.append(row)
                return result
            def update(self, record_id:int, updates:dict)->dict:
                for row in self.rows:
                    if row["id"]==record_id:
                        for field, value in updates.items():
                            if field not in self.schema:
                                raise ValueError(f"Поле '{field}' должно быть {self.schema[field]._name_}")
                            row[field]=value
                        return row
                raise ValueError(f"ID {record_id} не найден")
            def delete(self, record_id: int)->bool:
                for i, row in enumerate(self.rows):
                    if row["id"]==record_id:
                        del self.rows[i]
                        return True
                raise ValueError(f"ID {record_id} не найден")
                
                
                        
                
