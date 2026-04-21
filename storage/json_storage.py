import json
import os
class JsonStorage:
    @staticmethod
    def save(filename:str, tables:dict):
        data={}
        for name, table in tables.items():
            data[name]={
                "next_id":table.next_id,
                "rows":table.rows
            }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    @staticmethod
    def load(filename:str, tables:dict):
        if not os.path.exists(filename):
            return
        with open(filename, "r", encoding="utf-8") as f:
            data=json.load(f)
        for name, table in tables.items():
            if name in data:
                table.next_id=data[name]["next_id"]
                table.rows=data[name]["rows"]
        
        
