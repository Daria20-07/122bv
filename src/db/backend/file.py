"""
JSON-based file database implementation.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from .database import Database
from .errors import TableNotFoundError, TableAlreadyExistsError, InvalidStorageDataError, DatabaseError
from .table import Table


class FileDatabase(Database):
    def __init__(self, directory: str = "data"):
        self.directory = Path(directory)
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise DatabaseError(f"Cannot create directory '{directory}': {e}") from e
        self._cache: Dict[str, Table] = {}
    
    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"
    
    def _load_table(self, table_name: str) -> Table:
        if table_name in self._cache:
            return self._cache[table_name]
        
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Table '{table_name}' not found")
        
        try:
            with table_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidStorageDataError(f"Invalid JSON in {table_name}.json") from e
        except OSError as e:
            raise DatabaseError(f"Cannot read file '{table_path}': {e}") from e
        
        table = Table.from_dict(data)
        self._cache[table_name] = table
        return table
    
    def _save_table(self, table: Table) -> None:
        table_path = self._get_table_path(table.name)
        try:
            with table_path.open('w', encoding='utf-8') as f:
                json.dump(table.to_dict(), f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise DatabaseError(f"Cannot write to file '{table_path}': {e}") from e
        self._cache[table.name] = table
    
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        if self.table_exists(table_name):
            raise TableAlreadyExistsError(f"Table '{table_name}' already exists")
        self._save_table(Table(table_name, schema))
    
    def get_table(self, table_name: str) -> Table:
        return self._load_table(table_name)
    
    def get_table_schema(self, table_name: str) -> Dict[str, type]:
        """Get schema of a table."""
        table = self._load_table(table_name)
        return table.schema.copy()
    
    def table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()
    
    def drop_table(self, table_name: str) -> bool:
        if table_name in self._cache:
            del self._cache[table_name]
        table_path = self._get_table_path(table_name)
        if table_path.exists():
            try:
                table_path.unlink()
            except OSError as e:
                raise DatabaseError(f"Cannot delete file '{table_path}': {e}") from e
            return True
        return False
    
    def list_tables(self) -> List[str]:
        try:
            return [f.stem for f in self.directory.glob("*.json")]
        except OSError as e:
            raise DatabaseError(f"Cannot read directory '{self.directory}': {e}") from e
    
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