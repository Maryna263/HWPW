import os
import django
from pymongo import MongoClient

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hw_quotes.settings')
django.setup()

from quotes.models import Author, Quote, Tag

client = MongoClient("mongodb+srv://29072025pmv_db_user:bZuhdb6b0rvANCAq@cluster0.ozprlhm.mongodb.net/?retryWrites=true&w=majority")
db = client.hw_8 

def migrate_data():
    # 1. Перенесення Авторів
    print("Крок 1: Міграція авторів...")
    authors_mongo = db.authors.find()
    author_map = {} # Карта для зв'язку ID Mongo з об'єктом Django

    for a in authors_mongo:
        django_author, created = Author.objects.get_or_create(
            fullname=a['fullname'],
            defaults={
                'born_date': a.get('born_date', ''),
                'born_location': a.get('born_location', ''),
                'description': a.get('description', '')
            }
        )
        # Запам'ятовуємо ID з Mongo, щоб знайти автора для цитат
        author_map[str(a['_id'])] = django_author
    
    print(f"Авторів у базі: {Author.objects.count()}")

    # 2. Перенесення Цитат
    print("Крок 2: Міграція цитат...")
    quotes_mongo = db.quotes.find()
    for q in quotes_mongo:
        # Отримуємо ID автора з цитати та шукаємо його в нашій карті
        mongo_author_id = str(q.get('author'))
        django_author = author_map.get(mongo_author_id)

        if django_author:
            quote_obj, created = Quote.objects.get_or_create(
                quote=q.get('quote'),
                author=django_author
            )

            # Перенесення тегів
            tags = q.get('tags', [])
            for tag_name in tags:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                quote_obj.tags.add(tag_obj)
            
    print(f"Цитат у базі Django: {Quote.objects.count()}")
    print("Готово! Тепер можна запускати сервер.")

if __name__ == '__main__':
    migrate_data()