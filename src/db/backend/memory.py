"""
In-memory database implementation.
"""

from typing import Any, Dict, List
from .database import Database
from .errors import TableNotFoundError, TableAlreadyExistsError
from .table import Table


class MemoryDatabase(Database):
    def __init__(self):
        self._tables: Dict[str, Table] = {}
    
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        if table_name in self._tables:
            raise TableAlreadyExistsError(f"Table '{table_name}' already exists")
        self._tables[table_name] = Table(table_name, schema)
    
    def table_exists(self, table_name: str) -> bool:
        return table_name in self._tables
    
    def drop_table(self, table_name: str) -> bool:
        if table_name in self._tables:
            del self._tables[table_name]
            return True
        return False
    
    def list_tables(self) -> List[str]:
        return list(self._tables.keys())
    
    def create_record(self, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Table '{table_name}' not found")
        return self._tables[table_name].create(record)
    
    def select_records(self, table_name: str, **filters) -> List[Dict[str, Any]]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Table '{table_name}' not found")
        return self._tables[table_name].read(**filters)
    
    def update_record(self, table_name: str, record_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Table '{table_name}' not found")
        return self._tables[table_name].update(record_id, updates)
    
    def delete_record(self, table_name: str, record_id: int) -> bool:
        if table_name not in self._tables:
            raise TableNotFoundError(f"Table '{table_name}' not found")
        return self._tables[table_name].delete(record_id)