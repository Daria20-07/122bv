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
py -m src.db
py -m unittest tests.test_memory -v
