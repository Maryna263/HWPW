import sys
from mongoengine import connect
from models import Author, Quote

# Используйте ваш рабочий URI из upload.py
URI = "mongodb+srv://29072025pmv_db_user:bZuhdb6b0rvANCAq@cluster0.ozprlhm.mongodb.net/hw_8?appName=Cluster0"

def search_quotes():
    try:
        connect(host=URI)
        # Отладка: проверим, есть ли данные в базе
        print(f"--- Статистика БД: Авторов: {Author.objects.count()}, Цитат: {Quote.objects.count()} ---")
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return

    while True:
        user_input = input("Введіть команду (напр. name: Steve Martin): ").strip()
        
        if user_input.lower() == 'exit':
            break

        if ':' not in user_input:
            print("Невірний формат. Використовуйте 'команда: значення'")
            continue

        command, value = user_input.split(':', 1)
        command = command.strip().lower()
        value = value.strip()

        results = []

        if command == 'name':
            # Используем __icontains для поиска части имени без учета регистра
            author = Author.objects(fullname__icontains=value).first()
            if author:
                results = Quote.objects(author=author)
            else:
                print(f"Автора '{value}' не знайдено в базі.")

        elif command == 'tag':
            # Поиск цитат, где в списке тегов есть искомый (без учета регистра)
            results = Quote.objects(tags__icontains=value)
            
        elif command == 'tags':
            # Поиск по списку тегов через запятую
            tags_list = [t.strip() for t in value.split(',')]
            results = Quote.objects(tags__in=tags_list)

        if results:
            for q in results:
                # Вывод в UTF-8
                print(f"{q.quote}".encode('utf-8').decode('utf-8'))
        elif command in ['name', 'tag', 'tags']:
            print("Нічого не знайдено за цим запитом.")

if __name__ == "__main__":
    search_quotes()