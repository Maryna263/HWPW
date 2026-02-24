import json
from mongoengine import connect
from models import Author, Quote

# Замініть <connection_string> на ваш рядок підключення з MongoDB Atlas
connect(host="mongodb+srv://29072025pmv_db_user:bZuhdb6b0rvANCAq@cluster0.ozprlhm.mongodb.net/hw_8?appName=Cluster0")

def load_data():
    # Завантаження авторів
    with open('authors.json', 'r', encoding='utf-8') as f:
        authors_data = json.load(f)
        for data in authors_data:
            # Оновлюємо існуючого автора або створюємо нового (upsert)
            Author.objects(fullname=data['fullname']).update_one(upsert=True, **data)
    print("Автори завантажені або оновлені.")

    # Завантаження цитат
    with open('quotes.json', 'r', encoding='utf-8') as f:
        quotes_data = json.load(f)
        for data in quotes_data:
            author_name = data.get('author')
            author = Author.objects(fullname=author_name).first()
            if author:
                # Перевіряємо, чи така цитата вже є, щоб не дублювати
                if not Quote.objects(quote=data.get('quote'), author=author):
                    Quote(author=author, tags=data.get('tags'), quote=data.get('quote')).save()
    print("Цитати завантажені.")
    
if __name__ == "__main__":
    load_data()
    print("Дані успішно завантажені!")