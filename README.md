# In-Memory Database Management System (File Storage Version)

## Структура проекта
PIOA-122bv/
├── src/
│ └── db/
│ ├── backend/
│ │ ├── init.py
│ │ ├── errors.py # Пользовательские исключения
│ │ ├── database.py # Абстрактный интерфейс Database
│ │ ├── table.py # Класс Table с индексами
│ │ ├── memory.py # In-memory реализация
│ │ ├── file.py # JSON файловая реализация
│ │ └── csvdb.py # CSV файловая реализация (бонус)
│ ├── init.py
│ ├── main.py # Точка входа
│ └── tui.py # Пользовательский интерфейс
├── tests/
│ ├── init.py
│ ├── test_memory.py
│ ├── test_table.py
│ ├── test_file_database.py
│ └── test_csv_database.py
├── .gitignore
└── README.md

## Сравнение реализаций

| Характеристика | MemoryDatabase | FileDatabase (JSON) | CSVDatabase |
|----------------|----------------|---------------------|-------------|
| Скорость | Высокая | Средняя | Средняя |
| Персистентность | Нет | Да | Да |
| Читаемость | - | Высокая | Высокая (Excel) |
| Индексы | Да | Да | Да |

## Инструкция по запуску

```powershell
cd C:\Users\Honor\122bv
git checkout task4
py -m src.db