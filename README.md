# In-Memory Database (OOP Version)

## Описание

Object-oriented in-memory database with full CRUD operations, sorting, and 90%+ test coverage.

## Структура проекта
122bv/
├── src/db/
│ ├── backend/
│ │ ├── errors.py # Custom exceptions
│ │ └── memory.py # Database and Table classes
│ ├── main.py # Entry point
│ └── tui.py # OOP UI
├── tests/
│ └── test_memory.py # Unit tests
└── README.md

## Особенности

- CREATE, READ, UPDATE, DELETE operations
- Sort records by any field (ascending/descending)
- Multiple tables with dynamic schemas
- Type validation (str, int)
- Custom exceptions
- 90%+ test coverage

## Быстрый запуск

```bash
cd C:\Users\Honor\122bv
py -m src.db
py -m unittest tests.test_memory -v
1. Add record (CREATE)
2. View records (READ)
3. Update record (UPDATE)
4. Delete record (DELETE)
5. Sort records (SORT)
6. Create table
7. Delete table
8. Clear table
9. List tables
0. Exit

### 10. Запустить тесты и проверить

```powershell
# Убедиться, что находимся в корне проекта
cd C:\Users\Honor\122bv

# Запустить тесты
py -m unittest tests.test_memory -v

# Если есть ошибки импорта, создать __init__.py
New-Item -Path tests\__init__.py -ItemType File -Force
