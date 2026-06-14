"""
CSV-based file database implementation (bonus task).
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from .database import Database
from .errors import TableNotFoundError, TableAlreadyExistsError, InvalidStorageDataError
from .table import Table


class CSVDatabase(Database):
    def __init__(self, directory: str = "data_csv"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Table] = {}
    
    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"
    
    def _get_schema_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}_schema.json"
    
    def _load_table(self, table_name: str) -> Table:
        if table_name in self._cache:
            return self._cache[table_name]
        
        table_path = self._get_table_path(table_name)
        schema_path = self._get_schema_path(table_name)
        
        if not table_path.exists():
            raise TableNotFoundError(f"Table '{table_name}' not found")
        
        try:
            with schema_path.open('r', encoding='utf-8') as f:
                schema_data = json.load(f)
            
            schema = {}
            for field, type_name in schema_data.items():
                schema[field] = str if type_name == 'str' else int
            
            table = Table(table_name, schema)
            
            with table_path.open('r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    converted_row = {}
                    for field, value in row.items():
                        if field == 'id':
                            continue
                        if field in schema and schema[field] == int:
                            converted_row[field] = int(value) if value else 0
                        else:
                            converted_row[field] = value
                    table.create(converted_row)
            
            self._cache[table_name] = table
            return table
        except Exception as e:
            raise InvalidStorageDataError(f"Error loading CSV table {table_name}: {e}") from e
    
    def _save_table(self, table: Table) -> None:
        table_path = self._get_table_path(table.name)
        schema_path = self._get_schema_path(table.name)
        
        schema_data = {field: 'str' if t == str else 'int' 
                       for field, t in table.schema.items()}
        
        with schema_path.open('w', encoding='utf-8') as f:
            json.dump(schema_data, f, ensure_ascii=False, indent=2)
        
        fieldnames = ['id'] + list(table.schema.keys())
        
        with table_path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(table.get_all())
        
        self._cache[table.name] = table
    
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        if self.table_exists(table_name):
            raise TableAlreadyExistsError(f"Table '{table_name}' already exists")
        self._save_table(Table(table_name, schema))
    
    def get_table(self, table_name: str) -> Table:
        """Get a table by name."""
        return self._load_table(table_name)
    
    def table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()
    
    def drop_table(self, table_name: str) -> bool:
        if table_name in self._cache:
            del self._cache[table_name]
        
        deleted = False
        table_path = self._get_table_path(table_name)
        schema_path = self._get_schema_path(table_name)
        
        if table_path.exists():
            table_path.unlink()
            deleted = True
        if schema_path.exists():
            schema_path.unlink()
        
        return deleted
    
    def list_tables(self) -> List[str]:
        return [f.stem for f in self.directory.glob("*.csv")]
    
    def create_record(self, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        table = self._load_table(table_name)
        result = table.create(record)
        self._save_table(table)
        return result
    
    def select_records(self, table_name: str, **filters) -> List[Dict[str, Any]]:
        table = self._load_table(table_name)
        return table.read(**filters)
    
    def update_record(self, table_name: str, record_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        table = self._load_table(table_name)
        result = table.update(record_id, updates)
        self._save_table(table)
        return result
    
    def delete_record(self, table_name: str, record_id: int) -> bool:
        table = self._load_table(table_name)
        result = table.delete(record_id)
        self._save_table(table)
        return result
    
    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        table = self._load_table(table_name)
        return table.sort(field, reverse)
    
    def create_index(self, table_name: str, field_name: str) -> None:
        table = self._load_table(table_name)
        table.create_index(field_name)
        self._save_table(table)
    
    def drop_index(self, table_name: str, field_name: str) -> None:
        table = self._load_table(table_name)
        table.drop_index(field_name)
        self._save_table(table)