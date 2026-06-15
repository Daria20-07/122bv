"""
Abstract database interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Database(ABC):
    """Abstract interface for database implementations."""
    
    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        """Create a new table with given schema."""
        pass
    
    @abstractmethod
    def get_table(self, table_name: str):
        """Get a table by name."""
        pass
    
    @abstractmethod
    def get_table_schema(self, table_name: str) -> Dict[str, type]:
        """Get schema of a table."""
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        pass
    
    @abstractmethod
    def drop_table(self, table_name: str) -> bool:
        """Delete a table."""
        pass
    
    @abstractmethod
    def list_tables(self) -> List[str]:
        """List all table names."""
        pass
    
    @abstractmethod
    def create_record(self, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new record."""
        pass
    
    @abstractmethod
    def select_records(self, table_name: str, **filters) -> List[Dict[str, Any]]:
        """Read records with filters."""
        pass
    
    @abstractmethod
    def update_record(self, table_name: str, record_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record by ID."""
        pass
    
    @abstractmethod
    def delete_record(self, table_name: str, record_id: int) -> bool:
        """Delete a record by ID."""
        pass
    
    @abstractmethod
    def sort_records(self, table_name: str, field: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort records by field."""
        pass
    
    @abstractmethod
    def create_index(self, table_name: str, field_name: str) -> None:
        """Create an index on a field."""
        pass
    
    @abstractmethod
    def drop_index(self, table_name: str, field_name: str) -> None:
        """Drop an index on a field."""
        pass