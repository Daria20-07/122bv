from .backend import memory as db


def _print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + text)
    print("-" * 40)


def _print_success(message: str) -> None:
    """Print a success message."""
    print(f"OK {message}")


def _print_error(message: str) -> None:
    """Print an error message."""
    print(f"{message}")


def _print_info(message: str) -> None:
    """Print an info message."""
    print(f"{message}")


def _read_int(prompt: str, allow_empty: bool = False) -> int | None:
    while True:
        raw = input(prompt).strip()
        
        if allow_empty and raw == "":
            return None
        
        try:
            return int(raw)
        except ValueError:
            _print_error("Введите целое число")


def _read_string(prompt: str, allow_empty: bool = False) -> str | None:
    value = input(prompt).strip()
    
    if allow_empty and value == "":
        return None
    
    return value


def _select_table(action_name: str) -> str | None:
    """
    функция выбора таблицы
    """
    tables = db.list_tables()
    
    if not tables:
        _print_error("Нет доступных таблиц. Сначала создайте таблицу (пункт 5)")
        return None
    
    print(f"\nДоступные таблицы для {action_name}:")
    for i, t in enumerate(tables, 1):
        count = db.get_record_count(t)
        print(f"  {i}. {t} ({count} записей)")
    
    choice = _read_int(f"\nВыберите таблицу (1-{len(tables)}): ")
    
    if not choice or choice < 1 or choice > len(tables):
        _print_error("Неверный выбор")
        return None
    
    return tables[choice - 1]


def _print_record(record: dict) -> None:
    for key, value in record.items():
        print(f"    {key}: {value}")


def _print_records(records: list) -> None:
    if not records:
        _print_info("Записи не найдены")
        return
    
    print(f"\nНайдено записей: {len(records)}")
    for record in records:
        _print_record(record)


def _create_table() -> None:
    """функция создания новой таблицы"""
    _print_header("Создание новой таблицы")
    
    # Get table name
    while True:
        table_name = _read_string("Имя таблицы: ")
        if not table_name:
            _print_error("Имя таблицы не может быть пустым")
            continue
        
        if db.table_exists(table_name):
            _print_error(f"Таблица '{table_name}' уже существует")
            continue
        
        break
    
    # схема создания записи 
    _print_info("Определите структуру таблицы (поля и их типы)")
    _print_info("Доступные типы: str (строка), int (целое число)")
    _print_info("Для завершения добавления полей введите 'done'")
    
    schema = {}
    field_count = 0
    
    while True:
        print(f"\n--- Поле {field_count + 1} ---")
        field_name = _read_string("Имя поля: ")
        
        if not field_name:
            _print_error("Имя поля не может быть пустым")
            continue
        
        if field_name.lower() == 'done':
            if field_count == 0:
                _print_error("Добавьте хотя бы одно поле")
                continue
            break
        
        if field_name == 'id':
            _print_error("Поле 'id' создается автоматически и не может быть добавлено вручную")
            continue
        
        if field_name in schema:
            _print_error(f"Поле '{field_name}' уже добавлено")
            continue
        
        print("Тип поля:")
        print("  1. str (строка)")
        print("  2. int (целое число)")
        
        type_choice = _read_int("Выберите тип (1-2): ")
        
        if type_choice == 1:
            schema[field_name] = str
            field_count += 1
            _print_success(f"Поле '{field_name}' (строка) добавлено")
        elif type_choice == 2:
            schema[field_name] = int
            field_count += 1
            _print_success(f"Поле '{field_name}' (число) добавлено")
        else:
            _print_error("Неверный выбор. Используйте 1 или 2")
            continue
    
    try:
        db.create_table(table_name, schema)
        _print_success(f"Таблица '{table_name}' успешно создана")
        
        # Show created table structure
        print(f"\nСтруктура таблицы '{table_name}':")
        print(f"  {'Поле':<20} {'Тип':<15}")
        print(f"  {'id':<20} {'автоинкремент':<15}")
        for field, field_type in schema.items():
            type_name = "строка" if field_type == str else "число"
            print(f"  {field:<20} {type_name:<15}")
        
        _print_info("Теперь вы можете добавлять записи в эту таблицу")
    except ValueError as e:
        _print_error(str(e))


