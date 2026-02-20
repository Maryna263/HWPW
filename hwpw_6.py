import sqlite3
import random
import os
import sys
from faker import Faker

# Визначаємо шлях до папки, де лежить цей скрипт
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, 'university.db')

fake = Faker('uk_UA')

def create_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.executescript('''
            DROP TABLE IF EXISTS grades; DROP TABLE IF EXISTS students;
            DROP TABLE IF EXISTS subjects; DROP TABLE IF EXISTS teachers; DROP TABLE IF EXISTS groups;
            CREATE TABLE groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);
            CREATE TABLE teachers (id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT);
            CREATE TABLE subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, teacher_id INTEGER, FOREIGN KEY(teacher_id) REFERENCES teachers(id));
            CREATE TABLE students (id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT, group_id INTEGER, FOREIGN KEY(group_id) REFERENCES groups(id));
            CREATE TABLE grades (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, subject_id INTEGER, grade INTEGER, date_received DATE, FOREIGN KEY(student_id) REFERENCES students(id), FOREIGN KEY(subject_id) REFERENCES subjects(id));
        ''')
        # Наповнення
        cur.executemany("INSERT INTO groups (name) VALUES (?)", [('Група А',), ('Група Б',), ('Група В',)])
        for _ in range(5): cur.execute("INSERT INTO teachers (fullname) VALUES (?)", (fake.name(),))
        subjects = ['Математика', 'Фізика', 'Програмування', 'Історія', 'Хімія', 'Алгоритми', 'Бази даних', 'English']
        for sub in subjects: cur.execute("INSERT INTO subjects (name, teacher_id) VALUES (?, ?)", (sub, random.randint(1, 5)))
        for _ in range(40): cur.execute("INSERT INTO students (fullname, group_id) VALUES (?, ?)", (fake.name(), random.randint(1, 3)))
        for s_id in range(1, 41):
            for _ in range(15):
                cur.execute("INSERT INTO grades (student_id, subject_id, grade, date_received) VALUES (?, ?, ?, ?)",
                           (s_id, random.randint(1, 8), random.randint(50, 100), fake.date_between(start_date='-1y', end_date='today')))
        conn.commit()

def generate_sql_files():
    queries = {
        "1": "SELECT s.fullname, ROUND(AVG(g.grade), 2) as avg_g FROM students s JOIN grades g ON s.id = g.student_id GROUP BY s.id ORDER BY avg_g DESC LIMIT 5;",
        "2": "SELECT s.fullname, ROUND(AVG(g.grade), 2) as avg_g FROM students s JOIN grades g ON s.id = g.student_id WHERE g.subject_id = 1 GROUP BY s.id ORDER BY avg_g DESC LIMIT 1;",
        "3": "SELECT gr.name, ROUND(AVG(g.grade), 2) FROM groups gr JOIN students s ON gr.id = s.group_id JOIN grades g ON s.id = g.student_id WHERE g.subject_id = 1 GROUP BY gr.id;",
        "4": "SELECT ROUND(AVG(grade), 2) FROM grades;",
        "5": "SELECT name FROM subjects WHERE teacher_id = 1;",
        "6": "SELECT fullname FROM students WHERE group_id = 1;",
        "7": "SELECT s.fullname, g.grade FROM students s JOIN grades g ON s.id = g.student_id WHERE s.group_id = 1 AND g.subject_id = 1;",
        "8": "SELECT t.fullname, ROUND(AVG(g.grade), 2) FROM teachers t JOIN subjects s ON t.id = s.teacher_id JOIN grades g ON s.id = g.subject_id WHERE t.id = 1 GROUP BY t.id;",
        "9": "SELECT DISTINCT s.name FROM subjects s JOIN grades g ON s.id = g.subject_id WHERE g.student_id = 1;",
        "10": "SELECT DISTINCT s.name FROM subjects s JOIN grades g ON s.id = g.subject_id WHERE g.student_id = 1 AND s.teacher_id = 2;"
    }
    
    for num, sql_text in queries.items():
        # Створюємо шлях саме в папці HW
        file_path = os.path.join(CURRENT_DIR, f"query_{num}.sql")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(sql_text)
    
    print(f"\nГотово! Перевірте папку: {CURRENT_DIR}")
    print(f"Там мають бути файли query_1.sql ... query_10.sql та university.db")

if __name__ == "__main__":
    create_db()
    generate_sql_files()