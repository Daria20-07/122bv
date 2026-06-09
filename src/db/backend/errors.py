"""
Custom exceptions for the database module.
"""


class DatabaseError(Exception):
    """Base exception for database errors."""
    pass


class TableNotFoundError(DatabaseError):
    """Raised when accessing a non-existent table."""
    pass


class RecordNotFoundError(DatabaseError):
    """Raised when accessing a non-existent record."""
    pass


class ValidationError(DatabaseError):
    """Raised when data validation fails."""
    pass


class DuplicateIDError(ValidationError):
    """Raised when trying to create a record with duplicate ID."""
    pass


class InvalidFieldTypeError(ValidationError):
    """Raised when field type doesn't match schema."""
    pass


class MissingFieldError(ValidationError):
    """Raised when required field is missing."""
    pass
