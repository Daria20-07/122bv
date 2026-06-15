"""
Abstract database interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Database(ABC):
    """Abstract interface for database implementations."""
    
    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, type]) -> None:
        pass
    
    @abstractmethod
    def get_table(self, table_name: str):
        pass
    
    @abstractmethod
    def get_table_schema(self, table_name: str) -> Dict[str, type]:
        """Get schema of a table."""
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        pass
    
    @abstractmethod
    def drop_table(self, table_name: str) -> bool:
        pass
    
    @abstractmethod
    def list_tables(self) -> List[str]:
        pass
    
    @abstractmethod
    def create_record(self, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def select_records(self, table_name: str, **filters) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def update_record(self, table_name: str, record_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def delete_record(self, table_name: str, record_id: int) -> bool:
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