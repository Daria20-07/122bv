"""
Object-oriented in-memory database implementation.
Provides CRUD operations with multiple table support.
"""

from typing import Any, Dict, List, Optional
from copy import deepcopy
from .errors import (
    TableNotFoundError,
    RecordNotFoundError,
    DuplicateIDError,
    InvalidFieldTypeError,
    MissingFieldError,
    ValidationError
)


class Table:
    """
    Represents a database table with dynamic schema.
    """
    
    def __init__(self, name: str, schema: Dict[str, type]):
        """
        Initialize a new table.
        
        Args:
            name: Table name
            schema: Dictionary mapping field names to their expected types
        """
        self.name = name
        self.schema = schema
        self._data: List[Dict[str, Any]] = []
        self._next_id = 1
    
    def _validate_record(self, record: Dict[str, Any]) -> None:
        """
        Validate record against schema.
        
        Args:
            record: Record to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Check for required fields
        for field in self.schema:
            if field not in record:
                raise MissingFieldError(f"Missing required field: {field}")
        
        # Check field types
        for field, value in record.items():
            if field not in self.schema:
                if field != 'id':
                    raise InvalidFieldTypeError(f"Unknown field: {field}")
            else:
                expected_type = self.schema[field]
                if not isinstance(value, expected_type):
                    raise InvalidFieldTypeError(
                        f"Field '{field}' must be {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
    
    def create(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new record to the table.
        
        Args:
            record: Record data without 'id' field
            
        Returns:
            Created record with auto-generated ID
        """
        self._validate_record(record)
        
        new_record = record.copy()
        new_record['id'] = self._next_id
        self._next_id += 1
        self._data.append(new_record)
        
        return new_record.copy()
    
    def read(self, **filters) -> List[Dict[str, Any]]:
        """
        Read records with optional filtering.
        
        Args:
            **filters: Field-value pairs for filtering
            
        Returns:
            List of matching records
        """
        if not filters:
            return [record.copy() for record in self._data]
        
        result = []
        for record in self._data:
            match = True
            for field, value in filters.items():
                if field not in record or record[field] != value:
                    match = False
                    break
            if match:
                result.append(record.copy())
        
        return result
    
    def update(self, record_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a record by ID.
        
        Args:
            record_id: ID of record to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated record
            
        Raises:
            RecordNotFoundError: If record not found
        """
        for i, record in enumerate(self._data):
            if record['id'] == record_id:
                updated_record = record.copy()
                updated_record.update(updates)
                self._validate_record(updated_record)
                self._data[i] = updated_record
                return updated_record.copy()
        
        raise RecordNotFoundError(f"Record with ID {record_id} not found")
    
    def delete(self, record_id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            record_id: ID of record to delete
            
        Returns:
            True if deleted
            
        Raises:
            RecordNotFoundError: If record not found
        """
        for i, record in enumerate(self._data):
            if record['id'] == record_id:
                self._data.pop(i)
                return True
        
        raise RecordNotFoundError(f"Record with ID {record_id} not found")
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all records."""
        return [record.copy() for record in self._data]
    
    def count(self) -> int:
        """Get number of records."""
        return len(self._data)
    
    def clear(self) -> None:
        """Remove all records."""
        self._data.clear()
        self._next_id = 1
    
    def sort(self, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Sort records by field.
        
        Args:
            field: Field name to sort by
            reverse: True for descending, False for ascending
            
        Returns:
            Sorted list of records
        """
        if not self._data:
            return []
        
        if field not in self._data[0]:
            raise ValidationError(f"Cannot sort by unknown field: {field}")
        
        return sorted(self._data, key=lambda x: x[field], reverse=reverse)


class Database:
    """
    In-memory database supporting multiple tables.
    """
    
    def __init__(self):
        """Initialize empty database."""
        self._tables: Dict[str, Table] = {}
    
    def create_table(self, name: str, schema: Dict[str, type]) -> Table:
        """
        Create a new table.
        
        Args:
            name: Table name
            schema: Dictionary mapping field names to their expected types
            
        Returns:
            Created Table object
            
        Raises:
            ValidationError: If table already exists
        """
        if name in self._tables:
            raise ValidationError(f"Table '{name}' already exists")
        
        table = Table(name, schema)
        self._tables[name] = table
        return table
    
    def get_table(self, name: str) -> Table:
        """
        Get a table by name.
        
        Args:
            name: Table name
            
        Returns:
            Table object
            
        Raises:
            TableNotFoundError: If table not found
        """
        if name not in self._tables:
            raise TableNotFoundError(f"Table '{name}' not found")
        
        return self._tables[name]
    
    def drop_table(self, name: str) -> bool:
        """
        Remove a table.
        
        Args:
            name: Table name
            
        Returns:
            True if deleted
        """
        if name in self._tables:
            del self._tables[name]
            return True
        return False
    
    def list_tables(self) -> List[str]:
        """Get list of all table names."""
        return list(self._tables.keys())
    
    def table_exists(self, name: str) -> bool:
        """Check if table exists."""
        return name in self._tables