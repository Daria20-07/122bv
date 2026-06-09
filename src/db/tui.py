"""
Object-oriented Text User Interface for the database.
Supports Memory, JSON File, and CSV File backends.
"""

from typing import Optional, Dict, Any, List
from .backend.database import Database
from .backend.memory import MemoryDatabase
from .backend.file import FileDatabase
from .backend.csvdb import CSVDatabase
from .backend.errors import DatabaseError, RecordNotFoundError, ValidationError


class TUI:
    def __init__(self):
        self.database = self._select_database()
    
    def _select_database(self) -> Database:
        print("\n" + "=" * 50)
        print("  Database Selection")
        print("=" * 50)
        print("\nSelect storage backend:")
        print("  1. In-Memory Database (data lost after exit)")
        print("  2. JSON File Database (data saved to JSON files)")
        print("  3. CSV File Database (data saved to CSV files)")
        print("\n" + "-" * 50)
        
        while True:
            choice = input("\nEnter choice (1-3): ").strip()
            if choice == "1":
                print("[INFO] Using In-Memory Database")
                return MemoryDatabase()
            elif choice == "2":
                print("[INFO] Using JSON File Database")
                return FileDatabase("data")
            elif choice == "3":
                print("[INFO] Using CSV File Database")
                return CSVDatabase("data_csv")
            else:
                print("[ERROR] Invalid choice")
    
    def _print_header(self, text: str) -> None:
        print("\n" + text)
        print("-" * 40)
    
    def _print_success(self, message: str) -> None:
        print(f"[OK] {message}")
    
    def _print_error(self, message: str) -> None:
        print(f"[ERROR] {message}")
    
    def _print_info(self, message: str) -> None:
        print(f"[INFO] {message}")
    
    def _read_int(self, prompt: str, allow_empty: bool = False) -> Optional[int]:
        while True:
            raw = input(prompt).strip()
            if allow_empty and raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                self._print_error("Enter a valid integer")
    
    def _read_string(self, prompt: str, allow_empty: bool = False) -> Optional[str]:
        value = input(prompt).strip()
        if allow_empty and value == "":
            return None
        return value
    
    def _select_table(self, action_name: str) -> Optional[str]:
        tables = self.database.list_tables()
        if not tables:
            self._print_error(f"No tables available. Create a table first")
            return None
        
        print(f"\nAvailable tables for {action_name}:")
        for i, t in enumerate(tables, 1):
            try:
                count = len(self.database.select_records(t))
                print(f"  {i}. {t} ({count} records)")
            except:
                print(f"  {i}. {t}")
        
        choice = self._read_int(f"\nSelect table (1-{len(tables)}): ")
        if not choice or choice < 1 or choice > len(tables):
            self._print_error("Invalid choice")
            return None
        
        return tables[choice - 1]
    
    def _print_record(self, record: Dict[str, Any]) -> None:
        print("  " + "-" * 30)
        for key, value in record.items():
            print(f"    {key}: {value}")
        print("  " + "-" * 30)
    
    def _print_records(self, records: List[Dict[str, Any]]) -> None:
        if not records:
            self._print_info("No records found")
            return
        print(f"\nFound {len(records)} records")
        for record in records:
            self._print_record(record)
    
    def _create_table(self) -> None:
        self._print_header("Create New Table")
        
        while True:
            table_name = self._read_string("Table name: ")
            if not table_name:
                self._print_error("Table name cannot be empty")
                continue
            if self.database.table_exists(table_name):
                self._print_error(f"Table '{table_name}' already exists")
                continue
            break
        
        schema = {}
        field_count = 0
        
        self._print_info("Define table structure (enter 'done' to finish)")
        
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
            
            print("Field type:\n  1. str\n  2. int")
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
            self.database.create_table(table_name, schema)
            self._print_success(f"Table '{table_name}' created")
        except DatabaseError as e:
            self._print_error(str(e))
    
    def _add_record(self) -> None:
        table_name = self._select_table("adding record")
        if not table_name:
            return
        
        self._print_header(f"Add Record to '{table_name}'")
        
        # Try to get schema from existing records
        try:
            records = self.database.select_records(table_name)
            if records:
                schema = {k: type(v) for k, v in records[0].items() if k != 'id'}
            else:
                fields_input = self._read_string("Fields (comma-separated): ")
                if not fields_input:
                    self._print_error("At least one field required")
                    return
                schema = {f.strip(): str for f in fields_input.split(',')}
        except:
            self._print_error("Could not determine table schema")
            return
        
        record = {}
        for field in schema:
            while True:
                if schema[field] == int:
                    value = self._read_int(f"  {field}: ")
                else:
                    value = self._read_string(f"  {field}: ")
                
                if value is None:
                    continue
                record[field] = value
                break
        
        try:
            new_record = self.database.create_record(table_name, record)
            self._print_success(f"Record added. ID = {new_record['id']}")
            self._print_record(new_record)
        except DatabaseError as e:
            self._print_error(str(e))
    
    def _read_records(self) -> None:
        table_name = self._select_table("viewing records")
        if not table_name:
            return
        
        self._print_header(f"View Records in '{table_name}'")
        print("\nFilters (Enter to skip):")
        
        filters = {}
        while True:
            field = self._read_string("Field name (or 'done'): ")
            if not field or field.lower() == 'done':
                break
            value = self._read_string(f"Value for {field}: ")
            if value is not None:
                filters[field] = value
        
        try:
            records = self.database.select_records(table_name, **filters)
            self._print_records(records)
        except DatabaseError as e:
            self._print_error(str(e))
    
    def _update_record(self) -> None:
        table_name = self._select_table("updating record")
        if not table_name:
            return
        
        self._print_header(f"Update Record in '{table_name}'")
        
        record_id = self._read_int("Record ID: ")
        if record_id is None:
            return
        
        try:
            records = self.database.select_records(table_name, id=record_id)
            if not records:
                self._print_error(f"Record {record_id} not found")
                return
            
            self._print_info("Current record:")
            self._print_record(records[0])
            
            updates = {}
            print("\nNew values (Enter to keep):")
            for field, value in records[0].items():
                if field == 'id':
                    continue
                new_value = self._read_string(f"  {field} [{value}]: ", allow_empty=True)
                if new_value:
                    if isinstance(value, int):
                        try:
                            updates[field] = int(new_value)
                        except ValueError:
                            self._print_error(f"Invalid integer for {field}")
                            return
                    else:
                        updates[field] = new_value
            
            if updates:
                updated = self.database.update_record(table_name, record_id, updates)
                self._print_success("Record updated")
                self._print_record(updated)
            else:
                self._print_info("No changes")
        except DatabaseError as e:
            self._print_error(str(e))
    
    def _delete_record(self) -> None:
        table_name = self._select_table("deleting record")
        if not table_name:
            return
        
        self._print_header(f"Delete Record from '{table_name}'")
        
        record_id = self._read_int("Record ID: ")
        if record_id is None:
            return
        
        try:
            records = self.database.select_records(table_name, id=record_id)
            if not records:
                self._print_error(f"Record {record_id} not found")
                return
            
            self._print_info("Record to delete:")
            self._print_record(records[0])
            
            confirm = input(f"\nDelete record {record_id}? (y/N): ").strip().lower()
            if confirm == 'y':
                self.database.delete_record(table_name, record_id)
                self._print_success(f"Record {record_id} deleted")
            else:
                self._print_info("Cancelled")
        except DatabaseError as e:
            self._print_error(str(e))
    
    def _list_tables(self) -> None:
        self._print_header("List of Tables")
        tables = self.database.list_tables()
        
        if not tables:
            self._print_info("No tables")
            return
        
        for i, name in enumerate(tables, 1):
            try:
                count = len(self.database.select_records(name))
                print(f"{i}. {name} - {count} records")
            except:
                print(f"{i}. {name}")
    
    def _drop_table(self) -> None:
        tables = self.database.list_tables()
        if not tables:
            self._print_error("No tables")
            return
        
        self._print_header("Delete Table")
        for i, name in enumerate(tables, 1):
            print(f"{i}. {name}")
        
        choice = self._read_int("\nSelect table: ")
        if not choice or choice < 1 or choice > len(tables):
            self._print_error("Invalid choice")
            return
        
        table_name = tables[choice - 1]
        confirm = input(f"Delete '{table_name}'? (y/N): ").strip().lower()
        if confirm == 'y':
            self.database.drop_table(table_name)
            self._print_success(f"Table '{table_name}' deleted")
    
    def _print_menu(self) -> None:
        self._print_header("In-Memory Database Management System")
        print("\nDATA OPERATIONS:")
        print("  1. Add record (CREATE)")
        print("  2. View records (READ)")
        print("  3. Update record (UPDATE)")
        print("  4. Delete record (DELETE)")
        print("\nTABLE MANAGEMENT:")
        print("  5. Create table")
        print("  6. Delete table")
        print("  7. List tables")
        print("\n  0. Exit")
        
        tables = self.database.list_tables()
        print(f"\n[STATUS] {len(tables)} table(s)")
    
    def run(self) -> None:
        self._print_header("Welcome to In-Memory Database")
        self._print_info("Supports Memory, JSON, and CSV storage backends")
        
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
                self._create_table()
            elif choice == 6:
                self._drop_table()
            elif choice == 7:
                self._list_tables()
            elif choice == 0:
                self._print_info("Goodbye!")
                break
            else:
                self._print_error("Invalid choice")
            
            if choice != 0:
                input("\nPress Enter...")


def run() -> None:
    app = TUI()
    app.run()