from sqlalchemy import func, desc, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tabulate import tabulate
from models import Student, Group, Teacher, Subject, Grade

# Налаштування підключення
DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# --- ФУНКЦІЇ ВИБІРКИ ---

def select_1():
    """5 студентів із найбільшим середнім балом з усіх предметів."""
    return session.query(Student.fullname, func.round(func.avg(Grade.grade), 2).label('avg_grade')) \
        .select_from(Grade).join(Student) \
        .group_by(Student.id).order_by(desc('avg_grade')).limit(5).all()

def select_2(subject_id=1):
    """Студент із найвищим середнім балом з певного предмета."""
    return session.query(Student.fullname, func.round(func.avg(Grade.grade), 2).label('avg_grade')) \
        .select_from(Grade).join(Student).filter(Grade.subject_id == subject_id) \
        .group_by(Student.id).order_by(desc('avg_grade')).limit(1).all()

def select_3(subject_id=1):
    """Середній бал у групах з певного предмета."""
    return session.query(Group.name, func.round(func.avg(Grade.grade), 2).label('avg_grade')) \
        .select_from(Grade).join(Student).join(Group).filter(Grade.subject_id == subject_id) \
        .group_by(Group.id).all()

def select_4():
    """Середній бал на потоці (по всій таблиці оцінок)."""
    res = session.query(func.round(func.avg(Grade.grade), 2)).scalar()
    return [[res]] # Повертаємо список для tabulate

def select_5(teacher_id=1):
    """Які курси читає певний викладач."""
    return session.query(Subject.name).filter(Subject.teacher_id == teacher_id).all()

def select_6(group_id=1):
    """Список студентів у певній групі."""
    return session.query(Student.fullname).filter(Student.group_id == group_id).all()

def select_7(group_id=1, subject_id=1):
    """Оцінки студентів у окремій групі з певного предмета."""
    return session.query(Student.fullname, Grade.grade) \
        .select_from(Grade).join(Student) \
        .filter(Student.group_id == group_id, Grade.subject_id == subject_id).all()

def select_8(teacher_id=1):
    """Середній бал, який ставить певний викладач зі своїх предметів."""
    res = session.query(func.round(func.avg(Grade.grade), 2)) \
        .select_from(Grade).join(Subject).filter(Subject.teacher_id == teacher_id).scalar()
    return [[res]]

def select_9(student_id=1):
    """Список курсів, які відвідує певний студент."""
    return session.query(Subject.name).select_from(Grade).join(Subject) \
        .filter(Grade.student_id == student_id).distinct().all()

def select_10(student_id=1, teacher_id=1):
    """Список курсів, які певному студенту читає певний викладач."""
    return session.query(Subject.name).select_from(Grade).join(Subject) \
        .filter(Grade.student_id == student_id, Subject.teacher_id == teacher_id).distinct().all()

# --- БЛОК ВИВЕДЕННЯ ---

if __name__ == "__main__":
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТИ ЗАПИТІВ (SQLAlchemy)")
    print("="*50)

    print("\n1. Топ-5 студентів за середнім балом:")
    print(tabulate(select_1(), headers=["Студент", "Сер. бал"], tablefmt="fancy_grid"))

    print("\n2. Найкращий студент з предмета №1:")
    print(tabulate(select_2(1), headers=["Студент", "Сер. бал"], tablefmt="fancy_grid"))

    print("\n3. Середній бал у групах з предмета №1:")
    print(tabulate(select_3(1), headers=["Група", "Сер. бал"], tablefmt="fancy_grid"))

    print("\n4. Середній бал по всьому потоку:")
    print(tabulate(select_4(), headers=["Загальний сер. бал"], tablefmt="fancy_grid"))

    print("\n5. Курси викладача №1:")
    print(tabulate(select_5(1), headers=["Назва курсу"], tablefmt="fancy_grid"))

    print("\n6. Студенти групи №1:")
    print(tabulate(select_6(1), headers=["ПІБ Студента"], tablefmt="fancy_grid"))

    print("\n7. Оцінки групи №1 з предмета №1:")
    print(tabulate(select_7(1, 1), headers=["Студент", "Оцінка"], tablefmt="fancy_grid"))

    print("\n8. Сер. бал викладача №1 з його предметів:")
    print(tabulate(select_8(1), headers=["Сер. бал"], tablefmt="fancy_grid"))

    print("\n9. Курси, які відвідує студент №1:")
    print(tabulate(select_9(1), headers=["Назва курсу"], tablefmt="fancy_grid"))

    print("\n10. Курси студента №1 від викладача №1:")
    print(tabulate(select_10(1, 1), headers=["Назва курсу"], tablefmt="fancy_grid"))

    session.close()