def _drop_table() -> None:
    """функция удаления таблицы"""
    tables = db.list_tables()
    
    if not tables:
        _print_error("Нет доступных таблиц для удаления")
        return
    
    _print_header("Удаление таблицы")
    
    print("Существующие таблицы:")
    for i, t in enumerate(tables, 1):
        count = db.get_record_count(t)
        print(f"  {i}. {t} ({count} записей)")
    
    choice = _read_int("\nВыберите таблицу для удаления: ")
    
    if not choice or choice < 1 or choice > len(tables):
        _print_error("Неверный выбор")
        return
    
    table_name = tables[choice - 1]
    count = db.get_record_count(table_name)
    
    print(f"\nВНИМАНИЕ: Таблица '{table_name}' содержит {count} записей")
    confirm = input(f"Удалить таблицу '{table_name}' безвозвратно? (y/N): ").strip().lower()
    
    if confirm != 'y':
        _print_info("Удаление отменено")
        return
    
    if db.drop_table(table_name):
        _print_success(f"Таблица '{table_name}' удалена")
    else:
        _print_error("Ошибка при удалении")


def _clear_table() -> None:
    """функция очистки таблицы"""
    tables = db.list_tables()
    
    if not tables:
        _print_error("Нет доступных таблиц для очистки")
        return
    
    _print_header("Очистка таблицы")
    
    print("Существующие таблицы:")
    for i, t in enumerate(tables, 1):
        count = db.get_record_count(t)
        print(f"  {i}. {t} ({count} записей)")
    
    choice = _read_int("\nВыберите таблицу для очистки: ")
    
    if not choice or choice < 1 or choice > len(tables):
        _print_error("Неверный выбор")
        return
    
    table_name = tables[choice - 1]
    count = db.get_record_count(table_name)
    
    if count == 0:
        _print_info("Таблица уже пуста")
        return
    
    confirm = input(f"\nОчистить таблицу '{table_name}' ({count} записей)? (y/N): ").strip().lower()
    
    if confirm != 'y':
        _print_info("Очистка отменена")
        return
    
    if db.clear_table(table_name):
        _print_success(f"Таблица '{table_name}' очищена. Все {count} записей удалены")
    else:
        _print_error("Ошибка при очистке")


def _list_tables() -> None:
    """функция вывода всех таблиц"""
    _print_header("Список таблиц")
    
    tables = db.list_tables()
    
    if not tables:
        _print_info("Нет созданных таблиц")
        _print_info("Используйте пункт 5 для создания таблицы")
        return
    
    print(f"\nВсего таблиц: {len(tables)}\n")
    
    for idx, table_name in enumerate(tables, 1):
        schema = db.get_table_schema(table_name)
        count = db.get_record_count(table_name)
        
        print(f"{idx}. {table_name}")
        print(f"   Записей: {count}")
        print(f"   Структура:")
        print(f"     - id (автоинкремент, уникальный)")
        for field, field_type in schema.items():
            type_name = "строка" if field_type == str else "число"
            print(f"     - {field}: {type_name}")
        print()


def _add_record() -> None:
    """Add a new record to a table."""
    table_name = _select_table("добавления записи")
    if not table_name:
        return
    
    _print_header(f"Добавление записи в таблицу '{table_name}'")
    
    schema = db.get_table_schema(table_name)
    if not schema:
        _print_error("Таблица не найдена")
        return
    
    print("\nСтруктура таблицы (поля для заполнения):")
    for field, field_type in schema.items():
        type_name = "строка" if field_type == str else "число"
        print(f"  - {field}: {type_name}")
    
    # Collect record data
    record = {}
    print("\nВведите данные:")
    
    for field, field_type in schema.items():
        while True:
            if field_type == int:
                value = _read_int(f"  {field}: ")
                if value is None:
                    continue
            else:
                value = _read_string(f"  {field}: ")
                if not value:
                    _print_error("Поле не может быть пустым")
                    continue
            
            record[field] = value
            break
    
    # Create record
    try:
        new_record = db.create_record(table_name, record)
        _print_success(f"Запись добавлена. ID = {new_record['id']}")
        print("\nДобавленная запись:")
        _print_record(new_record)
    except ValueError as e:
        _print_error(str(e))


def _read_records() -> None:
    """Read records from a table with optional filters."""
    table_name = _select_table("просмотра записей")
    if not table_name:
        return
    
    _print_header(f"Просмотр записей в таблице '{table_name}'")
    
    schema = db.get_table_schema(table_name)
    if not schema:
        _print_error("Таблица не найдена")
        return
    
    # Ask for filters
    print("\nФильтрация (Enter - пропустить поле, показать все записи):")
    filters = {}
    
    for field in schema.keys():
        field_type = schema[field]
        if field_type == int:
            value = _read_int(f"  {field}: ", allow_empty=True)
            if value is not None:
                filters[field] = value
        else:
            value = _read_string(f"  {field}: ", allow_empty=True)
            if value:
                filters[field] = value
    
    # Get records
    if filters:
        _print_info(f"Поиск по фильтрам: {filters}")
    else:
        _print_info("Показаны все записи")
    
    records = db.select_records(table_name, **filters)
    _print_records(records)


