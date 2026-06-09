"""
Custom exceptions for the database module.
"""


class DatabaseError(Exception):
    """Base exception for database errors."""
    pass


class TableNotFoundError(DatabaseError):
    """Raised when accessing a non-existent table."""
    pass


class TableAlreadyExistsError(DatabaseError):
    """Raised when trying to create a table that already exists."""
    pass


class RecordNotFoundError(DatabaseError):
    """Raised when accessing a non-existent record."""
    pass


class DuplicateIDError(DatabaseError):
    """Raised when trying to create a record with duplicate ID."""
    pass


class ValidationError(DatabaseError):
    """Raised when data validation fails."""
    pass


class InvalidFieldTypeError(ValidationError):
    """Raised when field type doesn't match schema."""
    pass


class MissingFieldError(ValidationError):
    """Raised when required field is missing."""
    pass


class InvalidStorageDataError(DatabaseError):
    """Raised when reading corrupted data from file."""
    pass


class IndexError(DatabaseError):
    """Raised when index operations fail."""
    pass