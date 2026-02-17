import os
import shutil
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def copy_file(file_path: Path, target_base_dir: Path):
    """Копіює файл у відповідну піддиректорію на основі його розширення."""
    try:
        # Отримуємо розширення файлу (без крапки)
        ext = file_path.suffix[1:].lower() if file_path.suffix else "no_extension"
        
        # Створюємо цільову папку
        target_dir = target_base_dir / ext
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Копіюємо файл
        shutil.copy2(file_path, target_dir / file_path.name)
    except Exception as e:
        print(f"Помилка при копіюванні {file_path}: {e}")

def process_directory(source_dir: Path, target_dir: Path, executor: ThreadPoolExecutor):
    """Рекурсивно обходить директорії та передає файли на копіювання в пул потоків."""
    try:
        for item in source_dir.iterdir():
            if item.is_dir():
                # Якщо це директорія, запускаємо її обробку як окреме завдання в пулі
                executor.submit(process_directory, item, target_dir, executor)
            elif item.is_file():
                # Якщо це файл, відправляємо його на копіювання
                executor.submit(copy_file, item, target_dir)
    except PermissionError:
        print(f"Немає доступу до директорії: {source_dir}")
    except Exception as e:
        print(f"Помилка при обробці директорії {source_dir}: {e}")

def main():
    # Налаштування аргументів командного рядка
    parser = argparse.ArgumentParser(description="Сортування файлів за розширенням (багатопотоковість)")
    parser.add_argument("source", type=str, help="Шлях до вихідної директорії")
    parser.add_argument("target", type=str, nargs="?", default="dist", help="Шлях до цільової директорії (за замовчуванням dist)")
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    target_path = Path(args.target)

    if not source_path.exists() or not source_path.is_dir():
        print(f"Помилка: Вихідна директорія '{source_path}' не існує.")
        return

    print(f"Починаємо обробку: {source_path} -> {target_path}")

    # Використовуємо ThreadPoolExecutor для паралельного виконання
    with ThreadPoolExecutor() as executor:
        process_directory(source_path, target_path, executor)

    print("Обробка завершена.")

if __name__ == "__main__":
    main()