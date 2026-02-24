from mongoengine import Document, StringField, BooleanField, DateTimeField, ListField
from datetime import datetime

class Contact(Document):
    # Обов'язкові поля згідно з ТЗ
    full_name = StringField(required=True, max_length=120)
    email = StringField(required=True, unique=True)
    is_sent = BooleanField(default=False) # Значення False за замовчуванням
    additional_info = StringField() 
    
    # Додаткові поля для інформаційного навантаження
    phone = StringField(max_length=20)
    created_at = DateTimeField(default=datetime.now)
    tags = ListField(StringField(max_length=30))  # Категорії інтересів (наприклад, ["news", "promo"])
    meta = {'collection': 'contacts'} # Назва колекції в MongoDB

    def __str__(self):
        return f"{self.full_name} <{self.email}>"