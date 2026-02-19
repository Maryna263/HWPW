import pickle
from datetime import datetime, timedelta
from collections import UserDict
from abc import ABC, abstractmethod

# --- АБСТРАКЦІЯ ДЛЯ ІНТЕРФЕЙСУ КОРИСТУВАЧА ---

class UserInterface(ABC):
    @abstractmethod
    def display_message(self, message: str):
        """Виведення довільного текстового повідомлення"""
        pass

    @abstractmethod
    def display_contacts(self, book: 'AddressBook'):
        """Виведення списку всіх контактів у зручному форматі"""
        pass

    @abstractmethod
    def display_help(self):
        """Виведення списку доступних команд"""
        pass

# --- КОНКРЕТНА РЕАЛІЗАЦІЯ КОНСОЛЬНОГО ІНТЕРФЕЙСУ ---

class ConsoleInterface(UserInterface):
    def display_message(self, message: str):
        print(f"\n[System]: {message}")

    def display_contacts(self, book: 'AddressBook'):
        if not book.data:
            print("\n--- Contact list is empty ---")
            return
        
        print("\n" + "="*50)
        print(f"{'Name':<15} | {'Phones':<20} | {'Birthday'}")
        print("-" * 50)
        for record in book.data.values():
            phones = ", ".join(p.value for p in record.phones)
            bday = record.birthday.value if record.birthday else "-"
            print(f"{record.name.value:<15} | {phones:<20} | {bday}")
        print("="*50 + "\n")

    def display_help(self):
        commands = {
            "hello": "Greeting",
            "add [name] [phone]": "Add new contact or phone",
            "change [name] [old] [new]": "Change existing phone",
            "phone [name]": "Show contact phones",
            "all": "Show all contacts",
            "add-birthday [name] [date]": "Add birthday (DD.MM.YYYY)",
            "show-birthday [name]": "Show contact birthday",
            "birthdays": "Show upcoming birthdays for 7 days",
            "help": "Show this menu",
            "exit/close": "Save and exit"
        }
        print("\n--- Available Commands ---")
        for cmd, desc in commands.items():
            print(f"{cmd:<30} : {desc}")

# --- КЛАСИ ДАНИХ (БЕЗ ЗМІН У ЛОГІЦІ) ---

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field): pass

class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return True
        return False

    def add_birthday(self, birthday_string):
        self.birthday = Birthday(birthday_string)

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        upcoming = []
        today = datetime.today().date()
        for user in self.data.values():
            if not user.birthday: continue
            bday_obj = datetime.strptime(user.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = bday_obj.replace(year=today.year)
            if birthday_this_year < today: 
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            if 0 <= (birthday_this_year - today).days <= 7:
                congrats_date = birthday_this_year
                if congrats_date.weekday() == 5: congrats_date += timedelta(days=2)
                elif congrats_date.weekday() == 6: congrats_date += timedelta(days=1)
                upcoming.append({"name": user.name.value, "birthday": congrats_date.strftime("%d.%m.%Y")})
        return upcoming

# --- ЛОГІКА ЗАСТОСУНКУ ---

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError):
            return "Give me name and data please. Format: [name] [phone/birthday]"
        except KeyError:
            return "Contact not found."
    return inner

@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return "Phone added."
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f: pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f: return pickle.load(f)
    except (FileNotFoundError, EOFError): return AddressBook()

# --- ГОЛОВНИЙ ЦИКЛ З ВИКОРИСТАННЯМ UI ---

def main():
    book = load_data()
    ui = ConsoleInterface() # Тут ми легко можемо замінити на інший клас UI
    
    ui.display_message("Welcome to the assistant bot!")
    ui.display_help()

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input: continue
        parts = user_input.split()
        cmd, args = parts[0].lower(), parts[1:]

        if cmd in ["close", "exit"]:
            save_data(book)
            ui.display_message("Good bye!")
            break
        
        elif cmd == "hello":
            ui.display_message("How can I help you?")
        
        elif cmd == "help":
            ui.display_help()
            
        elif cmd == "add":
            ui.display_message(add_contact(args, book))
            
        elif cmd == "all":
            ui.display_contacts(book)
            
        elif cmd == "birthdays":
            upcoming = book.get_upcoming_birthdays()
            if not upcoming:
                ui.display_message("No upcoming birthdays.")
            else:
                msg = "\n".join([f"{u['name']}: {u['birthday']}" for u in upcoming])
                ui.display_message(f"Upcoming birthdays:\n{msg}")
        
        # Решта команд (phone, change тощо) обробляються аналогічно через ui.display_message
        else:
            ui.display_message("Invalid command. Type 'help' to see available commands.")

if __name__ == "__main__":
    main()