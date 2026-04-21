class Table:
    def _init_(self, name:str, schema:dict):
        self.name=name
        self.schema=schema
        self.rows=[]
        self.next_id=1
        def _validate(self, record: dict):
            for field, expected_type in self.schema.items():
                if field=="id":
                    continue
                if field not in record:
                    raise ValueError(f"Отсутствует поле: '{field}'")
                if not isinstance(record[field], expected_type):
                    raise TypeError(
                        f"Поле '{field}' должно быть {expected_type._name_},"
                        f"получен {type(record[field])._name_}"
                        )
        def create(self, record:dict)->dict:
            self._validate(record)
            new_record={"id": self.next_id}
            for field in self.schema:
                if field!="id":
                    new_record[field]=record[field]
            self.rows.append(new_record)
            self.next_id+=1
            return new_record
        def read(self, filters:dict=None)->list:
            if not filters:
                return self.rows.copy()
            result=[]
            for row in self.rows:
                match=True
                for key, value in filters.items():
                    if row.get(key)!=value:
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
                            raise ValueError(f"Поле '{field}' не существует")
                        if not isinstance(value, self.schema[field]):
                            raise TypeError(f"Поле '{field}' должно быть {self.schema[field]._name_}")
                        row[field]=value
                    return row
            raise ValueError(f"Запись с ID {record_id} не найдена")
        def delete(self, record_id: int)->bool:
            for i, row in enumerate(self.rows):
                if row["id"]==record_id:
                    del self.rows[i]
                    return True
            raise ValueError(f"Запись с ID {record_id} не найдена")
        def sort(self, key:str, reverse:bool=False)->list:
            if key not in self.schema:
                raise ValueError(f"Поле '{key}' не найдено в схеме")
            return sorted(self.rows, key=lambda row: row[key], reverse=reverse)
        
                
