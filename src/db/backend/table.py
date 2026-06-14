"""
Table class representing database table structure and operations.
"""

from typing import Any, Dict, List, Optional
from .errors import MissingFieldError, InvalidFieldTypeError, RecordNotFoundError, ValidationError


class Table:
    """Represents a database table with fixed schema."""
    
    def __init__(self, name: str, schema: Dict[str, type]):
        self.name = name
        self.schema = schema
        self._data: List[Dict[str, Any]] = []
        self._next_id = 1
        self._indexes: Dict[str, Dict[Any, List[int]]] = {}
    
    def _validate_record(self, record: Dict[str, Any]) -> None:
        """Validate record against schema."""
        for field in self.schema:
            if field not in record:
                raise MissingFieldError(f"Missing required field: {field}")
        
        for field, value in record.items():
            if field not in self.schema and field != 'id':
                raise InvalidFieldTypeError(f"Unknown field: {field}")
            elif field in self.schema:
                expected_type = self.schema[field]
                if not isinstance(value, expected_type):
                    raise InvalidFieldTypeError(
                        f"Field '{field}' must be {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
    
    def _update_indexes(self, record_id: int, record: Dict[str, Any], is_delete: bool = False) -> None:
        """Update indexes for a record."""
        for field_name, index in self._indexes.items():
            if field_name in record:
                value = record[field_name]
                if is_delete:
                    if value in index and record_id in index[value]:
                        index[value].remove(record_id)
                        if not index[value]:
                            del index[value]
                else:
                    if value not in index:
                        index[value] = []
                    if record_id not in index[value]:
                        index[value].append(record_id)
    
    def create_index(self, field_name: str) -> None:
        """Create an index on a field."""
        if field_name not in self.schema:
            raise ValidationError(f"Cannot index unknown field: {field_name}")
        
        if field_name in self._indexes:
            return
        
        self._indexes[field_name] = {}
        for idx, record in enumerate(self._data):
            if field_name in record:
                value = record[field_name]
                record_id = record.get('id', idx + 1)
                if value not in self._indexes[field_name]:
                    self._indexes[field_name][value] = []
                self._indexes[field_name][value].append(record_id)
    
    def drop_index(self, field_name: str) -> None:
        """Drop an index on a field."""
        if field_name in self._indexes:
            del self._indexes[field_name]
    
    def get_indexes(self) -> Dict[str, Dict[Any, List[int]]]:
        """Get all indexes."""
        return self._indexes.copy()
    
    def create(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new record."""
        self._validate_record(record)
        
        new_record = record.copy()
        new_record['id'] = self._next_id
        self._next_id += 1
        self._data.append(new_record)
        self._update_indexes(new_record['id'], new_record)
        
        return new_record.copy()
    
    def read(self, **filters) -> List[Dict[str, Any]]:
        """Read records with optional filtering."""
        if not filters:
            return [record.copy() for record in self._data]
        
        # Try to use index
        for field, value in filters.items():
            if field in self._indexes and value in self._indexes[field]:
                result_ids = self._indexes[field][value]
                result = []
                for record in self._data:
                    if record.get('id') in result_ids:
                        match = all(record.get(f) == v for f, v in filters.items())
                        if match:
                            result.append(record.copy())
                return result
        
        # Fallback to linear scan
        result = []
        for record in self._data:
            if all(record.get(field) == value for field, value in filters.items()):
                result.append(record.copy())
        return result
    
    def update(self, record_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record by ID."""
        for i, record in enumerate(self._data):
            if record['id'] == record_id:
                updated_record = record.copy()
                updated_record.update(updates)
                self._validate_record(updated_record)
                
                self._update_indexes(record_id, record, is_delete=True)
                self._data[i] = updated_record
                self._update_indexes(record_id, updated_record)
                
                return updated_record.copy()
        
        raise RecordNotFoundError(f"Record with ID {record_id} not found")
    
    def delete(self, record_id: int) -> bool:
        """Delete a record by ID."""
        for i, record in enumerate(self._data):
            if record['id'] == record_id:
                self._update_indexes(record_id, record, is_delete=True)
                self._data.pop(i)
                return True
        
        raise RecordNotFoundError(f"Record with ID {record_id} not found")
    
    def get_all(self) -> List[Dict[str, Any]]:
        return [record.copy() for record in self._data]
    
    def count(self) -> int:
        return len(self._data)
    
    def clear(self) -> None:
        self._data.clear()
        self._next_id = 1
        self._indexes.clear()
    
    def sort(self, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        if not self._data:
            return []
        if field not in self._data[0]:
            raise ValidationError(f"Cannot sort by unknown field: {field}")
        return sorted(self._data, key=lambda x: x[field], reverse=reverse)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table to dictionary for serialization."""
        return {
            'name': self.name,
            'schema': {k: v.__name__ for k, v in self.schema.items()},
            'data': self._data,
            'next_id': self._next_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        """Create table from dictionary."""
        schema = {}
        for field, type_name in data['schema'].items():
            schema[field] = str if type_name == 'str' else int
        
        table = cls(data['name'], schema)
        table._data = data['data']
        table._next_id = data['next_id']
        
        for record in table._data:
            table._update_indexes(record['id'], record)
        
        return table