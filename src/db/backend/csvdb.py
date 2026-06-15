"""
CSV-based file database implementation (bonus task).
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from .database import Database
from .errors import TableNotFoundError, TableAlreadyExistsError, InvalidStorageDataError, DatabaseError, ValidationError
from .table import Table


class CSVDatabase(Database):
    """Database that stores tables in CSV files with separate schema and index files."""
    
    def __init__(self, directory: str = "data_csv"):
        """Initialize CSV database with given directory."""
        self.directory = Path(directory)
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise DatabaseError(f"Cannot create directory '{directory}': {e}") from e
        self._cache: Dict[str, Table] = {}
    
    def _get_table_path(self, table_name: str) -> Path:
        """Get CSV file path for a table."""
        return self.directory / f"{table_name}.csv"
    
    def _get_schema_path(self, table_name: str) -> Path:
        """Get schema file path for a table."""
        return self.directory / f"{table_name}_schema.json"
    
    def _get_indexes_path(self, table_name: str) -> Path:
        """Get indexes file path for a table."""
        return self.directory / f"{table_name}_indexes.json"
    
    def _load_table(self, table_name: str, force_reload: bool = False) -> Table:
        """Load table from CSV file and restore indexes."""
        if not force_reload and table_name in self._cache:
            return self._cache[table_name]
        
        table_path = self._get_table_path(table_name)
        schema_path = self._get_schema_path(table_name)
        indexes_path = self._get_indexes_path(table_name)
        
        if not table_path.exists():
            raise TableNotFoundError(f"Table '{table_name}' not found")
        
        # Load schema
        try:
            with schema_path.open('r', encoding='utf-8') as f:
                schema_data = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidStorageDataError(f"Invalid JSON in schema file for {table_name}: {e}") from e
        except OSError as e:
            raise DatabaseError(f"Cannot read schema file '{schema_path}': {e}") from e
        
        schema = {}
        for field, type_name in schema_data.items():
            schema[field] = str if type_name == 'str' else int
        
        table = Table(table_name, schema)
        
        # Load indexes if exist
        if indexes_path.exists():
            try:
                with indexes_path.open('r', encoding='utf-8') as f:
                    indexes_data = json.load(f)
                for field_name, index_data in indexes_data.items():
                    for value_str, ids in index_data.items():
                        # Convert value back to original type
                        try:
                            value = int(value_str) if value_str.isdigit() else value_str
                        except ValueError:
                            value = value_str
                        for record_id in ids:
                            if value not in table._indexes.get(field_name, {}):
                                if field_name not in table._indexes:
                                    table._indexes[field_name] = {}
                                table._indexes[field_name][value] = []
                            if record_id not in table._indexes[field_name][value]:
                                table._indexes[field_name][value].append(record_id)
            except (json.JSONDecodeError, OSError) as e:
                raise InvalidStorageDataError(f"Cannot load indexes for {table_name}: {e}") from e
        
        # Load data from CSV
        try:
            with table_path.open('r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    converted_row = {}
                    for field, value in row.items():
                        if field == 'id':
                            continue
                        if field not in schema:
                            raise InvalidStorageDataError(f"Unknown field '{field}' in CSV file for table '{table_name}' at row {row_num}")
                        
                        if schema[field] == int:
                            # Check for empty value
                            if value == '' or value is None:
                                raise InvalidStorageDataError(f"Empty value for integer field '{field}' in table '{table_name}' at row {row_num}")
                            try:
                                converted_row[field] = int(value)
                            except ValueError as e:
                                raise InvalidStorageDataError(f"Invalid integer value '{value}' for field '{field}' in table '{table_name}' at row {row_num}") from e
                        else:
                            converted_row[field] = value
                    try:
                        table.create(converted_row)
                    except ValidationError as e:
                        raise InvalidStorageDataError(f"Validation error in row {row_num} of '{table_name}': {e}") from e
        except OSError as e:
            raise DatabaseError(f"Cannot read CSV file '{table_path}': {e}") from e
        
        self._cache[table_name] = table
        return table
    
    def _save_table(self, table: Table) -> None:
        """Save table to CSV file including schema and indexes."""
        table_path = self._get_table_path(table.name)
        schema_path = self._get_schema_path(table.name)
        indexes_path = self._get_indexes_path(table.name)
        
        # Save schema
        schema_data = {field: 'str' if t == str else 'int' 
                       for field, t in table.schema.items()}
        
        try:
            with schema_path.open('w', encoding='utf-8') as f:
                json.dump(schema_data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise DatabaseError(f"Cannot write schema file '{schema_path}': {e}") from e
        
        # Save indexes
        if table.get_indexes():
            serialized_indexes = {}
            for field_name, index in table.get_indexes().items():
                serialized_indexes[field_name] = {str(k): v for k, v in index.items()}
            try:
                with indexes_path.open('w', encoding='utf-8') as f:
                    json.dump(serialized_indexes, f, ensure_ascii=False, indent=2)
            except OSError as e:
                raise DatabaseError(f"Cannot write indexes file '{indexes_path}': {e}") from e
        else:
            # Remove indexes file if exists but no indexes
            if indexes_path.exists():
                indexes_path.unlink()
        
        # Save data to CSV
        fieldnames = ['id'] + list(table.schema.keys())
        
        try:
            with table_path.open('w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(table.get_all())
        except OSError as e:
            raise DatabaseError(f"Cannot write CSV file '{table_path}': {e}") from e
        
        self._cache[table.name] = table
    
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        """Create a new table with given schema."""
        if self.table_exists(table_name):
            raise TableAlreadyExistsError(f"Table '{table_name}' already exists")
        self._save_table(Table(table_name, schema))
    
    def get_table(self, table_name: str) -> Table:
        """Get a table by name."""
        return self._load_table(table_name)
    
    def get_table_schema(self, table_name: str) -> Dict[str, type]:
        """Get schema of a table."""
        table = self._load_table(table_name)
        return table.schema.copy()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        return self._get_table_path(table_name).exists()
    
    def drop_table(self, table_name: str) -> bool:
        """Delete a table completely."""
        if table_name in self._cache:
            del self._cache[table_name]
        
        deleted = False
        table_path = self._get_table_path(table_name)
        schema_path = self._get_schema_path(table_name)
        indexes_path = self._get_indexes_path(table_name)
        
        if table_path.exists():
            try:
                table_path.unlink()
                deleted = True
            except OSError as e:
                raise DatabaseError(f"Cannot delete file '{table_path}': {e}") from e
        if schema_path.exists():
            try:
                schema_path.unlink()
            except OSError as e:
                raise DatabaseError(f"Cannot delete file '{schema_path}': {e}") from e
        if indexes_path.exists():
            try:
                indexes_path.unlink()
            except OSError as e:
                pass  # Indexes file may not exist
        
        return deleted
    
    def list_tables(self) -> List[str]:
        """List all table names."""
        try:
            return [f.stem for f in self.directory.glob("*.csv")]
        except OSError as e:
            raise DatabaseError(f"Cannot read directory '{self.directory}': {e}") from e
    
    def create_record(self, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new record to the table."""
        table = self._load_table(table_name)
        result = table.create(record)
        self._save_table(table)
        return result
    
    def select_records(self, table_name: str, **filters) -> List[Dict[str, Any]]:
        """Read records with optional filtering."""
        table = self._load_table(table_name)
        return table.read(**filters)
    
    def update_record(self, table_name: str, record_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record by ID."""
        table = self._load_table(table_name)
        result = table.update(record_id, updates)
        self._save_table(table)
        return result
    
    def delete_record(self, table_name: str, record_id: int) -> bool:
        """Delete a record by ID."""
        table = self._load_table(table_name)
        result = table.delete(record_id)
        self._save_table(table)
        return result
    
    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort records by field."""
        table = self._load_table(table_name)
        return table.sort(field, reverse)
    
    def create_index(self, table_name: str, field_name: str) -> None:
        """Create an index on a field."""
        table = self._load_table(table_name)
        table.create_index(field_name)
        self._save_table(table)
    
    def drop_index(self, table_name: str, field_name: str) -> None:
        """Drop an index on a field."""
        table = self._load_table(table_name)
        table.drop_index(field_name)
        self._save_table(table)
    
    def clear_cache(self, table_name: str) -> None:
        """Clear cache for a table to force reload."""
        if table_name in self._cache:
            del self._cache[table_name]