def _update_record() -> None:
    """функция изменения записи"""
    table_name = _select_table("обновления записи")
    if not table_name:
        return
    
    _print_header(f"Обновление записи в таблице '{table_name}'")
    
    schema = db.get_table_schema(table_name)
    if not schema:
        _print_error("Таблица не найдена")
        return
    
    # Get record ID
    record_id = _read_int("ID записи для обновления: ")
    if record_id is None:
        return
    
    # Find record
    records = db.select_records(table_name, id=record_id)
    
    if not records:
        _print_error(f"Запись с ID={record_id} не найдена")
        return
    
    current_record = records[0]
    _print_info("Текущие данные:")
    _print_record(current_record)
    
    # Collect updates
    updates = {}
    print("\nВведите новые значения (Enter - оставить без изменений):")
    
    for field, field_type in schema.items():
        current_value = current_record.get(field)
        
        if field_type == int:
            value = _read_int(f"  {field} [текущее: {current_value}]: ", allow_empty=True)
            if value is not None:
                updates[field] = value
        else:
            value = _read_string(f"  {field} [текущее: {current_value}]: ", allow_empty=True)
            if value:
                updates[field] = value
    
    if not updates:
        _print_info("Нет изменений")
        return
    
    # Update record
    try:
        updated = db.update_record(table_name, record_id, updates)
        if updated:
            _print_success("Запись обновлена")
            print("\nОбновленная запись:")
            _print_record(updated)
        else:
            _print_error("Запись не найдена")
    except ValueError as e:
        _print_error(str(e))


def _delete_record() -> None:
    """функция удаления записи"""
    table_name = _select_table("удаления записи")
    if not table_name:
        return
    
    _print_header(f"Удаление записи из таблицы '{table_name}'")
    
    # Get record ID
    record_id = _read_int("ID записи для удаления: ")
    if record_id is None:
        return
    
    # Check if record exists
    records = db.select_records(table_name, id=record_id)
    
    if not records:
        _print_error(f"Запись с ID={record_id} не найдена")
        return
    
    # Show record to be deleted
    _print_info("Запись, которая будет удалена:")
    _print_record(records[0])
    
    # Confirm deletion
    confirm = input(f"\nУдалить запись с ID={record_id}? (y/N): ").strip().lower()
    
    if confirm != 'y':
        _print_info("Удаление отменено")
        return
    
    # Delete record
    if db.delete_record(table_name, record_id):
        _print_success(f"Запись с ID={record_id} удалена")
    else:
        _print_error(f"Запись с ID={record_id} не найдена")


def _print_main_menu() -> None:

    print("\nОПЕРАЦИИ С ДАННЫМИ (CRUD):")
    print("  1. Добавить запись (CREATE)")
    print("  2. Просмотреть записи (READ)")
    print("  3. Обновить запись (UPDATE)")
    print("  4. Удалить запись (DELETE)")
    
    print("\nУПРАВЛЕНИЕ ТАБЛИЦАМИ:")
    print("  5. Создать таблицу")
    print("  6. Удалить таблицу")
    print("  7. Очистить таблицу")
    print("  8. Показать список таблиц")
    
    print("\nВЫХОД:")
    print("  0. Выход из программы")
    
    # Show current statistics
    tables = db.list_tables()
    print(f"\nТЕКУЩАЯ СТАТИСТИКА:")
    if not tables:
        print("  Нет созданных таблиц. Создайте таблицу (пункт 5)")
    else:
        print(f"  Всего таблиц: {len(tables)}")
        for table in tables:
            count = db.get_record_count(table)
            print(f"    - {table}: {count} записей")


def run() -> None:

    print("\nДля начала работы создайте таблицу (пункт 5 в меню)")
    
    while True:
        _print_main_menu()
        
        choice = _read_int("\nВыберите действие: ")
        
        # CRUD Operations
        if choice == 1:
            _add_record()
        elif choice == 2:
            _read_records()
        elif choice == 3:
            _update_record()
        elif choice == 4:
            _delete_record()
        # Table Management
        elif choice == 5:
            _create_table()
        elif choice == 6:
            _drop_table()
        elif choice == 7:
            _clear_table()
        elif choice == 8:
            _list_tables()
        # Exit
        elif choice == 0:
            _print_info("До свидания!")
            break
        else:
            _print_error("Неизвестная команда. Используйте 0-8")
        
        if choice != 0:
            input("\nНажмите Enter для продолжения...")