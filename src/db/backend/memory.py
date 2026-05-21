"""
In-memory database implementation without classes.
Provides CRUD operations for managing multiple tables in RAM.
"""

from typing import Any, Optional, Dict, List, Tuple

# Global storage structure: {table_name: {'schema': {...}, 'data': [...], 'next_id': int}}
_tables: Dict[str, Dict[str, Any]] = {}


def _validate_record(record: Dict[str, Any], schema: Dict[str, type]) -> None:
    """
    Validate record against schema.
    
    Args:
        record: Record to validate
        schema: Table schema with field types
        
    Raises:
        ValueError: If validation fails
    """
    # Check for required fields
    for field, field_type in schema.items():
        if field not in record:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(record[field], field_type):
            raise ValueError(
                f"Field '{field}' must be of type {field_type.__name__}, "
                f"got {type(record[field]).__name__}"
            )
    
    # Check for extra fields (except 'id')
    for field in record:
        if field not in schema and field != 'id':
            raise ValueError(f"Unknown field: {field}")


def create_table(table_name: str, schema: Dict[str, type]) -> None:
    """
    Create a new table in the database.
    
    Args:
        table_name: Name of the table
        schema: Dictionary mapping field names to their expected types
        
    Raises:
        ValueError: If table already exists
    """
    if table_name in _tables:
        raise ValueError(f"Table '{table_name}' already exists")
    
    _tables[table_name] = {
        'schema': schema,
        'data': [],
        'next_id': 1
    }


def drop_table(table_name: str) -> bool:
    """
    Remove a table from the database.
    
    Args:
        table_name: Name of the table to remove
        
    Returns:
        True if deleted, False if not found
    """
    if table_name in _tables:
        del _tables[table_name]
        return True
    return False


def list_tables() -> List[str]:
    """
    Get list of all table names.
    
    Returns:
        List of table names
    """
    return list(_tables.keys())


def table_exists(table_name: str) -> bool:
    """
    Check if a table exists.
    
    Args:
        table_name: Name of the table to check
        
    Returns:
        True if table exists, False otherwise
    """
    return table_name in _tables


def get_table_schema(table_name: str) -> Optional[Dict[str, type]]:
    """
    Get schema of a table.
    
    Args:
        table_name: Name of the table
        
    Returns:
        Schema dictionary or None if table not found
    """
    if table_name not in _tables:
        return None
    return _tables[table_name]['schema'].copy()


def create_record(table_name: str, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Add a new record to the specified table.
    
    Args:
        table_name: Name of the table
        record: Record data without 'id' field
        
    Returns:
        Created record with auto-generated ID, or None if table not found
        
    Raises:
        ValueError: If validation fails
    """
    if table_name not in _tables:
        raise ValueError(f"Table '{table_name}' does not exist")
    
    table = _tables[table_name]
    schema = table['schema']
    
    # Validate record
    _validate_record(record, schema)
    
    # Create new record with ID
    new_record = record.copy()
    new_record['id'] = table['next_id']
    table['next_id'] += 1
    
    # Add to storage
    table['data'].append(new_record)
    
    return new_record.copy()


def select_records(table_name: str, **filters) -> List[Dict[str, Any]]:
    """
    Select records from table with optional filtering.
    
    Args:
        table_name: Name of the table
        **filters: Field-value pairs for filtering
        
    Returns:
        List of matching records, empty list if table not found
    """
    if table_name not in _tables:
        return []
    
    table = _tables[table_name]
    data = table['data']
    
    if not filters:
        return [record.copy() for record in data]
    
    result = []
    for record in data:
        match = True
        for field, value in filters.items():
            if field not in record or record[field] != value:
                match = False
                break
        if match:
            result.append(record.copy())
    
    return result


def update_record(table_name: str, record_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a record by ID.
    
    Args:
        table_name: Name of the table
        record_id: ID of record to update
        updates: Dictionary of fields to update
        
    Returns:
        Updated record, None if record not found or table doesn't exist
        
    Raises:
        ValueError: If validation fails
    """
    if table_name not in _tables:
        raise ValueError(f"Table '{table_name}' does not exist")
    
    table = _tables[table_name]
    schema = table['schema']
    data = table['data']
    
    # Find and update record
    for i, record in enumerate(data):
        if record['id'] == record_id:
            # Create updated record
            updated_record = record.copy()
            updated_record.update(updates)
            
            # Validate updated record
            _validate_record(updated_record, schema)
            
            # Update storage
            data[i] = updated_record
            return updated_record.copy()
    
    return None


def delete_record(table_name: str, record_id: int) -> bool:
    """
    Delete a record by ID.
    
    Args:
        table_name: Name of the table
        record_id: ID of record to delete
        
    Returns:
        True if deleted, False if record not found or table doesn't exist
    """
    if table_name not in _tables:
        return False
    
    table = _tables[table_name]
    data = table['data']
    
    for i, record in enumerate(data):
        if record['id'] == record_id:
            data.pop(i)
            return True
    
    return False


def get_all_records(table_name: str) -> List[Dict[str, Any]]:
    """
    Get all records from a table.
    
    Args:
        table_name: Name of the table
        
    Returns:
        List of all records, empty list if table not found
    """
    if table_name not in _tables:
        return []
    
    return [record.copy() for record in _tables[table_name]['data']]


def get_record_count(table_name: str) -> int:
    """
    Get number of records in a table.
    
    Args:
        table_name: Name of the table
        
    Returns:
        Record count, 0 if table not found
    """
    if table_name not in _tables:
        return 0
    
    return len(_tables[table_name]['data'])


def clear_table(table_name: str) -> bool:
    """
    Remove all records from a table.
    
    Args:
        table_name: Name of the table
        
    Returns:
        True if cleared, False if table not found
    """
    if table_name not in _tables:
        return False
    
    _tables[table_name]['data'] = []
    _tables[table_name]['next_id'] = 1
    return True