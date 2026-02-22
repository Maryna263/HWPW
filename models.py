import random
from faker import Faker
from sqlalchemy import create_engine, ForeignKey, String, Integer, Date, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

# 1. Налаштування підключення до Docker Postgres
DATABASE_URL = "postgresql+psycopg2://postgres:mysecretpassword@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker('uk_UA')

class Base(DeclarativeBase): pass

# --- МОДЕЛІ ---
class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    students: Mapped[list["Student"]] = relationship(back_populates="group")

class Teacher(Base):
    __tablename__ = "teachers"
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(150))
    subjects: Mapped[list["Subject"]] = relationship(back_populates="teacher")

class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id", ondelete="CASCADE"))
    teacher: Mapped["Teacher"] = relationship(back_populates="subjects")

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(150))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    group: Mapped["Group"] = relationship(back_populates="students")

class Grade(Base):
    __tablename__ = "grades"
    id: Mapped[int] = mapped_column(primary_key=True)
    grade: Mapped[int] = mapped_column(Integer)
    date_received: Mapped[Date] = mapped_column(Date)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"))

# --- ЗАПОВНЕННЯ ---
def fill_data():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Групи
    groups = [Group(name=n) for n in ['Група А', 'Група Б', 'Група В']]
    session.add_all(groups)
    
    # Викладачі
    teachers = [Teacher(fullname=fake.name()) for _ in range(5)]
    session.add_all(teachers)
    session.commit()

    # Предмети
    subjects_names = ['Математика', 'Фізика', 'Програмування', 'Історія', 'Хімія', 'Алгоритми', 'Бази даних', 'English']
    subjects = [Subject(name=name, teacher_id=random.randint(1, 5)) for name in subjects_names]
    session.add_all(subjects)
    
    # Студенти
    students = [Student(fullname=fake.name(), group_id=random.randint(1, 3)) for _ in range(40)]
    session.add_all(students)
    session.commit()

    # Оцінки
    for s_id in range(1, 41):
        for _ in range(15):
            g = Grade(
                student_id=s_id,
                subject_id=random.randint(1, 8),
                grade=random.randint(50, 100),
                date_received=fake.date_between(start_date='-1y', end_date='today')
            )
            session.add(g)
    
    session.commit()
    print("Базу даних у Docker успішно заповнено!")

if __name__ == "__main__":
    fill_data()