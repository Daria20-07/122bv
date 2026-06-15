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
        for record in self._data:
            if field_name in record:
                value = record[field_name]
                record_id = record['id']
                if value not in self._indexes[field_name]:
                    self._indexes[field_name][value] = []
                if record_id not in self._indexes[field_name][value]:
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
        """Read records with optional filtering using indexes when possible."""
        if not filters:
            return [record.copy() for record in self._data]
        
        # Validate filter fields against schema
        for field in filters:
            if field not in self.schema and field != 'id':
                raise InvalidFieldTypeError(f"Unknown filter field: {field}")
        
        # Find the best index to use (the one with smallest candidate set)
        best_index_field = None
        best_index_value = None
        best_index_size = None
        
        for field, value in filters.items():
            if field in self._indexes and value in self._indexes[field]:
                candidate_size = len(self._indexes[field][value])
                if best_index_size is None or candidate_size < best_index_size:
                    best_index_field = field
                    best_index_value = value
                    best_index_size = candidate_size
        
        # If we have a good index, use it as starting point
        if best_index_field is not None:
            result_ids = self._indexes[best_index_field][best_index_value]
            result = []
            for record in self._data:
                if record.get('id') in result_ids:
                    # Check all filters match
                    match = all(record.get(f) == v for f, v in filters.items())
                    if match:
                        result.append(record.copy())
            return result
        
        # Fallback to linear scan
        result = []
        for record in self._data:
            match = True
            for field, value in filters.items():
                if record.get(field) != value:
                    match = False
                    break
            if match:
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
        """Get all records."""
        return [record.copy() for record in self._data]
    
    def count(self) -> int:
        """Get number of records."""
        return len(self._data)
    
    def clear(self) -> None:
        """Remove all records."""
        self._data.clear()
        self._next_id = 1
        self._indexes.clear()
    
    def sort(self, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort records by field. Check field against schema."""
        if field not in self.schema and field != 'id':
            raise ValidationError(f"Cannot sort by unknown field: {field}")
        
        if not self._data:
            return []
        
        return sorted(self._data, key=lambda x: x.get(field), reverse=reverse)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table to dictionary for serialization (including indexes)."""
        serialized_indexes = {}
        for field_name, index in self._indexes.items():
            serialized_indexes[field_name] = {str(k): v for k, v in index.items()}
        
        return {
            'name': self.name,
            'schema': {k: v.__name__ for k, v in self.schema.items()},
            'data': self._data,
            'next_id': self._next_id,
            'indexes': serialized_indexes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        """Create table from dictionary (including indexes)."""
        schema = {}
        for field, type_name in data['schema'].items():
            schema[field] = str if type_name == 'str' else int
        
        table = cls(data['name'], schema)
        table._data = data['data']
        table._next_id = data['next_id']
        
        # Restore indexes
        if 'indexes' in data:
            for field_name, index_data in data['indexes'].items():
                index = {}
                for str_key, ids in index_data.items():
                    try:
                        key = int(str_key) if str_key.isdigit() else str_key
                    except ValueError:
                        key = str_key
                    index[key] = ids
                table._indexes[field_name] = index
        
        return table