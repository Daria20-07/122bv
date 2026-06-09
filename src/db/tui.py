"""
Object-oriented Text User Interface for the in-memory database.
"""

from typing import Optional, Dict, Any, List
from .backend.memory import Database, Table
from .backend.errors import (
    DatabaseError,
    TableNotFoundError,
    RecordNotFoundError,
    ValidationError
)


class TUI:
    """Text User Interface for database management."""
    
    def __init__(self):
        """Initialize the TUI with database instance."""
        self.db = Database()
        self.current_table: Optional[Table] = None
    
    def _print_header(self, text: str) -> None:
        """Print a formatted header."""
        print("\n" + text)
        print("-" * 40)
    
    def _print_success(self, message: str) -> None:
        """Print a success message."""
        print(f"[OK] {message}")
    
    def _print_error(self, message: str) -> None:
        """Print an error message."""
        print(f"[ERROR] {message}")
    
    def _print_info(self, message: str) -> None:
        """Print an info message."""
        print(f"[INFO] {message}")
    
    def _read_int(self, prompt: str, allow_empty: bool = False) -> Optional[int]:
        """Read an integer from console input."""
        while True:
            raw = input(prompt).strip()
            
            if allow_empty and raw == "":
                return None
            
            try:
                return int(raw)
            except ValueError:
                self._print_error("Enter a valid integer")
    
    def _read_string(self, prompt: str, allow_empty: bool = False) -> Optional[str]:
        """Read a string from console input."""
        value = input(prompt).strip()
        
        if allow_empty and value == "":
            return None
        
        return value
    
    def _select_table(self, action_name: str) -> Optional[Table]:
        """Select a table from existing tables."""
        tables = self.db.list_tables()
        
        if not tables:
            self._print_error(f"No tables available. Create a table first (option 6)")
            return None
        
        print(f"\nAvailable tables for {action_name}:")
        for i, t in enumerate(tables, 1):
            table = self.db.get_table(t)
            print(f"  {i}. {t} ({table.count()} records)")
        
        choice = self._read_int(f"\nSelect table (1-{len(tables)}): ")
        
        if not choice or choice < 1 or choice > len(tables):
            self._print_error("Invalid choice")
            return None
        
        return self.db.get_table(tables[choice - 1])
    
    def _print_record(self, record: Dict[str, Any]) -> None:
        """Print a single record."""
        print("  " + "-" * 30)
        for key, value in record.items():
            print(f"    {key}: {value}")
        print("  " + "-" * 30)
    
    def _print_records(self, records: List[Dict[str, Any]]) -> None:
        """Print a list of records."""
        if not records:
            self._print_info("No records found")
            return
        
        print(f"\nFound {len(records)} records")
        for record in records:
            self._print_record(record)
    
    def _create_table(self) -> None:
        """Create a new table."""
        self._print_header("Create New Table")
        
        # Get table name
        while True:
            table_name = self._read_string("Table name: ")
            if not table_name:
                self._print_error("Table name cannot be empty")
                continue
            
            if self.db.table_exists(table_name):
                self._print_error(f"Table '{table_name}' already exists")
                continue
            
            break
        
        schema = {}
        field_count = 0
        
        self._print_info("Define table structure")
        self._print_info("Enter 'done' to finish adding fields")
        
        while True:
            print(f"\n--- Field {field_count + 1} ---")
            field_name = self._read_string("Field name: ")
            
            if not field_name:
                self._print_error("Field name cannot be empty")
                continue
            
            if field_name.lower() == 'done':
                if field_count == 0:
                    self._print_error("Add at least one field")
                    continue
                break
            
            if field_name == 'id':
                self._print_error("Field 'id' is auto-generated")
                continue
            
            print("Field type:")
            print("  1. str (string)")
            print("  2. int (integer)")
            
            type_choice = self._read_int("Choose type (1-2): ")
            
            if type_choice == 1:
                schema[field_name] = str
                field_count += 1
                self._print_success(f"Field '{field_name}' (string) added")
            elif type_choice == 2:
                schema[field_name] = int
                field_count += 1
                self._print_success(f"Field '{field_name}' (integer) added")
            else:
                self._print_error("Invalid choice")
        
        try:
            self.db.create_table(table_name, schema)
            self._print_success(f"Table '{table_name}' created")
        except ValidationError as e:
            self._print_error(str(e))
    
    def _add_record(self) -> None:
        """Add a new record."""
        table = self._select_table("adding record")
        if not table:
            return
        
        self._print_header(f"Add Record to '{table.name}'")
        
        record = {}
        for field, field_type in table.schema.items():
            while True:
                if field_type == int:
                    value = self._read_int(f"  {field}: ")
                else:
                    value = self._read_string(f"  {field}: ")
                
                if value is None:
                    continue
                
                record[field] = value
                break
        
        try:
            new_record = table.create(record)
            self._print_success(f"Record added. ID = {new_record['id']}")
            self._print_record(new_record)
        except ValidationError as e:
            self._print_error(str(e))
    
    def _read_records(self) -> None:
        """Read records with filters."""
        table = self._select_table("viewing records")
        if not table:
            return
        
        self._print_header(f"View Records in '{table.name}'")
        
        print("\nFilters (Enter to skip):")
        filters = {}
        for field, field_type in table.schema.items():
            if field_type == int:
                value = self._read_int(f"  {field}: ", allow_empty=True)
            else:
                value = self._read_string(f"  {field}: ", allow_empty=True)
            
            if value is not None:
                filters[field] = value
        
        records = table.read(**filters)
        self._print_records(records)
    
    def _sort_records(self) -> None:
        """Sort records by field."""
        table = self._select_table("sorting records")
        if not table:
            return
        
        if table.count() == 0:
            self._print_info("Table is empty")
            return
        
        self._print_header(f"Sort Records in '{table.name}'")
        
        # Get first record to see available fields
        sample = table.get_all()[0]
        fields = [f for f in sample.keys() if f != 'id']
        
        print("\nFields for sorting:")
        for i, field in enumerate(fields, 1):
            print(f"  {i}. {field}")
        
        choice = self._read_int(f"\nSelect field (1-{len(fields)}): ")
        if not choice or choice < 1 or choice > len(fields):
            self._print_error("Invalid choice")
            return
        
        field = fields[choice - 1]
        
        print("\nOrder:")
        print("  1. Ascending")
        print("  2. Descending")
        
        order = self._read_int("Choose (1-2): ")
        reverse = (order == 2)
        
        try:
            sorted_records = table.sort(field, reverse=reverse)
            self._print_success(f"Sorted by '{field}'")
            self._print_records(sorted_records)
        except ValidationError as e:
            self._print_error(str(e))
    
    def _update_record(self) -> None:
        """Update a record."""
        table = self._select_table("updating record")
        if not table:
            return
        
        self._print_header(f"Update Record in '{table.name}'")
        
        record_id = self._read_int("Record ID: ")
        if record_id is None:
            return
        
        try:
            records = table.read(id=record_id)
            if not records:
                self._print_error(f"Record {record_id} not found")
                return
            
            self._print_info("Current record:")
            self._print_record(records[0])
            
            updates = {}
            print("\nNew values (Enter to keep):")
            for field, field_type in table.schema.items():
                current = records[0][field]
                if field_type == int:
                    value = self._read_int(f"  {field} [{current}]: ", allow_empty=True)
                else:
                    value = self._read_string(f"  {field} [{current}]: ", allow_empty=True)
                
                if value is not None:
                    updates[field] = value
            
            if updates:
                updated = table.update(record_id, updates)
                self._print_success("Record updated")
                self._print_record(updated)
            else:
                self._print_info("No changes")
                
        except (RecordNotFoundError, ValidationError) as e:
            self._print_error(str(e))
    
    def _delete_record(self) -> None:
        """Delete a record."""
        table = self._select_table("deleting record")
        if not table:
            return
        
        self._print_header(f"Delete Record from '{table.name}'")
        
        record_id = self._read_int("Record ID: ")
        if record_id is None:
            return
        
        try:
            records = table.read(id=record_id)
            if not records:
                self._print_error(f"Record {record_id} not found")
                return
            
            self._print_info("Record to delete:")
            self._print_record(records[0])
            
            confirm = input(f"\nDelete record {record_id}? (y/N): ").strip().lower()
            if confirm == 'y':
                table.delete(record_id)
                self._print_success(f"Record {record_id} deleted")
            else:
                self._print_info("Cancelled")
                
        except RecordNotFoundError as e:
            self._print_error(str(e))
    
    def _list_tables(self) -> None:
        """List all tables."""
        self._print_header("List of Tables")
        
        tables = self.db.list_tables()
        if not tables:
            self._print_info("No tables")
            return
        
        for i, name in enumerate(tables, 1):
            table = self.db.get_table(name)
            print(f"{i}. {name} - {table.count()} records")
            print(f"   Fields: {', '.join(table.schema.keys())}")
    
    def _clear_table(self) -> None:
        """Clear all records from a table."""
        table = self._select_table("clearing")
        if not table:
            return
        
        count = table.count()
        if count == 0:
            self._print_info("Table is empty")
            return
        
        confirm = input(f"\nClear '{table.name}' ({count} records)? (y/N): ").strip().lower()
        if confirm == 'y':
            table.clear()
            self._print_success(f"Table '{table.name}' cleared")
    
    def _drop_table(self) -> None:
        """Delete a table."""
        tables = self.db.list_tables()
        if not tables:
            self._print_error("No tables")
            return
        
        self._print_header("Delete Table")
        for i, name in enumerate(tables, 1):
            table = self.db.get_table(name)
            print(f"{i}. {name} ({table.count()} records)")
        
        choice = self._read_int("\nSelect table: ")
        if not choice or choice < 1 or choice > len(tables):
            self._print_error("Invalid choice")
            return
        
        table_name = tables[choice - 1]
        confirm = input(f"Delete '{table_name}'? (y/N): ").strip().lower()
        if confirm == 'y':
            self.db.drop_table(table_name)
            self._print_success(f"Table '{table_name}' deleted")
    
    def _print_menu(self) -> None:
        """Print main menu."""
        self._print_header("In-Memory Database")
        
        print("\nDATA OPERATIONS:")
        print("  1. Add record (CREATE)")
        print("  2. View records (READ)")
        print("  3. Update record (UPDATE)")
        print("  4. Delete record (DELETE)")
        print("  5. Sort records (SORT)")
        
        print("\nTABLE MANAGEMENT:")
        print("  6. Create table")
        print("  7. Delete table")
        print("  8. Clear table")
        print("  9. List tables")
        
        print("\n  0. Exit")
        
        # Statistics
        tables = self.db.list_tables()
        print(f"\n[STATUS] {len(tables)} table(s)")
        for name in tables:
            table = self.db.get_table(name)
            print(f"         - {name}: {table.count()} records")
    
    def run(self) -> None:
        """Main loop."""
        self._print_header("Welcome to In-Memory Database")
        self._print_info("OOP version with full CRUD + Sort")
        
        while True:
            self._print_menu()
            choice = self._read_int("\nChoice: ")
            
            if choice == 1:
                self._add_record()
            elif choice == 2:
                self._read_records()
            elif choice == 3:
                self._update_record()
            elif choice == 4:
                self._delete_record()
            elif choice == 5:
                self._sort_records()
            elif choice == 6:
                self._create_table()
            elif choice == 7:
                self._drop_table()
            elif choice == 8:
                self._clear_table()
            elif choice == 9:
                self._list_tables()
            elif choice == 0:
                self._print_info("Goodbye!")
                break
            else:
                self._print_error("Invalid choice")
            
            if choice != 0:
                input("\nPress Enter...")


def run() -> None:
    """Entry point."""
    app = TUI()
    app.run()