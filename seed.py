import random
from datetime import datetime
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Імпортуємо ваші моделі з файлу models.py
from models import Student, Group, Teacher, Subject, Grade

# Налаштування підключення до вашого Docker Postgres
DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

fake = Faker('uk_UA')

def seed_db():
    try:
        # 1. Створюємо 3 групи
        groups = [Group(name=f"Група {n}") for n in ['A', 'B', 'C']]
        session.add_all(groups)
        session.commit()

        # 2. Створюємо 3-5 викладачів
        teachers = [Teacher(fullname=fake.name()) for _ in range(random.randint(3, 5))]
        session.add_all(teachers)
        session.commit()

        # 3. Створюємо 5-8 предметів (випадково призначаємо викладача)
        subject_names = ['Математика', 'Фізика', 'Програмування', 'Історія', 'Хімія', 'Алгоритми', 'English', 'Logic']
        subjects = []
        for i in range(random.randint(5, 8)):
            sub = Subject(
                name=subject_names[i], 
                teacher_id=random.choice(teachers).id
            )
            subjects.append(sub)
        session.add_all(subjects)
        session.commit()

        # 4. Створюємо 30-50 студентів (випадково призначаємо групу)
        students = []
        for _ in range(random.randint(30, 50)):
            student = Student(
                fullname=fake.name(), 
                group_id=random.choice(groups).id
            )
            students.append(student)
        session.add_all(students)
        session.commit()

        # 5. Створюємо до 20 оцінок для кожного студента
        for student in students:
            for _ in range(random.randint(10, 20)):
                grade = Grade(
                    student_id=student.id,
                    subject_id=random.choice(subjects).id,
                    grade=random.randint(50, 100),
                    date_received=fake.date_between(start_date='-1y', end_date='today')
                )
                session.add(grade)
        
        session.commit()
        print("✅ Базу даних успішно заповнено випадковими даними!")

    except Exception as e:
        session.rollback()
        print(f"❌ Виникла помилка: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_db()