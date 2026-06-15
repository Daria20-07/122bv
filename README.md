# In-Memory Database Management System (File Storage Version)

## Структура проекта
```text
PIOA-122bv/
├── src/
│ └── db/
│ ├── backend/
│ │ ├── init.py
│ │ ├── errors.py
│ │ ├── database.py
│ │ ├── table.py
│ │ ├── memory.py
│ │ ├── file.py
│ │ └── csvdb.py
│ ├── init.py
│ ├── main.py
│ └── tui.py
├── tests/
│ ├── init.py
│ ├── test_memory.py
│ ├── test_table.py
│ ├── test_file_database.py
│ └── test_csv_database.py
├── .gitignore
└── README.md
```

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
